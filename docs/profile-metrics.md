# Profile metrics

The seven SVG cards in the README use [Metrics](https://github.com/lowlighter/metrics),
inspired by [Jess Frazelle's profile](https://github.com/jessfraz/jessfraz).
They show a profile overview, repositories, activity and community contributions,
a 3D contribution calendar, languages and issue/PR follow-up, coding habits, and achievements.

## Setup

1. Create a [classic personal access token](https://github.com/settings/tokens)
   with **no scopes**. The cards only need public data. Choose an expiration date;
   replace the secret when the token expires.
2. Add it as the `METRICS_TOKEN`
   [Actions repository secret](https://github.com/harperreed/harperreed/settings/secrets/actions).
   Do not put the token in a file or paste it into chat.
3. Push the metrics workflow to the task branch. Its push trigger generates and
   commits the initial SVGs to that branch. Check all seven render steps and the images
   before merging; the README references those files.

After merging, **Profile Metrics** refreshes the cards daily at 06:47 UTC.
It also runs when the workflow or stats source changes, and supports manual runs.
The token above reads public GitHub data; the built-in `GITHUB_TOKEN` commits
the SVGs. No private repository or organization access is needed.

Stars, forks, releases, and the most-used-language chart sample the 20 most
recently updated public, non-fork repositories. Larger queries can time out;
Metrics can then render empty repository data without failing. Both
`repositories` and `repositories_batch` are set to 20 to keep that scope explicit.
The final verification job checks the generated files and rejects a zero-star
repository card, since Harper's public repositories have stars.

The shared renderer in `.github/actions/profile-metrics/action.yml` pins the
approved, unmerged [upstream compatibility fix](https://github.com/lowlighter/metrics/pull/1834)
at `1e49d0b8b932624dd7762147e35ccc137eda09f1`. It handles push events without
commit arrays and replaces the retired Projects (classic) count with Projects V2.
`use_prebuilt_image: no` ensures that code actually runs. The workflow builds
the image once and reuses it for all seven cards on one runner.

## Editing and checking

Edit `content/github_stats.md` for the card layout. The README builder copies
that source into the `github_stats` section; editing only `README.md` gets
overwritten. Generated SVGs live in `metrics/`.

Run `uv run python -m unittest discover -s tests -v` to check that every card has
a generator and survives a README rebuild. Run `actionlint` to check workflows,
and `uv run ruff check .` for Python linting.
