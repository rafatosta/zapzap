
import subprocess

from tools.translation_manager import TranslationManager


class FlatpakRunner:
    SDK_VERSION = "6.11"
    MANIFEST = "tools/com.rtosta.zapzap.yaml"
    BUILD_DIR = "build"
    APP_COMMAND = "/app/bin/zapzap"

    def __init__(self, args: list[str]):
        self.args = args

    def execute(self, command: list[str]):
        print(f"$ {subprocess.list2cmdline(command)}", flush=True)
        subprocess.run(command, check=True)

    def setup(self):
        print("# === Add Flathub remote ===")
        self.execute([
            "flatpak", "remote-add",
            "--user",
            "--if-not-exists",
            "flathub",
            "https://flathub.org/repo/flathub.flatpakrepo",
        ])

        print("# === Install SDK dependencies ===")
        self.execute([
            "flatpak", "install",
            "--user",
            "--assumeyes",
            "flathub",
            f"org.kde.Platform//{self.SDK_VERSION}",
            f"org.kde.Sdk//{self.SDK_VERSION}",
            f"com.riverbankcomputing.PyQt.BaseApp//{self.SDK_VERSION}",
        ])

        print("# === Install Flatpak Builder ===")
        self.execute([
            "flatpak", "install",
            "--user",
            "--assumeyes",
            "org.flatpak.Builder",
        ])

    def build(self):
        print("# === Build translations ===")
        TranslationManager().run()

        print("# === Build Flatpak ===")
        self.execute([
            "flatpak", "run",
            "org.flatpak.Builder",
            "--force-clean",
            "--ccache",
            self.BUILD_DIR,
            self.MANIFEST,
        ])

    def start(self):
        print("# === Start Flatpak without installation ===")
        self.execute([
            "flatpak", "build",
            "--runtime",
            "--with-appdir",
            "--socket=wayland",
            "--socket=fallback-x11",
            "--socket=session-bus",
            "--socket=pulseaudio",
            "--share=ipc",
            "--share=network",
            "--device=all",
            "--env=QT_QPA_PLATFORM=wayland",
            self.BUILD_DIR,
            self.APP_COMMAND,
            *self.args,
        ])

    def run(self):
        print("# === Running in Flatpak mode ===")
        self.setup()
        self.build()
        self.start()
