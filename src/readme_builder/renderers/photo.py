# ABOUTME: Photo renderer - displays the latest photo from harper.blog/photos
# ABOUTME: Renders a single featured photo with title link

from ..fetchers.rss import FeedEntry
from .base import BaseRenderer


class PhotoRenderer(BaseRenderer):
    """Renders the latest photo."""

    def render(self, entries: list[FeedEntry]) -> str:
        """Render latest photo with title."""
        if not entries:
            return "*No recent photos*"

        entry = entries[0]
        if not entry.media_url:
            return "*No photo available*"

        # Image with link to full photo page
        return f"[![{entry.title}]({entry.media_url})]({entry.url})"
