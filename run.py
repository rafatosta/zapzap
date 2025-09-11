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
    extra_args = " ".join(sys.argv[2:])
    os.system(f"python -m zapzap {extra_args}")

def preview(build_translations=False):
    """Run the app in preview mode."""
    SDK_VERSION = 6.8
    use_flatpak = "--flatpak" in sys.argv
    use_appimage = "--appimage" in sys.argv

    print("Starting app in preview mode...")

    print(" # === Build the windows from the .ui file ===")
    os.system("chmod +x ./_scripts/build-windows.sh")
    os.system("./_scripts/build-windows.sh")

    if build_translations:
        print("# === Build translations ===")
        os.system("./_scripts/build-translations.sh")

    if use_flatpak:
        print("# === Running in Flatpak mode ===")
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
        extra_args = " ".join(sys.argv[2:])
        os.system(f"flatpak run com.rtosta.zapzap {extra_args}")
    elif use_appimage:
        print("# === Running in AppImage mode ===")
        os.system("chmod +x ./_scripts/build-appimage-local.sh")
        os.system("./_scripts/build-appimage-local.sh")
    else:
        print("Error: Specify --flatpak or --appimage for preview mode.")

def build():
    """Build the application for specified targets."""
    build_appimage = "--appimage" in sys.argv
    build_flatpak = "--flatpak-onefile" in sys.argv

    if build_appimage:
        if len(sys.argv) < 4:
            print("Error: You must specify a version when building AppImage.")
            print("Usage: python run.py build --appimage <version>")
            return
        version = sys.argv[3]
        print(f"Building AppImage version {version}...")
        os.system(f"./_scripts/build-appimage.sh {version}")

    if build_flatpak:
        print("Building Flatpak Onefile... Without support at the moment!!")

    if not build_appimage and not build_flatpak:
        print("No build target specified. Use --appimage <version> or --flatpak-onefile.")

def main():
    """Main entry point for the script."""
    commands = {
        "dev": dev,
        "preview": preview,
        "build": build,
    }

    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print(
            "Usage: python run.py [dev|preview|build] [--build-translations | --appimage | --flatpak-onefile]"
        )
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

AppImage: python run.py build --appimage TAG_RELEASE
            -> python run.py build --appimage 6.0

Obs.: Ao construir os arquivos das traduções, a data e hora são atualizadas.
"""
