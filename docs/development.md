# Development

This document describes the local development environment, repository structure and
commands used to run and build ZapZap from source.

## Requirements

- Python 3.8 or newer.
- `pip` and `venv`.
- QtWebEngine runtime dependencies required by PyQt6-WebEngine.
- Linux DBus development packages when installing `dbus-python` from source.

On Fedora-like systems, `dbus-python` may require:

```bash
sudo dnf install -y dbus-devel pkg-config gcc python3-devel
```

## Clone repository

```bash
git clone https://github.com/rafatosta/zapzap.git
cd zapzap
```

## Python environment

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
```

## Dependencies

Install the development dependency set from `requirements.txt`:

```bash
pip install -r requirements.txt
```

The Python package metadata in `pyproject.toml` declares the runtime dependencies
`PyQt6` and `PyQt6-WebEngine`.

## Running locally

Use local mode to run directly from the source checkout:

```bash
python run.py --local
```

The package entry point can also be installed and executed as `zapzap`:

```bash
pip install .
zapzap
```

## Project structure

| Path | Purpose |
| --- | --- |
| `zapzap/controllers/` | Main window, settings pages and UI orchestration. |
| `zapzap/services/` | Reusable services for settings, themes and environment handling. |
| `zapzap/webengine/` | QtWebEngine integration and injected JavaScript helpers. |
| `zapzap/ui/` | Qt Designer `.ui` source files. |
| `zapzap/views/` | Python UI files generated from Qt Designer files. |
| `zapzap/notifications/` | Notification service and platform-specific backends. |
| `po/` | Source translation catalogs. |
| `zapzap/po/` | Compiled gettext catalogs packaged with the app. |
| `builders/` | Packaging builders for supported artifact formats. |
| `tools/` | Local runner, Flatpak runner and helper scripts. |
| `share/` | Desktop entry, icon, screenshots and AppStream metadata. |

## Build commands

Build commands are package-specific. See [Packaging](packaging.md) for the complete
packaging overview.

Common development commands:

```bash
python run.py --local
pip install .
python -m build --wheel
```

## Related documentation

- [Packaging](packaging.md)
- [Contributing](../CONTRIBUTING.md)
- [Technical documentation](technical-documentation.md)
