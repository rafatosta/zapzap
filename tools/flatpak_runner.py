import subprocess

from tools.translation_manager import TranslationManager

class FlatpakRunner:
    SDK_VERSION = "6.11"

    def __init__(self, args: list[str]):
        self.args = args

    def execute(self, command: str):
        print(f"$ {command}")
        subprocess.run(command, shell=True, check=True)

    def setup(self):
        print("# === Add flathub remote ===")
        self.execute(
            "flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo"
        )

        print("# === Install SDK ===")
        self.execute(
            f"flatpak install --user --assumeyes flathub "
            f"org.kde.Platform//{self.SDK_VERSION} "
            f"org.kde.Sdk//{self.SDK_VERSION} "
            f"com.riverbankcomputing.PyQt.BaseApp//{self.SDK_VERSION}"
        )

        print("# === Flatpak Builder ===")
        self.execute("flatpak install --user --assumeyes org.flatpak.Builder")

    def build(self):
        print("# === Build translations ===")
        manager = TranslationManager()
        manager.run()

        print("# === Build Flatpak ===")
        self.execute(
            "flatpak run org.flatpak.Builder "
            "--force-clean "
            "--ccache "
            "--install "
            "--user "
            "build "
            "tools/com.rtosta.zapzap.yaml"
        )

    def start(self):
        print("# === Start Flatpak ===")

        extra_args = " ".join(self.args)

        self.execute(f"flatpak run com.rtosta.zapzap {extra_args}")

    def run(self):
        print("# === Running in Flatpak mode ===")
        self.setup()
        self.build()
        self.start()
