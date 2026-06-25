# Installation

This guide lists the installation options represented by the repository packaging files
and release tooling.

## Overview

ZapZap can be installed from published packages or built from source. GitHub releases
are the central location for release artifacts that are not distributed by a package
store.

## Flatpak

The repository contains the Flatpak manifest `com.rtosta.zapzap.yaml`. Published builds
are linked from Flathub:

- [ZapZap on Flathub](https://flathub.org/apps/details/com.rtosta.zapzap)
- [Flathub manifest repository](https://github.com/flathub/com.rtosta.zapzap)

## AppImage

AppImage artifacts are published through GitHub releases when available:

- [Latest GitHub releases](https://github.com/rafatosta/zapzap/releases)

The local AppImage builder is documented in [Packaging](packaging.md).

## Snap

Snap packaging files are available under `builders/snap/`. Build details are documented
in [Packaging](packaging.md).

## DEB

DEB packaging is available through `builders/deb/build.sh`. Build details are documented
in [Packaging](packaging.md).

## RPM

RPM packaging metadata is provided by `com.rtosta.zapzap.spec`. Build details are
documented in [Packaging](packaging.md).

## Windows

Windows executable build support is provided by `builders/windows_builder.py`. Published
Windows artifacts, when available, are distributed through GitHub releases.

## Building from source

Use the development guide to create a Python environment, install dependencies and run
ZapZap locally:

- [Development setup](development.md)

Minimal source install example:

```bash
pip install .
zapzap
```

## Related documentation

- [Development](development.md)
- [Packaging](packaging.md)
- [Troubleshooting](troubleshooting.md)
