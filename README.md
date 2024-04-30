# [ZapZap](https://zapzap-linux.github.io/) - Whatsapp Desktop for Linux 
![Zapzap for whatsapp](share/screenshot/default.png)

# About
This app aims to bring the WhatsApp experience on Linux closer to a native application.

Because Meta does not provide the public with an API to construct third-party applications around, so ZapZap is a [Progressive Web Application](https://en.wikipedia.org/wiki/Progressive_web_app).

# Download
<p align="center">
    <a href="https://flathub.org/apps/details/com.rtosta.zapzap">
        <img  alt="Download on Flathub" src="https://flathub.org/assets/badges/flathub-badge-en.png" width="150">
    </a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://copr.fedorainfracloud.org/coprs/rafatosta/zapzap/">
        <img  alt="Download Fedora Copr" src="https://redhat.discourse-cdn.com/fedoraproject/original/1X/c5f38bdccf3bed038510138b9dc16b3bf01b6e13.png" width="150" height='50'>
    </a>
</p>

# Features
Besides all the features that come with the WhatsApp web application, ZapZap provides:
1. **Looks**
   - Adaptive light and dark mode
   - Fullscreen mode
   - Personalized window decoration
2. **Usability**
   - Shortcuts for the main options
   - Adaptive Systray icon (it changes when there are new messages)
   - A background process
   - Drag and drop support
   - Work area notifications  <!-- what is this?? -->
3. **Additional features**
   - Spellchecker
   - Customizable Systray icons

# Development
WhatsApp desktop application written in Pyqt6 + PyQt6-WebEngine.

- [Build and execute locally](/_run/README.md)

## Packaging
- [Fecora Copr](/_packaging/fedora/zapzap.spec)
- [Flatpak](/_packaging/flatpak/README.md)

## Translation
The translations are supported.

Make sure the file for your language is in the [po](/po) folder. If it is just send a pull request with the updated file, otherwise open a [issue](https://github.com/zapzap-linux/zapzap/issues) requesting inclusion.

# Donations
<p align="center">
    <a href="https://www.paypal.com/donate/?business=E7R4BVR45GRC2&no_recurring=0&item_name=ZapZap+-+Whatsapp+Desktop+for+linux%0AAn+unofficial+WhatsApp+desktop+application+written+in+Pyqt6+%2B+PyQt6-WebEngine.&currency_code=USD">
        <img alt="Donate" src="share/logos/PayPal.svg" width="170">
    </a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://nubank.com.br/pagar/3c3r2/LS2hiJJKzv">
        <img  alt="Pix" src="share/logos/pix.png" width="120">
    </a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://ko-fi.com/X8X2E1OLG">
        <img  alt="Ko-fi" src="https://ko-fi.com/img/githubbutton_sm.svg" width="350">
    </a>
</p>

# Contact
Maintainer: Rafael Tosta<br/>
Email: *rafa.ecomp@gmail.com*<br/>
