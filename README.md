# [ZapZap](https://rtosta.com/zapzap-web/) – WhatsApp Desktop for Linux
![ZapZap for WhatsApp](share/screenshot/default.png)

## 📌 About

ZapZap brings the WhatsApp experience on Linux closer to that of a native application.  
Since Meta does not provide a public API for third-party applications, ZapZap is developed as a [Progressive Web Application (PWA)](https://en.wikipedia.org/wiki/Progressive_web_app), built with **PyQt6 + PyQt6-WebEngine**.


📌 About notifications and icons on Flatpak: 
See [docs/notifications.md](docs/notifications.md)

---

## 📥 Download

- **[Flathub](https://flathub.org/apps/details/com.rtosta.zapzap)**  
- **[AppImage](https://github.com/rafatosta/zapzap/releases/latest/download/ZapZap-x86_64.AppImage)**

---

## ✨ Features

ZapZap extends WhatsApp Web with additional features:

### 🎨 Appearance
- Adaptive **light and dark mode**
- **Fullscreen mode**
- Custom **window decorations**
- **Interface scaling adjustment** (ideal for 2K/4K screens)

### ⚡ Usability
- **Keyboard shortcuts** for main options
- Adaptive **system tray icon** (notifies new messages)
- **Background process** support
- **Drag-and-drop** functionality
- Ability to select a **custom folder for downloads**
- **Temporary folder** for opening files

### 🛠️ Extras
- **Spellchecker** with language selection via context menu
- Customizable **system tray icons**
- Option to choose a **folder for custom dictionaries**
- Setting to **disable the native file selection dialog** (Hyprland)
- **Custom CSS/JS** with global + per-account override
- **Reorganized Settings Panel**
- Added **Performance section**

### 🧩 Customizations
- New **Customizations** page in Settings
- Supports **Global** customization and **Current account** customization
- Account mode supports **inherit global settings** + optional override
- Users can:
  - import `.css` and `.js` files
  - create and edit CSS/JavaScript files in dialogs
  - enable/disable each imported CSS/JS file independently
  - import CSS/JavaScript from any `https://` URL
  - open customization folders directly
- Supports many userstyle files (`.user.css`) by extracting WhatsApp-targeted `@-moz-document` blocks
- Page actions: `Save`, `Save and reload`, `Reload`

Customization files are stored in the app local data path under:
- `customizations/global/css`
- `customizations/global/js`
- `customizations/accounts/<id>/css`
- `customizations/accounts/<id>/js`

Reserved for future extension support:
- `customizations/extensions`

---

# ⚙️ Development

## Requirements

-   **Python 3.9 or higher**



## Fedora 43 System Dependencies

If `pip install -r requirements.txt` fails due to `dbus-python`:

``` bash
sudo dnf install -y dbus-devel pkg-config gcc python3-devel
```

Then:

``` bash
pip install -r requirements.txt
```



# 🚀 Running ZapZap

``` bash
python run.py [dev|preview|build] [options]
```



## 🔧 Development Mode

Without translations:

``` bash
python run.py dev
```

With translations:

``` bash
python run.py dev --build-translations
```

#### Debugging WebEngine
- Open DevTools for current account page: `View -> Open DevTools` (`Ctrl+Shift+I`)


## 👀 Preview Mode

Flatpak:

``` bash
python run.py preview --flatpak
```

AppImage:

``` bash
python run.py preview --appimage
```

With translations:

``` bash
python run.py preview --build-translations --flatpak 
```



## 📦 Build AppImage

``` bash
python run.py build --appimage <version>
```

Example:

``` bash
python run.py build --appimage 6.0
```



## 📦 Build Flatpak Onefile

``` bash
python run.py build --flatpak-onefile
```

Output:

    dist/com.rtosta.zapzap.flatpak



## 📦 Install as Python Module

``` bash
pip install .
```

### Uninstall

``` bash
pip uninstall zapzap
```



## 🔧 uv Tool

``` bash
uv tool install . --with-requirements requirements.txt
```

## 📦 Packaging
- **[Flatpak](https://github.com/flathub/com.rtosta.zapzap)**
- **[AppImage](_scripts/build-appimage.sh)**

## 🌍 Translation
ZapZap supports translations. If your language file is missing from the [po](/po) folder, submit a pull request or open an [issue](https://github.com/rafatosta/zapzap/issues).

## 🤝 Contributions
Contributions are welcome!
Please submit a pull request with any improvements or changes you wish to propose.

## 📜 License
This project is licensed under the GPL.
See the LICENSE file for more information.

## 💖 Donations
**PayPal:** [Donate via PayPal](https://www.paypal.com/donate/?business=E7R4BVR45GRC2&no_recurring=0&item_name=ZapZap+-+Whatsapp+Desktop+for+linux%0AAn+unofficial+WhatsApp+desktop+application+written+in+Pyqt6+%2B+PyQt6-WebEngine.&currency_code=USD) 

**Pix:** [Donate via Pix](https://nubank.com.br/pagar/3c3r2/LS2hiJJKzv) 

**Ko-fi:** [Donate via Ko-fi](https://ko-fi.com/X8X2E1OLG)

## 📬 Contact
**Maintainer:** Rafael Tosta 

**Email:** [rafa.ecomp@gmail.com](mailto:rafa.ecomp@gmail.com)
