# ABOUTME: README assembler - combines all sections into final README
# ABOUTME: Handles chunk replacement and static content loading

import pathlib
import re


class ReadmeAssembler:
    """Assembles the final README from sections and static content."""

    def __init__(self, readme_path: pathlib.Path, content_dir: pathlib.Path):
        self.readme_path = readme_path
        self.content_dir = content_dir

    def load_readme(self) -> str:
        """Load current README content."""
        return self.readme_path.read_text()

    def load_static_content(self, name: str) -> str:
        """Load static content file."""
        path = self.content_dir / f"{name}.md"
        if path.exists():
            return path.read_text()
        return ""

    def replace_chunk(self, content: str, marker: str, chunk: str, inline: bool = False) -> str:
        """Replace content between marker comments."""
        pattern = re.compile(
            rf"<!\-\- {marker} starts \-\->.*<!\-\- {marker} ends \-\->",
            re.DOTALL,
        )
        if not inline:
            chunk = f"\n{chunk}\n"
        replacement = f"<!-- {marker} starts -->{chunk}<!-- {marker} ends -->"
        return pattern.sub(replacement, content)

    def save_readme(self, content: str) -> bool:
        """Save README if content changed. Returns True if saved."""
        current = self.load_readme()
        if content != current:
            self.readme_path.write_text(content)
            return True
        return False
