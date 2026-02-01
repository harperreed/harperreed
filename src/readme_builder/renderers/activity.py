# ABOUTME: Unified activity renderer - combines notes, books, music, links
# ABOUTME: Renders a mixed feed of recent activity with type icons

from ..fetchers.rss import FeedEntry
from .base import BaseRenderer

# Icons for different activity types
ACTIVITY_ICONS = {
    "note": "📝",
    "book": "📚",
    "music": "🎵",
    "link": "🔗",
}


class ActivityRenderer(BaseRenderer):
    """Renders unified activity feed from multiple sources."""

    def __init__(self, max_items: int = 8):
        self.max_items = max_items

    def render(self, entries_by_type: dict[str, list[FeedEntry]]) -> str:
        """Render unified activity feed, sorted by date."""
        # Flatten all entries
        all_entries: list[FeedEntry] = []
        for entries in entries_by_type.values():
            all_entries.extend(entries)

        if not all_entries:
            return "*No recent activity*"

        # Sort by published date, most recent first
        all_entries.sort(
            key=lambda e: e.published if e.published else e.published_str,
            reverse=True,
        )

        # Take top N items
        display_entries = all_entries[: self.max_items]

        lines = []
        for entry in display_entries:
            icon = ACTIVITY_ICONS.get(entry.entry_type, "•")
            lines.append(f"* {icon} [{entry.title}]({entry.url})")

        return "\n".join(lines)
