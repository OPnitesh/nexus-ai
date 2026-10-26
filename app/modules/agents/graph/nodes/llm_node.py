
import hashlib
import json
import logging

from langchain_core.messages import AIMessage, message_to_dict
from langchain_core.runnables import RunnableConfig

from app.core.db.session import AsyncSessionLocal
from app.core.redis.cache import RedisCache
from app.core.redis.client import redis_client
from app.modules.agents.embeddings import embeddings
from app.modules.agents.graph.state import ChatState
from app.modules.agents.llm import llm
from app.modules.agents.semantic_cache_repository import SemanticCacheRepository

logger = logging.getLogger(__name__)

REDIS_CACHE_TTL = 300
SEMANTIC_CACHE_MAX_DISTANCE = 0.15


def _build_context_hash(context: dict) -> str:
    serialized_context = json.dumps(
        context,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(serialized_context.encode("utf-8")).hexdigest()


# Checks exact and context-compatible semantic caches before calling Gemini.
async def llm_node(
    state: ChatState,
    config: RunnableConfig,
) -> dict:
    messages = state["messages"]
    model_name = llm.model

    if not messages:
        return {"messages": [AIMessage(content="Please provide a message.")]}

    cache = RedisCache(redis_client)
    payload = {
        "model": model_name,
        "messages": [message_to_dict(message) for message in messages],
    }

    cache_key = cache.build_key(payload)
    cached_response = None

    try:
        cached_response = await cache.get(cache_key)
    except Exception:
        logger.exception("REDIS_CACHE_LOOKUP_FAILED")

    if cached_response is not None:
        logger.info("REDIS_CACHE_HIT model=%s", model_name)
        return {"messages": [AIMessage.model_validate_json(cached_response)]}

    logger.info("REDIS_CACHE_MISS model=%s", model_name)

    if not isinstance(messages[-1].content, str):
        logger.info("GEMINI_GENERATION reason=unsupported_message_content")
        response = await llm.ainvoke(messages)
        return {"messages": [response]}

    question = messages[-1].content.strip()

    if not question:
        logger.info("GEMINI_GENERATION reason=empty_question")
        response = await llm.ainvoke(messages)
        return {"messages": [response]}

    prior_messages = [
        message_to_dict(message)
        for message in messages[:-1]
    ]

    if prior_messages:
        thread_id = config.get("configurable", {}).get("thread_id", "")
        context_payload = {
            "scope": "conversation",
            "thread_id": thread_id,
            "prior_messages": prior_messages,
        }
        logger.info("SEMANTIC_CACHE_SCOPE scope=conversation")
    else:
        context_payload = {"scope": "general"}
        logger.info("SEMANTIC_CACHE_SCOPE scope=general")

    context_hash = _build_context_hash(context_payload)
    question_embedding = None
    semantic_entry = None

    try:
        question_embedding = await embeddings.aembed_query(question)

        async with AsyncSessionLocal() as session:
            repository = SemanticCacheRepository(session)
            semantic_entry = await repository.find_similar(
                embedding=question_embedding,
                model_name=model_name,
                context_hash=context_hash,
                max_distance=SEMANTIC_CACHE_MAX_DISTANCE,
            )

    except Exception:
        logger.exception("SEMANTIC_CACHE_LOOKUP_FAILED")

    if semantic_entry is not None:
        logger.info("SEMANTIC_CACHE_HIT model=%s", model_name)
        response = AIMessage(content=semantic_entry.response)

        try:
            await cache.set(
                key=cache_key,
                value=response.model_dump_json(),
                ttl=REDIS_CACHE_TTL,
            )
        except Exception:
            logger.exception("REDIS_CACHE_SAVE_FAILED")

        return {"messages": [response]}

    logger.info("SEMANTIC_CACHE_MISS model=%s", model_name)
    logger.info("GEMINI_GENERATION model=%s", model_name)

    response = await llm.ainvoke(messages)

    try:
        await cache.set(
            key=cache_key,
            value=response.model_dump_json(),
            ttl=REDIS_CACHE_TTL,
        )
    except Exception:
        logger.exception("REDIS_CACHE_SAVE_FAILED")

    if question_embedding is not None and isinstance(response.content, str):
        try:
            async with AsyncSessionLocal() as session:
                repository = SemanticCacheRepository(session)
                await repository.save(
                    question=question,
                    embedding=question_embedding,
                    response=response.content,
                    model_name=model_name,
                    context_hash=context_hash,
                )
                await session.commit()

            logger.info("SEMANTIC_CACHE_SAVE model=%s", model_name)

        except Exception:
            logger.exception("SEMANTIC_CACHE_SAVE_FAILED")

    return {"messages": [response]}