import os


def dev():
    """Run the app in development mode."""
    print("Starting app in development mode...")
    os.system("python -m zapzap")


def preview():
    """Run the app in preview mode."""
    SDK_VERSION = 6.8

    print("Starting app in preview mode...")

    print("Add flathub remote")
    os.system(
        "flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo")

    print("# === Install Sdk === ")
    os.system(f"flatpak install --user --assumeyes flathub org.kde.Platform//{
        SDK_VERSION} org.kde.Sdk//{SDK_VERSION} com.riverbankcomputing.PyQt.BaseApp//{SDK_VERSION} ")

    print("# === Build === ")
    os.system(
        "flatpak-builder build com.rtosta.zapzap.yaml --force-clean --ccache --install --user")

    print("# === start === ")
    os.system("flatpak run com.rtosta.zapzap")


def build():
    """Build the app for production."""
    print("Building the app for production...")
    """ os.makedirs("dist", exist_ok=True)
    os.system("pyinstaller --onefile zapzap/main.py -n zapzap")
    print("Build completed. Check the 'dist' folder.") """


if __name__ == "__main__":
    import sys

    commands = {
        "dev": dev,
        "preview": preview,
        "build": build,
    }

    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print(f"Usage: python run.py [dev|preview|build]")
    else:
        commands[sys.argv[1]]()
