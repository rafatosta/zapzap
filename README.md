# ZapZap - Whatsapp Desktop for Linux 
WhatsApp desktop application written in Pyqt6 + PyQt6-WebEngine.

<p align="center">
    <a href="https://flathub.org/apps/details/com.rtosta.zapzap">
        <img  alt="Download on Flathub" src="https://flathub.org/assets/badges/flathub-badge-en.png" width="150">
    </a>
</p>

![Zapzap for whatsapp](share/screenshot/default.png)

# Donations
<p align="center">
    <a href="https://www.paypal.com/donate/?business=E7R4BVR45GRC2&no_recurring=0&item_name=ZapZap+-+Whatsapp+Desktop+for+linux%0AAn+unofficial+WhatsApp+desktop+application+written+in+Pyqt6+%2B+PyQt6-WebEngine.&currency_code=USD">
        <img alt="Donate" src="share/logos/PayPal.png" width="150">
    </a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://nubank.com.br/pagar/3c3r2/jAK5S45kuO">
        <img  alt="Pix" src="share/logos/pix.png" width="120">
    </a>
</p>

# Features
- Features come with Whatsapp web
- Icon in systray changes if there are new messages
- Customizable Systray icons
- System style (light and dark)
- Fullscreen mode
- Background running
- Spellchecker
- Drag and drop
- Work area notifications
- Personalized window decoration
- Shortcuts for the main options

# Contribute

If you want to help make ZapZap better the easiest thing you can do is to [report issues and feature requests](https://github.com/rafatosta/zapzap/issues).

# Translation
Translations are supported, so just send a zapzap.po file with your translations.
The model file can be found here: [zapzap.pot](zapzap/po/zapzap.pot)

# Development
### Dependencies
- Python >= 3.9

## Local Development

#### Installing dependencies
```bash
pip install PyQt6 PyQt6-WebEngine
```
#### Running the application
```bash
git clone https://github.com/rafatosta/zapzap.git
cd zapzap
# Building (.ui,.po) and Running
python run.py
```

## Flatpak Development

#### Installing dependencies

```bash
# add flathub remote
flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# installing required packages
flatpak install --user --assumeyes flathub org.kde.Platform//6.3 com.riverbankcomputing.PyQt.BaseApp//6.3
```
#### Building and running the application

```bash
# Building and Running
python run_flatpak.py
```

# Contact
Maintainer: Rafael Tosta<br/>
Email: *rafa.ecomp@gmail.com*<br/>
Telegram: *@RafaelTosta*<br/>