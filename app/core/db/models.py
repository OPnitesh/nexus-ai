"""
Import SQLAlchemy models here so they register with Base.metadata.
"""
from app.modules.agents.semantic_cache_model import SemanticCacheEntry

__all__ = ["SemanticCacheEntry"]
