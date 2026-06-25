# Troubleshooting

This page collects common environment issues for a PyQt6 and QtWebEngine desktop client
that embeds WhatsApp Web.

## General troubleshooting

- Start ZapZap from a terminal to capture Python, Qt and QtWebEngine messages.
- Confirm that the same WhatsApp Web account works in a regular browser.
- Check whether the issue is package-specific by testing another available package.
- Review custom CSS and JavaScript changes if only the web content layout is affected.

## Wayland

- Prefer the package default first, because Flatpak and Snap set Qt-related variables.
- If file selection or drag-and-drop fails, review package filesystem permissions.
- If rendering issues appear, compare behavior on an X11 session when possible.

## X11

- Ensure the system has the Qt platform plugin dependencies required by PyQt6.
- If tray icons do not appear, verify that the desktop environment provides a tray or
  StatusNotifier implementation.

## Flatpak permissions

The Flatpak manifest grants access to selected user folders and runtime services. If
file upload fails, adjust permissions with Flatseal or Flatpak overrides.

Example broad user override:

```bash
flatpak override --user --filesystem=home com.rtosta.zapzap
```

Restart ZapZap after changing permissions.

## Snap confinement

The Snap manifest uses strict confinement and declares desktop, Wayland, X11, network,
audio playback and browser-support plugs. If a feature fails only in the Snap package,
check connected interfaces and confinement-related denials.

```bash
snap connections zapzap
```

## Notifications

- Confirm notifications are enabled in ZapZap settings.
- Confirm notifications are enabled in the desktop environment.
- On sandboxed packages, ensure portal or notification permissions are available.
- On non-sandboxed Linux environments, verify Freedesktop notification support.

## File access

File upload, downloads and drag-and-drop depend on both QtWebEngine and package
permissions.

- For Flatpak, grant access to folders that contain files you need to upload.
- For Snap, check interface connections.
- For native packages, verify filesystem permissions and file chooser behavior.

## Graphics acceleration

QtWebEngine uses Chromium components and graphics behavior can vary by GPU, driver,
sandbox and display server.

- Test the same account after restarting the application.
- Compare Wayland and X11 sessions if the desktop supports both.
- For package-specific issues, include the package format in bug reports.

## Related documentation

- [Installation](installation.md)
- [Packaging](packaging.md)
- [FAQ](faq.md)
