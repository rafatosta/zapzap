# [ZapZap](https://rtosta.com/zapzap-web/) - WhatsApp Desktop for Linux 
![ZapZap for WhatsApp](share/screenshot/default.png)

## About
ZapZap aims to bring the WhatsApp experience on Linux closer to that of a native application. Since Meta does not provide a public API for third-party applications, ZapZap is developed as a [Progressive Web Application](https://en.wikipedia.org/wiki/Progressive_web_app).

## Download
<p align="center">
    <a href="https://flathub.org/apps/details/com.rtosta.zapzap">
        <img alt="Download on Flathub" src="https://flathub.org/assets/badges/flathub-badge-en.png" width="150">
    </a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://copr.fedorainfracloud.org/coprs/rafatosta/zapzap/">
        <img alt="Download Fedora Copr" src="https://redhat.discourse-cdn.com/fedoraproject/original/1X/c5f38bdccf3bed038510138b9dc16b3bf01b6e13.png" width="150" height="50">
    </a>
</p>

## Features
In addition to all the default features of WhatsApp Web, ZapZap provides:
1. **Looks**
   - Adaptive light and dark mode
   - Fullscreen mode
   - Personalized window decoration
2. **Usability**
   - Shortcuts for main options
   - Adaptive systray icon (changes when there are new messages)
   - Background process
   - Drag and drop support
3. **Additional Features**
   - Spellchecker
   - Customizable systray icons

## Development
ZapZap is a WhatsApp desktop application written in PyQt6 and PyQt6-WebEngine.

- [Build and Execute Locally](/_run/README.md)

### Packaging
- [Fedora Copr](/_packaging/fedora/zapzap.spec)
- [Flatpak](/_packaging/flatpak/README.md)

### Translation
Translations are supported. Ensure the file for your language is in the [po](/po) folder. If it is, submit a pull request with the updated file, otherwise open an [issue](https://github.com/rafatosta/zapzap/issues) requesting inclusion.

## Donations
<p align="center">
    <a href="https://www.paypal.com/donate/?business=E7R4BVR45GRC2&no_recurring=0&item_name=ZapZap+-+Whatsapp+Desktop+for+linux%0AAn+unofficial+WhatsApp+desktop+application+written+in+Pyqt6+%2B+PyQt6-WebEngine.&currency_code=USD">
        <img alt="Donate" src="share/logos/PayPal.svg" width="170">
    </a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://nubank.com.br/pagar/3c3r2/LS2hiJJKzv">
        <img alt="Pix" src="share/logos/pix.png" width="120">
    </a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://ko-fi.com/X8X2E1OLG">
        <img alt="Ko-fi" src="https://ko-fi.com/img/githubbutton_sm.svg" width="350">
    </a>
</p>

## Contact
**Maintainer:** Rafael Tosta<br/>
**Email:** [rafa.ecomp@gmail.com](mailto:rafa.ecomp@gmail.com)
