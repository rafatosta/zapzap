# Project philosophy

ZapZap focuses on providing a desktop shell around WhatsApp Web while keeping the scope
aligned with what the existing web service and QtWebEngine integration can support.

## Project goals

- Provide a native desktop experience for WhatsApp Web.
- Integrate with desktop notifications, tray behavior, theming and downloads.
- Support multiple accounts through isolated web profiles.
- Offer packaging paths for common Linux desktop formats and Windows builds.
- Keep user-facing behavior understandable and configurable.

## Design principles

- Use WhatsApp Web as the source of messaging functionality.
- Keep platform integration in services and environment-specific backends.
- Prefer package-specific fixes over global behavior changes when possible.
- Keep user customizations explicit and stored in predictable local paths.
- Document limitations caused by QtWebEngine, sandboxing or display servers.

## Scope

ZapZap includes:

- A PyQt6 desktop window embedding WhatsApp Web.
- Account, theme, notification, tray, download and customization management.
- Build scripts and metadata for the package formats present in the repository.
- Translation source and compiled gettext catalogs.

## Out of scope

ZapZap does not provide:

- A replacement WhatsApp protocol implementation.
- Server-side WhatsApp automation.
- Access to private WhatsApp APIs.
- Message synchronization outside the behavior provided by WhatsApp Web.
- A guarantee that third-party CSS or JavaScript customizations remain compatible with
  future WhatsApp Web changes.

## Compatibility philosophy

Compatibility work prioritizes supported package formats, current QtWebEngine behavior
and the desktop environments that can be validated by maintainers and contributors.
When an issue is caused by sandbox permissions or display-server behavior, the preferred
fix is a documented configuration or package-specific adjustment.

## Related documentation

- [Technical documentation](technical-documentation.md)
- [Troubleshooting](troubleshooting.md)
- [Packaging](packaging.md)
