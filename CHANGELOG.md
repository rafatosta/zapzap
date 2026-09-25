# Changelog

All changes and additions to ZapZap are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/).
Every pull request or commit that changes the repository must add or update an
entry under the version currently marked `In development`, including internal,
documentation, test, packaging, and workflow changes.

This mandatory record starts after version 7.4.1. The 7.4.1 entry below is the
historical baseline; older release summaries remain available in the GitHub
releases and the AppStream metadata.

## [7.5] - In development

### Added

- Added a compact floating account button in the top-left corner of the
  browser content area, shown only while the sidebar is hidden. It mirrors the
  active account's avatar, stays anchored on window resize, and opens the
  existing account grid switcher on click, without duplicating any account
  management logic. The button can also be moved by clicking and holding the
  left mouse button; ordinary clicks continue to open the account switcher.
- Added shared recent-download menus to the sidebar and right side of the
  menubar, including native platform file-type icons, per-item progress bars
  and percentages, queued/paused/interrupted/cancelled/blocked/completed
  states, pause/resume/cancel controls, per-item folder access, history
  clearing, the downloads-folder shortcut, localized labels, and a five-second
  automatic popup after direct downloads. File icons are resolved through Qt's
  native file-icon provider on Linux, Windows and macOS, with MIME-theme and
  generic-system fallbacks rather than bundled type artwork.
- Added Chrome-style repeated-download protection for WhatsApp: only the first
  download request in an application session is implicitly allowed; every
  later request requires the shared ask/allow/block permission, so spacing
  automated requests apart cannot bypass the prompt. Remembered decisions can
  be reset in Settings, and a global cap of six active WhatsApp downloads
  queues excess requests. Paused transfers do not occupy an active slot.
- Added download behavior preferences for preserving the existing confirmation
  dialog, saving directly to the selected folder, or asking for a destination
  every time, plus independent opt-in automatic opening for completed PDFs and
  raster images with the system default applications. Both auto-open switches
  remain disabled by default and require verified file content, a compatible
  safe extension and no conflicting server MIME type. Download names and final
  target paths are sanitized/canonicalized to prevent directory traversal and
  symlink escape.
- Refined the download experience with a Chrome-style two-level downloads UI:
  the sidebar and menubar buttons open a compact dropdown limited to the five
  most recent items, while its footer opens a separate small, vertically
  scrollable history window retaining up to 100 recent/session records.
  Hovering a finished row reveals outline-only palette-aware folder and trash
  actions; the trash deletes the downloaded file from disk while keeping its
  history record. Right-click menus expose state-appropriate actions including
  pause/resume/cancel, show-in-folder, delete-file and remove-from-history.
  Active transfers expose a right-side X that cancels into the Cancelled state.
  The history window footer uses icon-only clear-history, downloads-folder and a
  true gear-shaped download-settings shortcut. Active rows show percentage,
  smoothed current
  transfer speed and estimated time remaining. The download button no longer
  overlays a percentage; a proportional circular progress ring is drawn around
  the icon only while the estimated remaining time is greater than five seconds,
  without resizing the button or icon.
- Kept download presentation stable during fast transfers: unstarted requests
  dismissed from the save dialog no longer appear as cancelled, terminal states
  retain their original request position, and long names are middle-elided while
  preserving the extension. PDF, image and other file-type artwork now prefers
  the current desktop MIME icon theme before falling back to Qt's native generic
  file provider.
- Added a Linux/Windows/macOS quality matrix for download and tray regression
  coverage so queueing, path hardening, settings, MIME validation, native file
  presentation and tray interaction behavior are exercised on maintained
  desktop operating systems.
- Changed tray activation to respect each desktop's native contract. On
  Windows/macOS and tray backends that report primary activation, a primary
  click toggles the application window and a context/right click opens the
  menu. Linux StatusNotifier/AppIndicator keeps its native context menu because
  GNOME-style hosts may consume primary/context clicks themselves; when those
  hosts emit their Activate event as Qt Trigger or DoubleClick, ZapZap toggles
  the window without opening a second application-side menu.
- Show native taskbar/dock unread badges on supported Qt platforms, following
  the existing unread-counter preference. Added regression coverage and
  documented the integration and manual validation.
- Remembered, in memory only and for the currently open conversation, the last
  directory picked with a download's "Save as", suggesting it as the initial
  directory for the next downloads of the same conversation; plain "Save"
  keeps its default behavior and does not update this state. The state is
  discarded when the conversation closes, the window closes, or the app
  quits, and never touches the persisted global download directory.
