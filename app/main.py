from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.core.db.engine import engine
from app.modules.agents.router import router as agents_router
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.core.redis.client import redis_client
from app.modules.agents.graph.checkpointer import create_checkpointer
from app.core.logging.logger import setup_logging


# Manages application-wide infrastructure resources during startup and shutdown.s
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Nexus AI...")

    try:
        async with engine.begin() as connection:
            await connection.execute(text("SELECT 1"))

        print("Database Connected")

        await redis_client.ping()
        print("Redis Connected")

        async with create_checkpointer() as checkpointer:
            app.state.checkpointer = checkpointer

            print("LangGraph Checkpointer Connected")

            yield

    finally:
        await redis_client.aclose()
        await engine.dispose()

        print("Shutting down Nexus AI...")

setup_logging()
app = FastAPI(
    title="Nexus AI",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(agents_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Nexus AI"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
