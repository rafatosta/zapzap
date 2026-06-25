# Changelog

This changelog summarizes the project history that can be verified from the repository
metadata, packaging files and current source tree.

## Versioning policy

ZapZap exposes its application version in `zapzap/__init__.py` through the
`__version__` attribute. Python packaging reads that value dynamically from
`pyproject.toml`, and package builders reuse the same source of truth where possible.

- Version tags are expected to match release artifacts published on GitHub.
- Packaging metadata should be updated when a package format requires a static version.
- User-visible changes should be grouped as features, fixes or improvements.

## Release history

### 6.5.2.4

Current repository version.

#### Features

- WhatsApp Web desktop client implemented with Python, PyQt6 and QtWebEngine.
- Multi-account support with isolated web profiles.
- Desktop notifications with environment-specific backends.
- System tray integration.
- Light, dark and system theme support.
- Custom CSS and JavaScript loading, globally and per account.
- Spell checking support through QtWebEngine dictionaries.
- Build support for Flatpak, AppImage, Snap, DEB, RPM and Windows executable artifacts.

#### Fixes

- No repository-local fix entries are available for this version.

#### Improvements

- Packaging scripts share common installation helpers for wheel installation,
  dictionary installation and package validation.
- Development and packaging documentation has been reorganized into `docs/`.

## Related documentation

- [Release process](docs/release-process.md)
- [Packaging](docs/packaging.md)
- [Development](docs/development.md)
