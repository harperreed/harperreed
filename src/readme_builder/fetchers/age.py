# ABOUTME: Age endpoint fetcher for dynamic age display
# ABOUTME: Calls Harper's age API and returns current age as float

import httpx

from .base import BaseFetcher


class AgeFetcher(BaseFetcher):
    """Fetches current age from the age API endpoint."""

    def __init__(self, endpoint: str, timeout: float = 10.0):
        super().__init__(timeout)
        self.endpoint = endpoint

    def fetch(self) -> float:
        """Fetch current age from API."""
        response = httpx.get(self.endpoint, timeout=self.timeout)
        response.raise_for_status()
        return float(response.json())

    def default_value(self) -> float:
        return 0.0
