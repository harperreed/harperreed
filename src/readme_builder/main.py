# ABOUTME: Main orchestrator for README generation
# ABOUTME: Coordinates fetchers and renderers to build the final README

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from .config import Config, load_config
from .fetchers import AgeFetcher, GitHubFetcher, RSSFetcher
from .fetchers.rss import FeedEntry
from .renderers import (
    ActivityRenderer,
    BlogRenderer,
    NowRenderer,
    PhotoRenderer,
    ProjectsRenderer,
    ReadmeAssembler,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_all_data(config: Config) -> dict[str, Any]:
    """Fetch all data concurrently."""
    data: dict[str, Any] = {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {}

        # RSS feeds
        for name, feed_config in config.feeds.items():
            fetcher = RSSFetcher(
                url=feed_config.url,
                max_entries=feed_config.max_entries,
                entry_type=feed_config.type,
            )
            futures[executor.submit(fetcher.safe_fetch)] = f"feed_{name}"

        # GitHub projects
        github_fetcher = GitHubFetcher(
            username=config.github.username,
            orgs=config.github.orgs,
            max_count=config.github.max_count,
            min_stars=config.github.min_stars,
            months_active=config.github.months_active,
        )
        futures[executor.submit(github_fetcher.safe_fetch)] = "github_projects"

        # Age
        if config.age_endpoint:
            age_fetcher = AgeFetcher(endpoint=config.age_endpoint)
            futures[executor.submit(age_fetcher.safe_fetch)] = "age"

        # Collect results
        for future in as_completed(futures):
            key = futures[future]
            try:
                data[key] = future.result()
                logger.info(f"Fetched {key}")
            except Exception as e:
                logger.error(f"Failed to fetch {key}: {e}")
                data[key] = None

    return data


def build_readme(config: Config, data: dict[str, Any]) -> str:
    """Build the README content from fetched data."""
    assembler = ReadmeAssembler(config.readme_path, config.content_dir)
    content = assembler.load_readme()

    # Static content sections
    for section in ["bio", "links", "details", "github_stats", "social"]:
        static_content = assembler.load_static_content(section)
        if static_content:
            content = assembler.replace_chunk(content, section, static_content)

    # Now section (centered/prominent)
    now_entries = data.get("feed_now", [])
    now_renderer = NowRenderer()
    content = assembler.replace_chunk(content, "now", now_renderer.render(now_entries))

    # Blog posts
    blog_entries = data.get("feed_blog", [])
    blog_renderer = BlogRenderer()
    content = assembler.replace_chunk(content, "blog", blog_renderer.render(blog_entries))

    # Latest photo
    photo_entries = data.get("feed_photos", [])
    photo_renderer = PhotoRenderer()
    content = assembler.replace_chunk(content, "photos", photo_renderer.render(photo_entries))

    # GitHub projects
    projects = data.get("github_projects", [])
    projects_renderer = ProjectsRenderer()
    content = assembler.replace_chunk(content, "projects", projects_renderer.render(projects))

    # Unified activity feed
    activity_data: dict[str, list[FeedEntry]] = {}
    for feed_name in config.activity_feeds:
        entries = data.get(f"feed_{feed_name}", [])
        if entries:
            activity_data[feed_name] = entries

    activity_renderer = ActivityRenderer(max_items=config.display.activity_max_items)
    content = assembler.replace_chunk(content, "activity", activity_renderer.render(activity_data))

    # Age
    age = data.get("age", 0.0)
    if age > 0:
        age_md = f"- 👨Age: {age:.1f} years old"
        content = assembler.replace_chunk(content, "age", age_md)

    return content


def main():
    """Main entry point."""
    logger.info("Starting README build...")

    config = load_config()
    logger.info(f"Loaded config with {len(config.feeds)} feeds")

    data = fetch_all_data(config)
    logger.info("All data fetched")

    content = build_readme(config, data)
    logger.info("README content built")

    assembler = ReadmeAssembler(config.readme_path, config.content_dir)
    if assembler.save_readme(content):
        logger.info("README.md updated successfully")
    else:
        logger.info("No changes detected. README.md not updated.")


if __name__ == "__main__":
    main()
