"""
Repositories package for data access layer.

This package contains all data access repositories that handle
database and file system operations.
"""

from .flashcard_repository import FlashcardRepository

__all__ = ["FlashcardRepository"]
