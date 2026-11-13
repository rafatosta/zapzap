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
- Linux packages and native Windows x86_64 and ARM64 executable builds.


## Supported platforms

| Platform | Package |
|----------|---------|
| Linux | Flatpak (recommended) |
| Linux | AppImage (x86_64, aarch64) |
| Debian / Ubuntu | DEB |
| Linux | Snap |
| Fedora | COPR |
| Windows | EXE (x86_64, ARM64) |
| Developers | Python Wheel (`.whl`) |

## Installation

| Platform | Installation |
|----------|--------------|
| Flatpak | https://flathub.org/apps/com.rtosta.zapzap |
| AppImage, DEB, Windows | https://github.com/rafatosta/zapzap/releases |
| Snap | https://snapcraft.io/zapzap |
| Fedora (COPR) | https://copr.fedorainfracloud.org/coprs/rafatosta/zapzap |
| Python | `pip install zapzap` |

## Codec support

WhatsApp Web needs H.264 video and AAC audio. Whether those work depends on the
Qt WebEngine build shipped with the package, not on ZapZap itself:

| Package | Qt WebEngine | H.264 / AAC |
|---------|--------------|-------------|
| Flatpak | bundled runtime | included |
| AppImage | bundled Qt | included |
| DEB (Debian / Ubuntu) | distribution package | usually **not** included; Debian builds Qt WebEngine without proprietary codecs |
| RPM / Fedora COPR | distribution package | depends on the distribution build |
| Snap | bundled runtime | check the runtime information below |
| Windows, macOS | bundled | included |

Open **Settings → Report a problem → Runtime information** to see what the
running engine advertises. The `media_codecs` block reports `h264` and `aac`
through `canPlayType` and Media Source Extensions, and the same block is
included in problem reports. An unsupported codec explains silent or missing
chat media; it cannot be fixed by changing a ZapZap setting, because the
package must ship a Qt WebEngine built with proprietary codecs. On Debian and
Ubuntu the AppImage or the Flatpak are the packages that include them.

Videos can also be silent while everything else is audible when the global mute
is active (the speaker button in the toolbar, the tray menu or the floating
panel). Video and audio playback on ARM64 Linux usually uses software decoding,
so very high-resolution files may stutter even when the codecs are present;
that is a performance limit, not a missing codec.

## Donations

ZapZap is a free and open-source project maintained in my spare time. If you find it useful, consider supporting its continued development through one of the following methods:

| Method | Details |
|--------|---------|
| GitHub Sponsors | https://github.com/sponsors/rafatosta |
| Ko-fi | https://ko-fi.com/rafaeltosta |
| PayPal | https://www.paypal.com/donate/?business=E7R4BVR45GRC2 |
| Wise | https://wise.com/pay/me/rafaelt2487 |
| Pix (Brazil) | https://nubank.com.br/pagar/3c3r2/LS2hiJJKzv |

Every contribution helps keep ZapZap free, maintained, and continuously improving. ❤️

## Development and maintenance

Architecture, maintenance procedures and automated-test instructions are
available in the [technical documentation](docs/README.md).
All project changes and additions are recorded in the
[changelog](CHANGELOG.md).

## License
ZapZap is licensed under the GNU General Public License v3.0 or later. See [LICENSE](LICENSE) for the full license text.
