import os
import sys


def dev(build_translations=False):
    """Run the app in development mode."""
    print(f"Running in dev mode. Translations: {build_translations}")
    
    print(" # === Build the windows from the .ui file ===")
    os.system("chmod +x ./_scripts/build-windows.sh")
    os.system("./_scripts/build-windows.sh")

    

    if build_translations:
        print("# === Build translations ===")
        os.system("./_scripts/build-translations.sh")

    print("# === Start === ")
    os.system("python -m zapzap")


def preview(build_translations=False):
    """Run the app in preview mode."""
    SDK_VERSION = 6.8

    print("Starting app in preview mode...")

    print(" # === Build the windows from the .ui file ===")
    os.system("chmod +x ./_scripts/build-windows.sh")
    os.system("./_scripts/build-windows.sh")

    if build_translations:
        print("# === Build translations ===")
        os.system("./_scripts/build-translations.sh")

    print("Add flathub remote")
    os.system(
        "flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo"
    )
    print("# === Install SDK === ")
    os.system(
        f"flatpak install --user --assumeyes flathub "
        f"org.kde.Platform//{SDK_VERSION} org.kde.Sdk//{SDK_VERSION} "
        f"com.riverbankcomputing.PyQt.BaseApp//{SDK_VERSION}"
    )
    print("# === Build === ")
    os.system(
        "flatpak-builder build com.rtosta.zapzap.yaml --force-clean --ccache --install --user"
    )
    print("# === Start === ")
    os.system("flatpak run com.rtosta.zapzap")


def build():
    build_appimage = "--appimage" in sys.argv
    build_flatpak = "--flatpak-onefile" in sys.argv
    
    if build_appimage:
        print("Building AppImage...")
        os.system("./_scripts/build-appimage.sh")

    if build_flatpak:
        print("Building Flatpak Onefile...")
    
    if not build_appimage and not build_flatpak:
        print("No build target specified. Use --appimage or --flatpak-onefile.")


def main():
    """Main entry point for the script."""
    commands = {
        "dev": dev,
        "preview": preview,
        "build": build,
    }

    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print("Usage: python run.py [dev|preview|build] [--build-translations | --appimage | --flatpak-onefile]")
        return

    build_translations = "--build-translations" in sys.argv
    if sys.argv[1] == "dev":
        dev(build_translations)
    else:
        commands[sys.argv[1]]()


if __name__ == "__main__":
    main()


"""
Exemplo de uso:
Sem build das traduções: python run.py dev
Com build traduções: python run.py dev --build-translations


Obs.: Ao construir os arquivos das traduções, a data e hora são atualizadas.
"""