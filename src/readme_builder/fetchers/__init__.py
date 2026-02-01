# ABOUTME: Fetcher module for retrieving data from external sources
# ABOUTME: Contains RSS, GitHub, and age endpoint fetchers

from .age import AgeFetcher
from .base import BaseFetcher
from .github import GitHubFetcher
from .rss import RSSFetcher

__all__ = ["BaseFetcher", "RSSFetcher", "GitHubFetcher", "AgeFetcher"]
