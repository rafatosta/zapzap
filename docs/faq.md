# FAQ

This page answers common questions about ZapZap usage, installation and project scope.

## General questions

### Is ZapZap an official WhatsApp client?

No. ZapZap is an unofficial desktop client that embeds WhatsApp Web with PyQt6 and
QtWebEngine.

### Does ZapZap implement the WhatsApp protocol?

No. Messaging functionality is provided by WhatsApp Web at `https://web.whatsapp.com/`.
ZapZap provides the desktop shell and integrations around it.

### Where are technical details documented?

See [Technical documentation](technical-documentation.md).

## Installation

### Which package should I install?

Use the package that matches your platform and distribution preference. The available
repository-supported formats are listed in [Installation](installation.md).

### Why do package behaviors differ?

Sandboxed packages and distribution packages expose different filesystem, notification
and QtWebEngine environments. See [Packaging](packaging.md) and
[Troubleshooting](troubleshooting.md).

## Accounts

### Does ZapZap support multiple accounts?

Yes. The application creates separate web profiles for accounts so sessions can be kept
isolated.

### Does ZapZap store my WhatsApp password?

ZapZap uses WhatsApp Web. Login and session handling are provided by WhatsApp Web and
QtWebEngine profile storage.

## Updates

### Where are releases published?

Releases and downloadable artifacts are published on GitHub when available:

- [GitHub releases](https://github.com/rafatosta/zapzap/releases)

### How is the application version defined?

The source version is defined in `zapzap/__init__.py` as `__version__` and consumed by
Python packaging metadata.

## Security

### Can custom CSS and JavaScript affect my session?

Yes. Custom CSS and JavaScript run in the embedded web context. Only import
customizations from sources you trust.

### Why does file upload need filesystem permissions?

QtWebEngine needs access to selected files so WhatsApp Web can upload them. Sandboxed
packages may require explicit permissions for common user directories.

## Troubleshooting references

- [Troubleshooting](troubleshooting.md)
- [Installation](installation.md)
- [Packaging](packaging.md)

## Related documentation

- [Installation](installation.md)
- [Troubleshooting](troubleshooting.md)
- [Project philosophy](philosophy.md)
