# Gotchas

- 2026-10-31: `content/github_stats.md` owns the profile card layout; the daily
  builder copies it into `README.md`. Profile Metrics needs a scopeless classic
  PAT in `METRICS_TOKEN` to read user-wide public data. The repository token only
  commits the SVGs. Generate all seven files on the task branch before merging
  the README links. See `docs/profile-metrics.md` for setup.

- 2026-10-31: The README workflow must stage only `README.md`. Python 3.12 caches
  are already tracked, and `uv run` rewrites them on the runner; staging all files
  adds unrelated bytecode changes to bot commits.

- 2026-10-31: Metrics can return a successful render with zero repository data
  after a 100-repo GraphQL query times out: its retry loop exits without retrying.
  Use an explicit 20-repo sample (`repositories` and `repositories_batch`), label
  the sample in the README, and verify the generated SVGs before merging.
