set -euo pipefail

rm -rf .snapcraft-project
mkdir -p .snapcraft-project

rsync -a \
  --exclude .git \
  --exclude .snapcraft-project \
  ./ \
  .snapcraft-project/

if [[ ! -f .github/packaging/snap/snapcraft.yaml ]]; then
  echo "snapcraft.yaml not found at .github/packaging/snap/snapcraft.yaml"
  exit 1
fi

cp .github/packaging/snap/snapcraft.yaml .snapcraft-project/snapcraft.yaml

cd .snapcraft-project
snapcraft