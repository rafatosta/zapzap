"""
    Building Single-file: Generates a unique file for installation and distribution
"""

import os

# Build flatpak
os.system('flatpak-builder build _packaging/flatpak/com.rtosta.zapzap.yaml --force-clean --ccache')

# Export the result to the 'export' folder
os.system('flatpak build-export export build')


# Create single file
os.system('flatpak build-bundle export export/zapzap.flatpak com.rtosta.zapzap')
