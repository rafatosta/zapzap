# [ZapZap](https://rtosta.com/zapzap-web/) - WhatsApp Desktop for Linux
![ZapZap for WhatsApp](share/screenshot/default.png)

## About

ZapZap brings the WhatsApp experience on Linux closer to that of a native application. Since Meta does not provide a public API for third-party applications, ZapZap is developed as a [Progressive Web Application](https://en.wikipedia.org/wiki/Progressive_web_app).

## Download

**Flathub:** [Download through Flathub](https://flathub.org/apps/details/com.rtosta.zapzap)  
**Fedora Copr:** [Download through Fedora Copr](https://copr.fedorainfracloud.org/coprs/rafatosta/zapzap/)

## Features

ZapZap extends WhatsApp Web with additional features:

### **Appearance**

- Adaptive light and dark mode
- Fullscreen mode
- Custom window decorations
- Interface scaling adjustment (ideal for 2K/4K screens)

### **Usability**

- Keyboard shortcuts for main options
- Adaptive system tray icon (notifies new messages)
- Background process support
- Drag-and-drop functionality
- Ability to select a custom folder for downloads
- Temporary folder for opening files

### **Extras**

- Spellchecker with language selection via context menu
- Customizable system tray icons
- Option to choose a folder for custom dictionaries
- Setting to disable the native file selection dialog (Hyprland)
- Reorganized Settings Panel
- Added Performance section

## Development

ZapZap is built using PyQt6 and PyQt6-WebEngine.

### **Build & Run Locally**

- [Instructions](/_run/README.md)

### **Packaging**

- [Fedora Copr](/_packaging/fedora/zapzap.spec)
- [Flatpak](/_packaging/flatpak/README.md)

### **Translation**

ZapZap supports translations. If your language file is missing from the [po](/po) folder, submit a pull request or open an [issue](https://github.com/rafatosta/zapzap/issues).

## Execution

### **Description**

This is a Python application that can be run in three different modes:

- **dev**: Development mode
- **preview**: Preview mode
- **build**: Generates an executable for production (`zapzap.flatpak`)

The project uses `zapzap.toml` to manage dependencies and a Python script (`run.py`) to execute commands.

### **Requirements**

- Python 3.9 or higher

### **Installation**

1. **Clone the repository**

```bash
git clone https://github.com/rafatosta/zapzap.git
cd zapzap
```

2. **Install dependencies**

Then, install the project dependencies:

```bash
pip install -r requirements.txt
```

### **Usage**

Usage: 

```bash
python run.py [dev|preview|build] [--build-translations | --appimage | --flatpak-onefile]
```

The executable will be generated in the `dist/` folder as `zapzap.flatpak`.


## Contributions

Contributions are welcome! Please submit a pull request with any improvements or changes you wish to propose.

## License

This project is licensed under the GPL. See the LICENSE file for more information.

## Donations

**PayPal:** [Donate via PayPal](https://www.paypal.com/donate/?business=E7R4BVR45GRC2&no_recurring=0&item_name=ZapZap+-+Whatsapp+Desktop+for+linux%0AAn+unofficial+WhatsApp+desktop+application+written+in+Pyqt6+%2B+PyQt6-WebEngine.&currency_code=USD)  
**Pix:** [Donate via Pix](https://nubank.com.br/pagar/3c3r2/LS2hiJJKzv)  
**Ko-fi:** [Donate via Ko-fi](https://ko-fi.com/X8X2E1OLG)

## Contact

**Maintainer:** Rafael Tosta  
**Email:** [rafa.ecomp@gmail.com](mailto:rafa.ecomp@gmail.com)

