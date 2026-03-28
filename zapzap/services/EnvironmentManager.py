import os
import sys
from enum import Enum


class Packaging(Enum):
    APPIMAGE = "AppImage"
    FLATPAK = "Flatpak"
    RPM = "RPM"
    UNOFFICIAL = "Unofficial"


class EnvironmentManager:
    @staticmethod
    def identify_packaging():
        """Identifies the packaging type of the application and returns an Enum."""

        if "APPIMAGE" in os.environ:
            return Packaging.APPIMAGE
        elif "FLATPAK_ID" in os.environ:
            return Packaging.FLATPAK

        # Identification via executable path
        app_path = os.path.abspath(sys.argv[0])

        if app_path.startswith("/usr/bin/") or app_path.startswith("/usr/local/bin/"):
            return Packaging.RPM  # Assuming it's an RPM package

        return Packaging.UNOFFICIAL

    @staticmethod
    def show_information():
        """Displays information about the identified packaging."""
        packaging = EnvironmentManager.identify_packaging()
        print(f"Empacotamento identificado: {packaging.value}")

        if packaging == Packaging.APPIMAGE:
            appdir = os.getenv("APPDIR", "")
            if appdir:
                print(f"Diretório do AppImage: {appdir}")
                print(f"Arquivos no diretório: {os.listdir(appdir)}")

    @staticmethod
    def isOfficial() -> bool:
        if EnvironmentManager.identify_packaging() == Packaging.UNOFFICIAL:
            return False

        return True
