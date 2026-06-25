# Packaging

This document explains the package formats represented in the repository and the build
scripts used to create distribution artifacts.

## Packaging overview

ZapZap packaging is based on a Python wheel installed into a package-specific root. The
shared shell helpers in `builders/common/common.sh` build the wheel, install it through
`installer`, copy dictionaries when present and validate the result.

| Format | Repository entry point | Output location |
| --- | --- | --- |
| Flatpak | `com.rtosta.zapzap.yaml`, `builders/flatpak_builder.py` | `dist/` |
| AppImage | `builders/appimage_builder.py` | `dist/` |
| Snap | `builders/snap/snapcraft.yaml` | Snapcraft output |
| RPM | `com.rtosta.zapzap.spec` | RPM build tree |
| DEB | `builders/deb/build.sh` | `dist/` |
| Windows | `builders/windows_builder.py` | `dist/` |

## Flatpak

The Flatpak manifest uses KDE Platform and the PyQt BaseApp. It grants network,
Wayland, fallback X11, audio, notification and selected filesystem permissions required
by the embedded WhatsApp Web workflow.

Build with a Flatpak Builder workflow using `com.rtosta.zapzap.yaml`.

## AppImage

The AppImage builder downloads or copies a source tree, builds with PyInstaller,
assembles an AppDir and runs `appimagetool`.

Example for a release tag:

```bash
python builders/appimage_builder.py 6.5.2.4
```

Example for the local checkout:

```bash
python builders/appimage_builder.py dev
```

## Snap

Snap packaging is defined in `builders/snap/snapcraft.yaml`. It uses `core24`, strict
confinement and stages Python, PyQt6, QtWebEngine and Qt Wayland packages.

Build from the repository root with Snapcraft:

```bash
snapcraft -f builders/snap/snapcraft.yaml
```

## RPM

RPM metadata is defined in `com.rtosta.zapzap.spec`. The spec builds a Python wheel,
installs the package and installs the desktop entry and icon.

Example source RPM workflow:

```bash
rpmbuild -ba com.rtosta.zapzap.spec
```

## DEB

The DEB builder uses the shared packaging helpers and creates a Debian package with
`dpkg-deb`.

```bash
builders/deb/build.sh
```

## Windows

The Windows builder compiles selected Qt Designer files, runs PyInstaller in one-file
windowed mode and renames the executable with the project version.

```bash
python builders/windows_builder.py
```

## Package differences

- Flatpak and Snap run under sandboxed environments and require explicit permissions.
- AppImage and Windows artifacts bundle more runtime content through PyInstaller.
- RPM and DEB rely more heavily on distribution Python and Qt package dependencies.
- File chooser, upload and notification behavior can differ by sandbox and display
  server; see [Troubleshooting](troubleshooting.md).

## Related documentation

- [Installation](installation.md)
- [Development](development.md)
- [Release process](release-process.md)
