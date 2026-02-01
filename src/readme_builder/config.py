# ABOUTME: Configuration loader for the README builder
# ABOUTME: Reads config.yaml and provides typed access to settings

import pathlib
from dataclasses import dataclass

import yaml


@dataclass
class FeedConfig:
    url: str
    max_entries: int
    type: str


@dataclass
class GitHubConfig:
    username: str
    orgs: list[str]
    max_count: int = 10
    min_stars: int = 0
    months_active: int = 6


@dataclass
class DisplayConfig:
    activity_max_items: int = 8


@dataclass
class Config:
    github: GitHubConfig
    feeds: dict[str, FeedConfig]
    activity_feeds: list[str]
    age_endpoint: str
    display: DisplayConfig
    content_dir: pathlib.Path
    readme_path: pathlib.Path


def load_config(config_path: pathlib.Path | None = None) -> Config:
    """Load configuration from YAML file."""
    if config_path is None:
        config_path = pathlib.Path(__file__).parent.parent.parent / "config.yaml"

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    root = config_path.parent

    github_raw = raw.get("github", {})
    projects_raw = github_raw.get("projects", {})
    github = GitHubConfig(
        username=github_raw.get("username", "harperreed"),
        orgs=github_raw.get("orgs", []),
        max_count=projects_raw.get("max_count", 10),
        min_stars=projects_raw.get("min_stars", 0),
        months_active=projects_raw.get("months_active", 6),
    )

    feeds = {}
    for name, feed_raw in raw.get("feeds", {}).items():
        feeds[name] = FeedConfig(
            url=feed_raw["url"],
            max_entries=feed_raw.get("max_entries", 5),
            type=feed_raw.get("type", name),
        )

    display_raw = raw.get("display", {})
    display = DisplayConfig(
        activity_max_items=display_raw.get("activity_max_items", 8),
    )

    return Config(
        github=github,
        feeds=feeds,
        activity_feeds=raw.get("activity_feeds", []),
        age_endpoint=raw.get("age_endpoint", ""),
        display=display,
        content_dir=root / "content",
        readme_path=root / "README.md",
    )
