import os
import sys
import shutil
import subprocess


def dev(build_translations=False):
    """Run the app in development mode."""
    import sys as _sys
    print(f"Running in dev mode. Translations: {build_translations}")
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python run.py dev [--build-translations] [extra-args]")
        return

    extra_args = " ".join(_sys.argv[2:])

    if _sys.platform == "win32":
        # Windows: call pyuic6 directly instead of the bash build-windows.sh
        print(" # === Build the windows from the .ui file ===")
        ui_files = [
            ("zapzap/ui/ui_mainwindow.ui",   "zapzap/views/ui_mainwindow.py"),
        ]
        for src, dst in ui_files:
            os.system(f"pyuic6 -x {src} -o {dst}")

        if build_translations:
            print("# === Build translations ===")
            os.system("python _scripts/build-translations.py")

        print("# === Start === ")
        os.system(f"python -m zapzap {extra_args}")
    else:
        print(" # === Build the windows from the .ui file ===")
        os.system("chmod +x ./_scripts/build-windows.sh")
        os.system("./_scripts/build-windows.sh")

        if build_translations:
            print("# === Build translations ===")
            os.system("./_scripts/build-translations.sh")

        print("# === Start === ")
        os.system(f"python -m zapzap {extra_args}")



def preview(build_translations=False):
    """Run the app in preview mode."""
    SDK_VERSION = "6.10"
    use_flatpak = "--flatpak" in sys.argv
    use_appimage = "--appimage" in sys.argv
    use_windows = "--windows" in sys.argv

    print("Starting app in preview mode...")

    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python run.py preview [--flatpak | --appimage | --windows] [--build-translations]")
        return

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
    elif use_windows:
        print("# === Running in Windows Preview mode ===")
        build()
        print("# === Starting Executable === ")
        os.system(r"dist\ZapZap\ZapZap.exe")
    else:
        print("Error: Specify --flatpak, --appimage or --windows for preview mode.")


