set -euo pipefail

rm -rf .snapcraft-project
mkdir -p .snapcraft-project
rsync -a \
  --exclude .git \
  --exclude .snapcraft-project \
  ./ \
  .snapcraft-project/
cp .github/packaging/snap/snapcraft.yaml .snapcraft-project/snapcraft.yaml