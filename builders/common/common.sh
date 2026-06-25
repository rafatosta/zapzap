#!/bin/sh

set -eu

ROOT_DIR=${ROOT_DIR:-$(pwd)}
DIST_DIR=${DIST_DIR:-"${ROOT_DIR}/dist"}
DESTDIR=${DESTDIR:-}
PREFIX=${PREFIX:-/usr}
PYTHON=${PYTHON:-python3}

log() {
    printf '\n==> %s\n' "$*"
}

_require_destdir() {
    if [ -z "${DESTDIR}" ]; then
        echo "DESTDIR must be set before installing." >&2
        exit 1
    fi

    case "${DESTDIR}" in
        /|/usr|/usr/|/usr/local|/usr/local/)
            echo "Refusing to install into host filesystem DESTDIR=${DESTDIR}" >&2
            exit 1
            ;;
    esac
}

build_wheel() {
    log "Building wheel"
    mkdir -p "${DIST_DIR}"
    rm -f "${DIST_DIR}"/*.whl
    (cd "${ROOT_DIR}" && "${PYTHON}" -Im build --wheel --outdir "${DIST_DIR}")
}

_find_wheel() {
    set -- "${DIST_DIR}"/*.whl
    if [ ! -e "$1" ]; then
        echo "No wheel found in ${DIST_DIR}" >&2
        exit 1
    fi
    if [ "$#" -ne 1 ]; then
        echo "Expected exactly one wheel in ${DIST_DIR}, found $#" >&2
        exit 1
    fi
    printf '%s\n' "$1"
}

install_wheel() {
    _require_destdir
    wheel=$(_find_wheel)
    log "Installing wheel into ${DESTDIR}"
    mkdir -p "${DESTDIR}"
    "${PYTHON}" -Im installer --destdir "${DESTDIR}" --prefix "${PREFIX}" "${wheel}"
    _normalize_executable
}

_normalize_executable() {
    expected_bin="${DESTDIR}${PREFIX}/bin/zapzap"

    if [ -x "${expected_bin}" ]; then
        return 0
    fi

    installed_bin=$(find "${DESTDIR}" -type f -path "*/bin/zapzap" -perm -111 | head -n 1)

    if [ -n "${installed_bin}" ]; then
        log "Normalizing executable path to ${expected_bin}"
        mkdir -p "$(dirname "${expected_bin}")"
        cp -f "${installed_bin}" "${expected_bin}"
        chmod 755 "${expected_bin}"
    fi
}

project_version() {
    "${PYTHON}" - <<EOF_PY
from pathlib import Path
import ast

init_py = Path("${ROOT_DIR}") / "zapzap" / "__init__.py"
for node in ast.parse(init_py.read_text(encoding="utf-8")).body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__version__":
                print(ast.literal_eval(node.value))
                raise SystemExit
raise SystemExit("__version__ not found")
EOF_PY
}

find_qt_dir() {
    "${PYTHON}" - <<'EOF_PY'
from pathlib import Path
candidates = [
    Path('/usr/lib/qt6'),
    Path('/usr/lib64/qt6'),
    Path(f'/usr/lib/{__import__("platform").machine()}-linux-gnu/qt6'),
    Path('/usr/lib/x86_64-linux-gnu/qt6'),
]
for path in candidates:
    if path.exists():
        print(path)
        raise SystemExit
raise SystemExit('Qt6 installation directory not found')
EOF_PY
}

install_dictionaries() {
    _require_destdir
    log "Installing QtWebEngine dictionaries into ${DESTDIR}"
    dict_dst="${DESTDIR}${PREFIX}/share/zapzap/qtwebengine_dictionaries"
    mkdir -p "${dict_dst}"

    if [ -d "${ROOT_DIR}/qtwebengine_dictionaries" ]; then
        dict_src="${ROOT_DIR}/qtwebengine_dictionaries"
    elif [ -d "${ROOT_DIR}/zapzap/qtwebengine_dictionaries" ]; then
        dict_src="${ROOT_DIR}/zapzap/qtwebengine_dictionaries"
    else
        echo "No qtwebengine_dictionaries directory found; skipping." >&2
        return 0
    fi

    found=0
    for dict in "${dict_src}"/*.bdic; do
        [ -e "${dict}" ] || continue
        cp -f "${dict}" "${dict_dst}/"
        found=1
    done

    if [ "${found}" -eq 0 ]; then
        echo "No .bdic dictionaries found in ${dict_src}; skipping." >&2
    fi
}

validate_install() {
    _require_destdir
    log "Validating installation in ${DESTDIR}"
    [ -x "${DESTDIR}${PREFIX}/bin/zapzap" ] || {
        echo "Missing executable: ${DESTDIR}${PREFIX}/bin/zapzap" >&2
        exit 1
    }

    "${PYTHON}" - <<EOF_PY
from pathlib import Path
import sys
root = Path("${DESTDIR}")
matches = list(root.glob("**/site-packages/zapzap/__init__.py"))
matches.extend(root.glob("**/dist-packages/zapzap/__init__.py"))
if not matches:
    sys.exit("Missing installed zapzap package under DESTDIR")
EOF_PY
}

prepare_package() {
    build_wheel
    install_wheel
    install_dictionaries
    validate_install
}