def build():
    """Build the application for specified targets."""
    SDK_VERSION = "6.10"
    APP_ID = "com.rtosta.zapzap"
    MANIFEST = "com.rtosta.zapzap.yaml"

    build_appimage = "--appimage" in sys.argv
    build_flatpak = "--flatpak-onefile" in sys.argv
    build_windows = "--windows" in sys.argv

    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python run.py build [--windows | --appimage <version> | --flatpak-onefile]")
        return

    # ======================
    # Windows EXE
    # ======================
    if build_windows:
        print("# === Building Windows Executable ===")
        print(" # === Compile UI Files ===")
        ui_files = [
            ("zapzap/ui/ui_mainwindow.ui",   "zapzap/views/ui_mainwindow.py"),
            ("zapzap/ui/ui_page_general.ui",    "zapzap/views/ui_page_general.py"),
            ("zapzap/ui/ui_page_network.ui",    "zapzap/views/ui_page_network.py"),
        ]
        for src, dst in ui_files:
            if os.path.exists(src):
                print(f"Compiling {src} -> {dst}")
                try:
                    subprocess.run([sys.executable, "-m", "PyQt6.uic.pyuic", "-x", src, "-o", dst], check=True)
                except Exception as e:
                    print(f"Warning: Compilation failed for {src}. Trying fallback pyuic6 command...")
                    subprocess.run(["pyuic6", "-x", src, "-o", dst], check=True)

        print("# === Running PyInstaller ===")
        pyinstaller_cmd = [
            sys.executable, "-m", "PyInstaller",
            "--name", "ZapZap",
            "--onefile",
            "--windowed",
            "--noconfirm",
            "--add-data", "zapzap/po;zapzap/po",
            "--add-data", "zapzap/ui;zapzap/ui",
            "--add-data", "zapzap/resources;zapzap/resources",
            "--add-data", "zapzap/webengine/webrtc_shield.js;zapzap/webengine",
            "zapzap/__main__.py"
        ]
        
        try:
            subprocess.run(pyinstaller_cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: PyInstaller failed with exit code {e.returncode}")
            sys.exit(1)
        
        print("# === Creating Distribution ZIP ===")
        # In --onefile mode, PyInstaller creates dist/ZapZap.exe
        exe_path = "dist/ZapZap.exe"
        if os.path.exists(exe_path):
            # We create a temporary folder to zip it cleanly (so the zip contains the exe)
            temp_zip_dir = "dist/ZapZap_zip_temp"
            if os.path.exists(temp_zip_dir):
                shutil.rmtree(temp_zip_dir)
            os.makedirs(temp_zip_dir)
            shutil.copy2(exe_path, os.path.join(temp_zip_dir, "ZapZap.exe"))
            
            shutil.make_archive("dist/ZapZap-Windows", 'zip', temp_zip_dir)
            shutil.rmtree(temp_zip_dir)
            
            print("Build finished successfully!")
            print(f"Output: {exe_path}")
            print("Archive: dist/ZapZap-Windows.zip")
        else:
            print(f"Error: {exe_path} not found. Build failed.")
            sys.exit(1)
        return

    # ======================
    # AppImage
    # ======================
    if build_appimage:
        if len(sys.argv) < 4:
            print("Error: You must specify a version when building AppImage.")
            print("Usage: python run.py build --appimage <version>")
            return

        version = sys.argv[3]
        print(f"Building AppImage version {version}...")
        os.system(f"./_scripts/build-appimage.sh {version}")
        return

    # ======================
    # Flatpak Onefile
    # ======================
    if build_flatpak:
        build_dir = ".flatpak-build"
        repo_dir = ".flatpak-repo"
        dist_dir = "dist"
        bundle_name = f"{APP_ID}.flatpak"

        print("# === Building Flatpak Onefile ===")

        print("# === Add flathub remote ===")
        os.system(
            "flatpak remote-add --user --if-not-exists "
            "flathub https://flathub.org/repo/flathub.flatpakrepo"
        )

        print("# === Install SDK ===")
        os.system(
            f"flatpak install --user --assumeyes flathub "
            f"org.kde.Platform//{SDK_VERSION} "
            f"org.kde.Sdk//{SDK_VERSION} "
            f"com.riverbankcomputing.PyQt.BaseApp//{SDK_VERSION}"
        )

        print("# === Cleaning previous build ===")
        os.system(f"rm -rf {build_dir} {repo_dir}")
        os.system(f"mkdir -p {dist_dir}")

        print("# === Build Flatpak ===")
        os.system(
            f"flatpak-builder {build_dir} {MANIFEST} "
            f"--force-clean "
            f"--repo={repo_dir}"
        )

        print("# === Create onefile bundle ===")
        os.system(
            f"flatpak build-bundle {repo_dir} "
            f"{dist_dir}/{bundle_name} "
            f"{APP_ID} "
            f"--runtime-repo=https://flathub.org/repo/flathub.flatpakrepo"
        )

        print("Flatpak Onefile build finished!")
        print(f"Output: {dist_dir}/{bundle_name}")
        return

    # ======================
    # No target
    # ======================
    print("No build target specified.")
    print("Usage:")
    print("  python run.py build --windows")
    print("  python run.py build --appimage <version>")
    print("  python run.py build --flatpak-onefile")


def main():
    """Main entry point for the script."""
    commands = {
        "dev": dev,
        "preview": preview,
        "build": build,
    }

    if len(sys.argv) < 2 or sys.argv[1] not in commands or "--help" in sys.argv or "-h" in sys.argv:
        print(
            "Usage: python run.py [dev|preview|build] [--build-translations | --appimage | --flatpak-onefile | --windows | --flatpak]"
        )
        if len(sys.argv) > 1 and sys.argv[1] in commands:
            commands[sys.argv[1]]()
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
