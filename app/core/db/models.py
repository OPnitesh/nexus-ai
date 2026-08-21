"""
Import all SQLAlchemy models here.

This ensures SQLAlchemy registers every model
with Base.metadata.
"""

from app.modules.users.model import User

__all__ = ["User"]