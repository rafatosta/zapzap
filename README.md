# ZapZap - Whatsapp Desktop para linux
    Unofficial WebApp for WhatsApp Web created in PyQt6
    
    - O PySide6 foi só dor de cabeça para empacotar em Flatpak 

# Ainda não tive tempo nem paciência para fazer um Readme de responsa
    Sua contribuição será muito bem vinda!!! =D

# Se deseja executar em sua máquina
### Instale os seguintes pacotes e execute o __main__.py ou python zapzap dentro da pasta raíz 
- pip install PyQt6
- pip install PyQt6-WebEngine

# Flatpak
    - Install a runtime and the matching SDK
        - flatpak install flathub org.kde.Platform//6.2 org.kde.Sdk//6.2 io.qt.qtwebengine.BaseApp//6.2
    - Building and install
        - flatpak-builder build com.rtosta.zapzap.yaml --force-clean --ccache --install --user
    - Bem resumido, mas já dará para utilizá-lo
    - Se tudo ocorreu bem, o app do ZapZap deverá aparecer na sua lista.

## Obs.: Em caso de Fork não esqueça de alterar o link do seu github em com.rtosta.zapzap.yaml (espera-se que saiba o que está fazendo, caso contrário entre em contato. Toda ajuda será bem vinda! =D)

### Contact
Maintainer: Rafael Tosta<br/>
E-Mail: *rafa.ecomp@gmail.com*<br/>
Telegram: *@RafaelTosta*<br/>





