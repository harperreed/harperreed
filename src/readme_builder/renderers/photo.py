# ABOUTME: Photo renderer - displays the latest photo from harper.photos
# ABOUTME: Renders a single featured photo with caption

from ..fetchers.rss import FeedEntry
from .base import BaseRenderer


class PhotoRenderer(BaseRenderer):
    """Renders the latest photo."""

    def render(self, entries: list[FeedEntry]) -> str:
        """Render latest photo with caption."""
        if not entries:
            return "*No recent photos*"

        entry = entries[0]
        if not entry.media_url:
            return "*No photo available*"

        # Image with link to full photo page, plus caption
        return f"[![{entry.title}]({entry.media_url})]({entry.url})\n*{entry.description}*"
