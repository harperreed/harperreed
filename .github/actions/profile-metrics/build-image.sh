#!/usr/bin/env bash
# ABOUTME: Build the pinned Metrics source with its required native build tools.
# ABOUTME: Prepare one local image for all profile-card steps on the Actions runner.

set -euo pipefail

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    echo "Usage: build-image.sh"
    echo "Run in GitHub Actions before the profile-card steps to build their shared image."
    exit 0
fi
if [[ $# -ne 0 ]]; then
    echo "Usage: build-image.sh (or --help)" >&2
    exit 64
fi

trap 'echo "Metrics image build failed at line ${LINENO}; see the build log above." >&2' ERR

build_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
metrics_revision="$(sed -nE 's/^[[:space:]]*- uses: lowlighter\/metrics@([0-9a-f]{40}).*$/\1/p' "$build_root/action.yml")"
if [[ ! "$metrics_revision" =~ ^[0-9a-f]{40}$ ]]; then
    echo "Expected one pinned Metrics commit in $build_root/action.yml" >&2
    exit 1
fi

metrics_source="$(mktemp -d "${RUNNER_TEMP:?Run this build in GitHub Actions}/profile-metrics.XXXXXX")"
git init --quiet "$metrics_source"
git -C "$metrics_source" fetch --quiet --depth=1 https://github.com/lowlighter/metrics "$metrics_revision"
git -C "$metrics_source" checkout --quiet --detach FETCH_HEAD
git -C "$metrics_source" apply "$build_root/build.patch"
metrics_version="$(jq -r .version "$metrics_source/package.json")"

docker build --tag "metrics:forked-$metrics_version" "$metrics_source"
