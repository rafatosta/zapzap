# Release process

This document describes the release workflow implied by the repository version metadata,
package builders and GitHub-based distribution model.

## Version update

- Update `__version__` in `zapzap/__init__.py`.
- Update package metadata that stores a static version, such as
  `com.rtosta.zapzap.spec` when an RPM release is prepared.
- Update `CHANGELOG.md` with user-visible features, fixes and improvements.

## Build pipeline

Validate the source checkout before producing release artifacts:

```bash
python run.py --local
python -m build --wheel
```

Package-specific builders may require additional system tools such as Flatpak Builder,
Snapcraft, RPM tooling, Debian packaging tools or PyInstaller.

## Packaging

Use the commands documented in [Packaging](packaging.md) for each target format.
Release artifacts should be produced from a clean checkout or release tag.

## GitHub Release

- Create a Git tag that matches the release version.
- Build and upload the supported artifacts for the release.
- Include concise release notes based on `CHANGELOG.md`.
- Link installation documentation for users who need package-specific guidance.

## Website update

If the project website links to specific downloads or release notes, update those links
after the GitHub release and package-store updates are available.

## Related documentation

- [Changelog](../CHANGELOG.md)
- [Packaging](packaging.md)
- [Installation](installation.md)
