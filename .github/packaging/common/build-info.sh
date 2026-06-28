#!/usr/bin/env bash
set -euo pipefail

PACKAGING="${1:?usage: build-info.sh <packaging-name>}"

cat > zapzap/BuildInfo.py <<EOF_BUILD_INFO
BUILD_CHANNEL = "Official"
BUILD_PROVIDER = "GitHub Actions"
BUILD_REPOSITORY = "${GITHUB_REPOSITORY:-unknown}"
BUILD_PACKAGING = "${PACKAGING}"
EOF_BUILD_INFO
