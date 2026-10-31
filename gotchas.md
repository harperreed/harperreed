# Gotchas

- 2026-10-31: `content/github_stats.md` owns the profile card layout; the daily
  builder copies it into `README.md`. Profile Metrics needs a scopeless classic
  PAT in `METRICS_TOKEN` to read user-wide public data. The repository token only
  commits the SVGs. Generate all seven files on the task branch before merging
  the README links. See `docs/profile-metrics.md` for setup.
