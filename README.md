# ZapZap

ZapZap is an unofficial WhatsApp Web desktop client built with Python, PyQt6 and
QtWebEngine. It wraps `https://web.whatsapp.com/` in a desktop application and adds
native integration for accounts, notifications, tray behavior, theming and packaging.

![ZapZap main window](share/screenshot/default.png)

## Key features

- WhatsApp Web in a native PyQt6 desktop window.
- Multiple account profiles with isolated web sessions.
- System tray integration and desktop notifications.
- Light, dark and system theme handling.
- Custom CSS and JavaScript injection, globally or per account.
- Spell checking through QtWebEngine dictionaries.
- Download handling with configurable download behavior.
- Linux packages and Windows executable build support.

## Supported platforms

| Platform | Status in repository | Primary packaging files |
| --- | --- | --- |
| Linux | Supported | `com.rtosta.zapzap.yaml`, `builders/`, `com.rtosta.zapzap.spec` |
| Windows | Build support | `builders/windows_builder.py` |

ZapZap depends on QtWebEngine and the behavior can vary by display server, sandbox and
package format. See [Troubleshooting](docs/troubleshooting.md) for known environment
considerations.

## Installation

Use the installation guide for package-specific instructions and links:

- [Installation guide](docs/installation.md)
- [Latest GitHub releases](https://github.com/rafatosta/zapzap/releases)
- [Flathub package](https://flathub.org/apps/details/com.rtosta.zapzap)

## Documentation

- [Installation](docs/installation.md)
- [Development](docs/development.md)
- [Packaging](docs/packaging.md)
- [Project philosophy](docs/philosophy.md)
- [FAQ](docs/faq.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Release process](docs/release-process.md)
- [Technical documentation](docs/technical-documentation.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)

## Donations

If ZapZap is useful to you, you can support the maintainer through the project donation
links:

- [Project donation page](https://rtosta.com/zapzap/#donate)
- [Pix](https://nubank.com.br/pagar/3c3r2/LS2hiJJKzv)
- [Ko-fi](https://ko-fi.com/rafaeltosta)
- [GitHub Sponsors](https://github.com/sponsors/rafatosta)

## Contributing

Contributions are welcome. Before opening a pull request, read the
[contribution guide](CONTRIBUTING.md) and test the affected workflow locally.

## License

ZapZap is licensed under the GNU General Public License v3.0 or later. See
[LICENSE](LICENSE) for the full license text.

## Related documentation

- [Installation](docs/installation.md)
- [Development](docs/development.md)
- [Contributing](CONTRIBUTING.md)
