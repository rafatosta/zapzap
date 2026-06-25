#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "${SCRIPT_DIR}/../.." && pwd)
PROJECT_DIR=${SNAPCRAFT_PROJECT_DIR:-"${ROOT_DIR}/.snapcraft-project"}

rm -rf "${PROJECT_DIR}"
mkdir -p "${PROJECT_DIR}"

rsync -a \
    --exclude .git \
    --exclude .snapcraft-project \
    "${ROOT_DIR}/" \
    "${PROJECT_DIR}/"

cp "${SCRIPT_DIR}/snapcraft.yaml" "${PROJECT_DIR}/snapcraft.yaml"

cd "${PROJECT_DIR}"
snapcraft pack "$@"
