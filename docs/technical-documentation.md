# Technical documentation

ZapZap is a Python desktop application that embeds WhatsApp Web in a PyQt6 and
QtWebEngine shell, then adds desktop integration through services, controllers and
package-specific runtime configuration.

## Overview

- Language: Python 3.8 or newer.
- UI toolkit: PyQt6.
- Web engine: PyQt6-WebEngine.
- Settings: Qt `QSettings`.
- Account metadata: SQLite.
- Translations: gettext catalogs from `po/` and `zapzap/po/`.
- Packaging: Flatpak, AppImage, Snap, RPM, DEB and Windows builder support.

## Startup flow

1. `zapzap.__main__:main` starts the application entry point.
2. Environment setup configures QtWebEngine, display and dictionary paths.
3. Translation setup loads gettext resources.
4. Crash handling and single-instance behavior are initialized.
5. The main window restores saved state and loads accounts.
6. Each account creates an isolated `QWebEngineProfile` and loads WhatsApp Web.

## Architecture

### Controllers and views

- `zapzap/controllers/` contains main-window and settings-page behavior.
- `zapzap/ui/` contains Qt Designer source files.
- `zapzap/views/` contains generated Python classes for the UI files.

### Web engine layer

- `zapzap/webengine/WebView.py` manages profile, downloads, spell checking and
  context-menu behavior.
- `zapzap/webengine/PageController.py` handles navigation, permissions, new-window
  behavior, injected scripts and theme integration.
- JavaScript helpers are stored in `zapzap/webengine/`.

### Services

- `SettingsManager` wraps application settings.
- `ThemeManager` applies light, dark and system theme behavior.
- `CustomizationsManager` manages CSS and JavaScript customizations.
- `DownloadManager` handles QtWebEngine downloads.
- `DictionariesManager` and `PathManager` resolve dictionary locations.
- `SysTrayManager` manages tray menu and tray interactions.
- `EnvironmentManager` and `EnvironmentDetector` handle runtime environment details.

### Notifications

`NotificationService` selects an available backend for the current environment:

- Portal notifications for sandboxed environments where available.
- Freedesktop notifications on Linux desktops that support them.
- Windows notifications for Windows builds.

## Persistence

- Account metadata is stored in SQLite through the project configuration layer.
- Application preferences are stored with `QSettings`.
- Customization files are stored under application-local data directories for global
  and per-account CSS and JavaScript.
- Compiled translations are packaged under `zapzap/po/`.

## Package integration

Package builders share the same Python project metadata and install the application
entry point `zapzap`. Linux package metadata also installs the desktop file, icon and
AppStream metadata from `share/` where applicable.

## Maintenance guidance

- Add reusable application behavior under `zapzap/services/`.
- Keep controller classes focused on UI orchestration.
- Regenerate `zapzap/views/` when Qt Designer files in `zapzap/ui/` change.
- Validate QtWebEngine changes on the affected display server and package format.
- Update documentation when commands, paths or package behavior change.

## Related documentation

- [Development](development.md)
- [Packaging](packaging.md)
- [Troubleshooting](troubleshooting.md)
