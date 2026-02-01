# ABOUTME: GitHub fetcher for repos with releases or recent commits
# ABOUTME: Uses gh CLI to fetch repos from user and specified orgs

import json
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from .base import BaseFetcher


@dataclass
class GitHubProject:
    name: str
    description: str
    url: str
    stars: int
    language: str | None
    pushed_at: datetime
    has_release: bool = False
    owner: str = ""


class GitHubFetcher(BaseFetcher):
    """Fetches GitHub repos with releases or recent commits from user and orgs."""

    def __init__(
        self,
        username: str,
        orgs: list[str] | None = None,
        exclude_repos: list[str] | None = None,
        max_count: int = 10,
        min_stars: int = 0,
        months_active: int = 6,
        timeout: float = 30.0,
    ):
        super().__init__(timeout)
        self.username = username
        self.orgs = orgs or []
        self.exclude_repos = set(exclude_repos or [])
        self.max_count = max_count
        self.min_stars = min_stars
        self.months_active = months_active

    def fetch(self) -> list[GitHubProject]:
        """Fetch repos from user and orgs, mixing sources fairly."""
        cutoff = datetime.now(UTC) - timedelta(days=self.months_active * 30)

        # Fetch and filter repos from each source separately
        user_repos = self._get_filtered_repos(self.username, is_user=True, cutoff=cutoff)
        org_repos_by_org: dict[str, list[dict]] = {}
        for org in self.orgs:
            repos = self._get_filtered_repos(org, is_user=False, cutoff=cutoff)
            if repos:
                org_repos_by_org[org] = repos

        # Check releases and sort each source by pushed_at
        user_repos = self._check_and_sort_repos(user_repos)

        for org in org_repos_by_org:
            org_repos_by_org[org] = self._check_and_sort_repos(org_repos_by_org[org])

        # Combine all repos and sort by pushed_at
        all_repos = user_repos[:]
        for org_repo_list in org_repos_by_org.values():
            all_repos.extend(org_repo_list)

        # Sort by pushed_at descending (most recent first)
        all_repos.sort(key=lambda r: r["pushed_at"], reverse=True)

        # Take top N, ensuring at least some org representation if available
        selected = all_repos[: self.max_count]

        return [
            GitHubProject(
                name=r["name"],
                description=r["description"] or "",
                url=r["url"],
                stars=r["stars"],
                language=r["language"],
                pushed_at=r["pushed_at"],
                has_release=r.get("has_release", False),
                owner=r["owner"],
            )
            for r in selected[: self.max_count]
        ]

    def _get_filtered_repos(self, owner: str, is_user: bool, cutoff: datetime) -> list[dict]:
        """Fetch repos and filter by date and stars."""
        repos = self._fetch_repos_for_owner(owner, is_user=is_user)

        # Filter by activity date, stars, and exclusion list
        filtered = [
            r
            for r in repos
            if r["pushed_at"] > cutoff
            and r["stars"] >= self.min_stars
            and r["name"] not in self.exclude_repos
        ]

        return filtered

    def _check_and_sort_repos(self, repos: list[dict]) -> list[dict]:
        """Sort by pushed_at and check releases for top candidates."""
        repos.sort(key=lambda r: r["pushed_at"], reverse=True)

        # Only check releases for top candidates to avoid too many API calls
        for repo in repos[: self.max_count * 2]:
            repo["has_release"] = self._has_releases(repo["owner"], repo["name"])

        return repos

    def default_value(self) -> list[GitHubProject]:
        return []

    def _fetch_repos_for_owner(self, owner: str, is_user: bool = True) -> list[dict]:
        """Fetch repos for a user or org using gh CLI."""
        endpoint = f"/users/{owner}/repos" if is_user else f"/orgs/{owner}/repos"
        cmd = [
            "gh",
            "api",
            endpoint,
            "--paginate",
            "-q",
            ".[] | {name, description, url: .html_url, stars: .stargazers_count, "
            "language, pushed_at, fork, owner: .owner.login}",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout fetching repos for {owner}")
            return []

        if result.returncode != 0:
            self.logger.error(f"gh api failed for {owner}: {result.stderr}")
            return []

        repos = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            try:
                repo = json.loads(line)
                # Skip forks
                if repo.get("fork"):
                    continue
                # Parse pushed_at
                pushed_str = repo.get("pushed_at", "")
                if pushed_str:
                    repo["pushed_at"] = datetime.fromisoformat(pushed_str.replace("Z", "+00:00"))
                else:
                    repo["pushed_at"] = datetime.min.replace(tzinfo=UTC)
                repos.append(repo)
            except json.JSONDecodeError:
                continue

        return repos

    def _has_releases(self, owner: str, repo_name: str) -> bool:
        """Check if a repo has any releases."""
        cmd = [
            "gh",
            "api",
            f"/repos/{owner}/{repo_name}/releases",
            "-q",
            "length",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return False
            count = int(result.stdout.strip())
            return count > 0
        except (subprocess.TimeoutExpired, ValueError):
            return False
