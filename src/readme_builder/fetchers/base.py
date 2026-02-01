# ABOUTME: Base fetcher class for all data sources
# ABOUTME: Provides common interface, error handling, and logging

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class BaseFetcher(ABC):
    """Abstract base class for all fetchers."""

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def fetch(self) -> Any:
        """Fetch data from the source. Returns appropriate default on failure."""
        pass

    def safe_fetch(self) -> Any:
        """Fetch with error handling. Returns default value on failure."""
        try:
            return self.fetch()
        except Exception as e:
            self.logger.error(f"Fetch failed: {e}")
            return self.default_value()

    @abstractmethod
    def default_value(self) -> Any:
        """Return the default value when fetch fails."""
        pass
