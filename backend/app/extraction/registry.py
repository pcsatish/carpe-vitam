"""Extractor registry for auto-discovery."""

from typing import Type
from .base import BaseExtractor


class ExtractorRegistry:
    """Registry of available extractors."""

    _extractors: list[Type[BaseExtractor]] = []

    @classmethod
    def register(cls, extractor_class: Type[BaseExtractor]) -> Type[BaseExtractor]:
        """
        Decorator to register an extractor.

        Usage:
            @ExtractorRegistry.register
            class MyExtractor(BaseExtractor):
                ...
        """
        cls._extractors.append(extractor_class)
        # Sort by priority (lower = first)
        cls._extractors.sort(key=lambda e: e.priority)
        return extractor_class

    @classmethod
    def get_extractor(cls, file_path: str, text_sample: str) -> Type[BaseExtractor] | None:
        """
        Get the appropriate extractor for the given file.

        Returns:
            Extractor class if found, None otherwise
        """
        for extractor_class in cls._extractors:
            if extractor_class.can_handle(file_path, text_sample):
                return extractor_class
        return None

    @classmethod
    def get_all_extractors(cls) -> list[Type[BaseExtractor]]:
        """Get all registered extractors."""
        return cls._extractors
