# ABOUTME: Base renderer class for markdown section generation
# ABOUTME: Provides common interface for all section renderers

from abc import ABC, abstractmethod
from typing import Any


class BaseRenderer(ABC):
    """Abstract base class for all markdown renderers."""

    @abstractmethod
    def render(self, data: Any) -> str:
        """Render data to markdown string."""
        pass
