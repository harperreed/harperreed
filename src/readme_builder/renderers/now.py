# ABOUTME: Now section renderer - displays current status/now page content
# ABOUTME: Renders the /now page content as the prominent centered section

from ..fetchers.rss import FeedEntry
from .base import BaseRenderer


class NowRenderer(BaseRenderer):
    """Renders the Now section from /now RSS feed."""

    def render(self, entries: list[FeedEntry]) -> str:
        """Render now section content."""
        if not entries:
            return "No recent updates available. [Check here for the latest.](https://harperreed.com/now/)"

        # The now feed typically has HTML content in description
        return entries[0].description
