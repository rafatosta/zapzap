# [ZapZap](https://rtosta.com/zapzap/) – WhatsApp Web Desktop Client

ZapZap is an unofficial WhatsApp Web desktop client built with Python, PyQt6 and QtWebEngine. It wraps `https://web.whatsapp.com/` in a desktop application and adds native integration for accounts, notifications, tray behavior, theming and packaging.

## Why ZapZap?

| Feature | WhatsApp Web | ZapZap |
|---------|:------------:|:------:|
| Runs in your default browser | ✅ | ❌ |
| Standalone desktop application | ❌ | ✅ |
| Multiple accounts | ❌ | ✅ |
| Native system tray integration | ❌ | ✅ |
| Native desktop notifications | Limited | ✅ |
| Linux package manager support | ❌ | ✅ |
| Flatpak package | ❌ | ✅ |
| AppImage package | ❌ | ✅ |
| Snap package | ❌ | ✅ |
| Native DEB package | ❌ | ✅ |
| Fedora COPR repository | ❌ | ✅ |
| Automatic AppImage updates (`.zsync`) | ❌ | ✅ |
| Spell checking | Browser dependent | ✅ |
| Custom CSS & JavaScript | ❌ | ✅ |
| Open source (GPL-3.0) | ❌ | ✅ |
| Privacy | Browser session | Dedicated desktop application |


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

| Platform | Package |
|----------|---------|
| Linux | Flatpak (recommended) |
| Linux | AppImage (x86_64, aarch64) |
| Debian / Ubuntu | DEB |
| Linux | Snap |
| Fedora | COPR |
| Windows | EXE Installer |
| Developers | Python Wheel (`.whl`) |

## Installation

| Platform | Installation |
|----------|--------------|
| Flatpak | https://flathub.org/apps/com.rtosta.zapzap |
| AppImage, DEB, Windows | https://github.com/rafatosta/zapzap/releases |
| Snap | https://snapcraft.io/zapzap |
| Fedora (COPR) | https://copr.fedorainfracloud.org/coprs/rafatosta/zapzap |
| Python | `pip install zapzap` |

## Development and tests

Run the commands below from the repository root after installing the project
dependencies.

### Automated tests

Run the complete test suite:

```bash
python -m unittest discover -s tests -q
```

Run the complete suite with the name and result of every test:

```bash
python -m unittest discover -s tests -v
```

Run only the UI tests:

```bash
python -m unittest discover -s tests -p 'test_*_ui.py' -v
```

Run one test module directly:

```bash
python tests/test_about_settings_ui.py -v
```

The shared Qt test setup automatically:

- uses the local repository instead of an installed ZapZap version;
- selects the Qt `offscreen` platform when no platform was specified;
- keeps a single `QApplication` instance alive;
- stores test data, settings and cache in a temporary directory.

UI tests are automated assertions and do not open an interactive window.

### Static unused-code and package checks

Check for probably unused imports, variables, attributes, methods and classes,
and also compare Python package directories with
`tool.setuptools.packages` in `pyproject.toml`:

```bash
python tests/check_unused_code.py
```

The command returns a non-zero status when it finds candidates. To print the
inventory without failing:

```bash
python tests/check_unused_code.py --no-fail
```

Check only whether packages were added to or removed from
`pyproject.toml` correctly:

```bash
python tests/check_unused_code.py --packages-only
```

## Donations

ZapZap is a free and open-source project maintained in my spare time. If you find it useful, consider supporting its continued development through one of the following methods:

| Method | Details |
|--------|---------|
| GitHub Sponsors | https://github.com/sponsors/rafatosta |
| Ko-fi | https://ko-fi.com/rafaeltosta |
| PayPal | https://www.paypal.com/donate/?business=E7R4BVR45GRC2 |
| Wise | https://wise.com/pay/me/rafaelt2487 |
| Pix (Brazil) | **Pix Key:** `c86378c4-c34a-4951-bad0-42d5c1774f79` |

Every contribution helps keep ZapZap free, maintained, and continuously improving. ❤️

## License
ZapZap is licensed under the GNU General Public License v3.0 or later. See [LICENSE](LICENSE) for the full license text.