- Added a structured graphics/runtime diagnostic snapshot to the project
  reporting flow, with allowlisted environment data and explicit handling for
  missing GPU, VAAPI, Vulkan, and Flatpak metadata so the report stays robust
  on unsupported or minimal Linux systems.

### Fixed

- Avoided accessing the optional Qt NativeGesture event enum when it is not
  exposed by older distribution PyQt6 builds, preventing startup failures on
  those systems while keeping gesture handling enabled where supported.
- Prevented links opened from an internal WhatsApp popup, such as a call
  window, from crashing Qt WebEngine by deferring the popup disposal until
  after its navigation request has been processed. Closing the window from
  inside the navigation callback hid its view and made Chromium discard the
  web contents of the navigation still in flight.
- Prevented a popup whose internal window cannot be created during shutdown
  from stopping its page inside the same navigation callback.
- Logged why the Freedesktop notification backend is unavailable instead of
  disabling desktop notifications silently. The three early returns of the
  D-Bus connection setup (no session bus, `org.freedesktop.Notifications` not
  registered, signal subscription failure), the runtime `Notify` and
  `CloseNotification` failures, and the facade fallback to no backend now emit
  a warning; the notification sound kept playing from the WhatsApp Web page,
  so the missing balloons looked like a desktop problem. Added regression
  coverage and documented the manual validation.

### Changed

- Extended the internal popup and external link regression tests to cover the
  deferred disposal and the shutdown path that still stopped a page
  reentrantly.
- Expanded the runtime diagnostics report with a privacy-safe graphics section
  covering the active Qt session, GPU topology, VAAPI and Vulkan hints, Flatpak
  metadata, and the effective Chromium flags assembled for the app. The
  structured data is kept in the same report builder and Markdown flow without
  broadening the runtime surface or enabling automatic workarounds.

## [7.4.5] - 2026-09-23

### Added

- Show native taskbar/dock unread badges on supported Qt platforms, following
  the existing unread-counter preference. Added regression coverage and
  documented the integration and manual validation.
- Remembered, in memory only and for the currently open conversation, the last
  directory picked with a download's "Save as", suggesting it as the initial
  directory for the next downloads of the same conversation; plain "Save"
  keeps its default behavior and does not update this state. The state is
  discarded when the conversation closes, the window closes, or the app quits,
  and never touches the persisted global download directory.
- Added a structured graphics/runtime diagnostic snapshot to the project
  reporting flow, with allowlisted environment data and explicit handling for
  missing GPU, VAAPI, Vulkan, and Flatpak metadata so the report stays robust
  on unsupported or minimal Linux systems.

### Fixed

- Prevented links opened from an internal WhatsApp popup, such as a call
  window, from crashing Qt WebEngine by deferring the popup disposal until
  after its navigation request has been processed. Closing the window from
  inside the navigation callback hid its view and made Chromium discard the
  web contents of the navigation still in flight.
- Prevented a popup whose internal window cannot be created during shutdown
  from stopping its page inside the same navigation callback.
- Logged why the Freedesktop notification backend is unavailable instead of
  disabling desktop notifications silently. The three early returns of the
  D-Bus connection setup, runtime notification failures, and the facade
  fallback to no backend now emit a warning; the notification sound kept
  playing from the WhatsApp Web page, so missing balloons looked like a
  desktop problem. Added regression coverage and documented the manual
  validation.

### Changed

- Extended the internal popup and external link regression tests to cover the
  deferred disposal and the shutdown path that still stopped a page
  reentrantly.
- Expanded the runtime diagnostics report with a privacy-safe graphics
  section covering the active Qt session, GPU topology, VAAPI and Vulkan
  hints, Flatpak metadata, and the effective Chromium flags assembled for the
  app. The structured data is kept in the same report builder and Markdown
  flow without broadening the runtime surface or enabling automatic
  workarounds.

## [7.4.4] - 2026-09-01

### Added

- Added a read-only clipboard diagnostics collector for reproducing browser,
  LibreOffice, and desktop clipboard interoperability problems without storing
  clipboard payload contents.

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

[7.5]: https://github.com/rafatosta/zapzap/compare/7.4.5...HEAD
[7.4.5]: https://github.com/rafatosta/zapzap/compare/7.4.4...7.4.5
[7.4.4]: https://github.com/rafatosta/zapzap/compare/7.4.3...7.4.4
[7.4.3]: https://github.com/rafatosta/zapzap/compare/7.4.2...7.4.3
[7.4.2]: https://github.com/rafatosta/zapzap/compare/7.4.1...7.4.2
[7.4.1]: https://github.com/rafatosta/zapzap/releases/tag/7.4.1
