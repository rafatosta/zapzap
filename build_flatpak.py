import os
# Constroi o Flatpak
os.system('flatpak-builder build _packaging/flatpak/com.rtosta.zapzap.yaml --force-clean --ccache')
# Exporta o resultado para a pasta export
os.system('flatpak build-export export build')
# Cria o arquivo único
os.system('flatpak build-bundle export export/zapzap.flatpak com.rtosta.zapzap')
