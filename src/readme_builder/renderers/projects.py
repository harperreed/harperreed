# ABOUTME: GitHub projects renderer - displays repos with releases or recent activity
# ABOUTME: Renders project list with descriptions, star badges, and release indicators

from ..fetchers.github import GitHubProject
from .base import BaseRenderer


class ProjectsRenderer(BaseRenderer):
    """Renders GitHub projects with releases or recent commits."""

    def render(self, projects: list[GitHubProject]) -> str:
        """Render projects as a list with descriptions and stars."""
        if not projects:
            return "*No recent projects*"

        lines = []
        for project in projects:
            # Truncate long descriptions
            desc = project.description
            if len(desc) > 60:
                desc = desc[:57] + "..."

            # Build badges
            badges = []
            if project.has_release:
                badges.append("📦")
            if project.stars > 0:
                badges.append(f"⭐{project.stars}")

            badge_str = " ".join(badges)

            # Always show owner/repo format
            display_name = f"{project.owner}/{project.name}"

            # Format: [repo-name](url) - description badges
            if desc:
                line = f"* [{display_name}]({project.url}) - {desc} {badge_str}".strip()
            else:
                line = f"* [{display_name}]({project.url}) {badge_str}".strip()
            lines.append(line)

        return "\n".join(lines)
