import os

os.system('flatpak-builder build _packaging/flatpak/com.rtosta.zapzap.yaml --force-clean --ccache --install --user')

os.system('flatpak run com.rtosta.zapzap')
