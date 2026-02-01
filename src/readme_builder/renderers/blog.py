# ABOUTME: Blog posts renderer - displays recent blog entries as a list
# ABOUTME: Renders blog posts with title links

from ..fetchers.rss import FeedEntry
from .base import BaseRenderer


class BlogRenderer(BaseRenderer):
    """Renders recent blog posts as a markdown list."""

    def render(self, entries: list[FeedEntry]) -> str:
        """Render blog posts as bullet list."""
        if not entries:
            return "*No recent posts*"

        lines = [f"* [{entry.title}]({entry.url})" for entry in entries]
        return "\n".join(lines)
