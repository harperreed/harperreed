# ABOUTME: Now section renderer - displays current status/now page content
# ABOUTME: Converts HTML from RSS feed to clean markdown

import html
import re

from ..fetchers.rss import FeedEntry
from .base import BaseRenderer


class NowRenderer(BaseRenderer):
    """Renders the Now section from /now RSS feed."""

    def render(self, entries: list[FeedEntry]) -> str:
        """Render now section content, converting HTML to markdown."""
        if not entries:
            return "*No recent updates available.*"

        content = entries[0].description
        return self._html_to_markdown(content)

    def _html_to_markdown(self, html_content: str) -> str:
        """Convert HTML to clean markdown."""
        text = html_content

        # Decode HTML entities
        text = html.unescape(text)

        # Remove video/figure elements (not supported in GitHub markdown)
        text = re.sub(r"<figure[^>]*>.*?</figure>", "", text, flags=re.DOTALL)
        text = re.sub(r"<video[^>]*>.*?</video>", "", text, flags=re.DOTALL)

        # Convert headers
        text = re.sub(r"<h2[^>]*>(.*?)</h2>", r"### \1", text)
        text = re.sub(r"<h3[^>]*>(.*?)</h3>", r"#### \1", text)
        text = re.sub(r"<h4[^>]*>(.*?)</h4>", r"**\1**", text)

        # Convert links
        text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r"[\2](\1)", text)

        # Convert emphasis
        text = re.sub(r"<strong>(.*?)</strong>", r"**\1**", text)
        text = re.sub(r"<em>(.*?)</em>", r"*\1*", text)

        # Convert lists
        text = re.sub(r"<ul[^>]*>", "", text)
        text = re.sub(r"</ul>", "", text)
        text = re.sub(r"<li>(.*?)</li>", r"- \1", text, flags=re.DOTALL)

        # Convert paragraphs
        text = re.sub(r"<p>(.*?)</p>", r"\1\n", text, flags=re.DOTALL)

        # Remove any remaining HTML tags
        text = re.sub(r"<[^>]+>", "", text)

        # Clean up whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"^- ", "- ", text, flags=re.MULTILINE)

        return text.strip()
