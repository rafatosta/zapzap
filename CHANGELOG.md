# Changelog

All changes and additions to ZapZap are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/).
Every pull request or commit that changes the repository must add or update an
entry under the version currently marked `In development`, including internal,
documentation, test, packaging, and workflow changes.

This mandatory record starts after version 7.4.1. The 7.4.1 entry below is the
historical baseline; older release summaries remain available in the GitHub
releases and the AppStream metadata.

## [7.4.4] - In development

### Fixed

- Prevented external conversation links from crashing Qt WebEngine by avoiding
  a reentrant stop while its navigation request is still being processed.

## [7.4.3] - 2026-08-30

### Added

- Added Default, Compatibility, and automatically detected Manual rendering
  profiles while retaining every advanced performance control, including new
  GPU video-buffer and zero-copy compatibility switches.
- Added an in-app, privacy-preserving problem reporter with a localized,
  mandatory review, sanitized crash preparation, bounded local history,
  Markdown copying, and a safe handoff to GitHub for account-authenticated
  publication.
- Added a cross-platform Qt WebEngine dictionary manager with verified
  downloads from the official catalog, offline cache, local imports, removal,
  progress, cancellation, search, filters, and accessible active-language
  management.

### Changed

- Expanded interface scale choices from 50% through 200% to use 5% increments
  while preserving the existing global scale setting and restart behavior.
- Added a dedicated Conventional Commits guide and required every code or
  structural change to include a copy-ready commit suggestion.
- Moved managed spell-check dictionaries to one application-owned data
  directory and non-destructively migrate valid dictionaries from legacy
  package or custom locations before Qt WebEngine starts. Package catalogs
  remain in place only when a matching manifest proves they are complete;
  partial catalogs use the managed store, provision only the system-language
  dictionary, and leave every other download user-driven.
- Adopted versioned development cycles so new work identifies itself with the
  next numeric version while release builds retain the version being published.
- Allowed the documentation validator to verify both an active development
  cycle and the documented closed-release state used for publication.

### Fixed

- Kept WhatsApp voice and video call pop-ups inside authenticated ZapZap
  windows while continuing to hand external links to the default browser and
  cleaning every temporary or internal WebEngine page. Page-requested closure
  now closes the native popup, while unsafe manual closure is blocked with clear
  guidance to use WhatsApp's End call action.
- Selected the native Qt display backend automatically on Linux, using Wayland
  for Wayland sessions and XCB for X11 while preserving explicit environment,
  command-line, user fallback, and Flatpak behavior.
- Restored client-side decorated windows correctly after hiding them with
  Ctrl+W, including their normal, maximized, or fullscreen state.
- Matched the client-side Adwaita close button to the neutral gray
  window-control palette instead of displaying it in red on GNOME.

### Removed

- Removed bundled Qt WebEngine dictionaries from AppImage and Snap and the
  inherited dictionary directory from Flatpak; official packages now provision
  the system language into writable data and leave other downloads to the user.
- Removed the experimental desktop-sharing picker after Wayland portal and
  PipeWire sessions caused unbounded memory growth; the existing WebEngine
  permission flow remains unchanged while the integration is redesigned.

## [7.4.2] - 2026-08-14

### Fixed

- Prevented invalid HTTP cache limits from stopping startup by repairing stored
  values and falling back to Qt's automatic cache management.
- Prevented malformed Qt-facing settings from aborting startup or account
  loading by repairing scale, window state, cache type, tray theme, zoom,
  spellcheck, proxy, theme, and download parameters with scoped fallbacks.
- Kept failed proxy changes pending with visible feedback while preserving the
  previously active proxy, and isolated a failed WebEngine profile so other
  accounts can still load and the failed account can be retried.
- Connected the persistent-cookies preference to each WebEngine profile and
  migrated the JavaScript memory-limit selector to the startup flag while
  keeping its legacy key synchronized.

### Added

- Added a sidebar shortcut for WhatsApp Web's native app lock, keeping lock
  setup and authentication entirely inside WhatsApp.
- Added this changelog as the mandatory source of truth for all project changes
  and additions.
- Added strict proxy isolation for explicit HTTP and SOCKS5 proxies, using
  Chromium's native policy to block non-proxied WebRTC UDP after restart.

### Changed

- Applied the global proxy before any functional WebEngine profile is created
  and kept proxy failures fail-closed without a direct-connection fallback.

### Removed

- Removed misleading per-account proxy settings and proxy changes during
  account switching; all accounts now use the single global proxy.

## [7.4.1] - 2026-08-12

### Added

- Added an update indicator with release details and quick access to release
  notes and downloads.

### Changed

- Improved reliability when ZapZap is closed by the operating system.
- Included performance improvements.

[7.4.4]: https://github.com/rafatosta/zapzap/compare/7.4.3...HEAD
[7.4.3]: https://github.com/rafatosta/zapzap/compare/7.4.2...7.4.3
[7.4.2]: https://github.com/rafatosta/zapzap/compare/7.4.1...7.4.2
[7.4.1]: https://github.com/rafatosta/zapzap/releases/tag/7.4.1
