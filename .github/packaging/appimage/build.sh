#!/usr/bin/env bash
set -euo pipefail

# CI-only wrapper.
# Prefer the new CI path; fallback keeps the current release.yml compatible during migration.
GET_DEPS=".github/packaging/appimage/scripts/get-dependencies.sh"
MAKE_APPIMAGE=".github/packaging/appimage/scripts/make-appimage.sh"

chmod +x "$GET_DEPS" "$MAKE_APPIMAGE"
"$GET_DEPS"
find . -name "*.bdic" | sort || true
"$MAKE_APPIMAGE"
