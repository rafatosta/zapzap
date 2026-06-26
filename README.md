# [ZapZap](https://rtosta.com/zapzap-web/) – WhatsApp Web Desktop Client

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