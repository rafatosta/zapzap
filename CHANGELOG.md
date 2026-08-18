# Changelog

All changes and additions to ZapZap are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/).
Every pull request or commit that changes the repository must add or update an
entry under the version currently marked `In development`, including internal,
documentation, test, packaging, and workflow changes.

This mandatory record starts after version 7.4.1. The 7.4.1 entry below is the
historical baseline; older release summaries remain available in the GitHub
releases and the AppStream metadata.

## [7.4.3] - In development

### Added

- Added a cross-platform Qt WebEngine dictionary manager with verified
  downloads from the official catalog, offline cache, local imports, removal,
  progress, cancellation, search, filters, and accessible active-language
  management.

### Changed

- Moved spell-check dictionaries to one application-owned data directory and
  non-destructively migrate valid dictionaries from legacy package or custom
  locations before Qt WebEngine starts.
- Adopted versioned development cycles so new work identifies itself with the
  next numeric version while release builds retain the version being published.

### Removed

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

[7.4.3]: https://github.com/rafatosta/zapzap/compare/7.4.2...HEAD
[7.4.2]: https://github.com/rafatosta/zapzap/compare/7.4.1...7.4.2
[7.4.1]: https://github.com/rafatosta/zapzap/releases/tag/7.4.1
