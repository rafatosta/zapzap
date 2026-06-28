#!/usr/bin/env bash
set -euo pipefail

rm -rf .snapcraft-project
mkdir -p .snapcraft-project
rsync -a \
  --exclude .git \
  --exclude .snapcraft-project \
  ./ \
  .snapcraft-project/

if [[ -s .github/packaging/snap/snapcraft.yaml ]] && ! grep -q "Move the current" .github/packaging/snap/snapcraft.yaml; then
  cp .github/packaging/snap/snapcraft.yaml .snapcraft-project/snapcraft.yaml
elif [[ -f builders/snap/snapcraft.yaml ]]; then
  cp builders/snap/snapcraft.yaml .snapcraft-project/snapcraft.yaml
else
  echo "snapcraft.yaml not found. Move builders/snap/snapcraft.yaml to .github/packaging/snap/snapcraft.yaml"
  exit 1
fi
