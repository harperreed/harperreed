# ABOUTME: RSS feed fetcher for blog posts, notes, books, music, links
# ABOUTME: Generic fetcher that normalizes entries from various RSS sources

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import feedparser

from .base import BaseFetcher


@dataclass
class FeedEntry:
    title: str
    url: str
    published: datetime | None
    description: str
    entry_type: str
    media_url: str | None = None

    @property
    def published_str(self) -> str:
        if self.published:
            return self.published.strftime("%Y-%m-%d")
        return ""


class RSSFetcher(BaseFetcher):
    """Fetches and normalizes RSS feed entries."""

    def __init__(
        self,
        url: str,
        max_entries: int = 5,
        entry_type: str = "post",
        timeout: float = 15.0,
    ):
        super().__init__(timeout)
        self.url = url
        self.max_entries = max_entries
        self.entry_type = entry_type

    def fetch(self) -> list[FeedEntry]:
        """Fetch RSS feed and return normalized entries."""
        feed = feedparser.parse(self.url)
        entries = []

        for entry in feed.entries[: self.max_entries]:
            published = self._parse_date(entry.get("published", ""))
            media_url = self._extract_media(entry)

            entries.append(
                FeedEntry(
                    title=entry.get("title", "Untitled"),
                    url=entry.get("link", "").split("#")[0],
                    published=published,
                    description=entry.get("description", ""),
                    entry_type=self.entry_type,
                    media_url=media_url,
                )
            )

        return entries

    def default_value(self) -> list[FeedEntry]:
        return []

    def _parse_date(self, date_str: str) -> datetime | None:
        """Parse various date formats from RSS feeds."""
        if not date_str:
            return None

        # Try common RSS date formats
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",  # RFC 822
            "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601
            "%Y-%m-%dT%H:%M:%SZ",  # ISO 8601 UTC
            "%Y-%m-%d",  # Simple date
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        # Last resort: try parsing just the date part
        try:
            date_part = date_str.split("T")[0]
            return datetime.strptime(date_part, "%Y-%m-%d")
        except (ValueError, IndexError):
            return None

    def _extract_media(self, entry: dict[str, Any]) -> str | None:
        """Extract media URL from entry (for photos)."""
        media_content = entry.get("media_content", [])
        if media_content and isinstance(media_content, list):
            return media_content[0].get("url")
        return None
