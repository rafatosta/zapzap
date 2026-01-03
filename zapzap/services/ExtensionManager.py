from os import path, listdir
import sys

from zapzap import APP_PATH
from zapzap.extensions.DarkReaderBridge import DarkReaderBridge


class ExtensionManager:
    _domain = "zapzap"
    _extensions_dir = path.join(APP_PATH, "extensions")
    _qview = None
    _profile = None
    _extension_manager = None
    extensions = {}  # Dict with all the IDs mapped to their folders

    @staticmethod
    def set_extensions(qview, profile):
        ExtensionManager._qview = qview
        ExtensionManager._profile = profile
        ExtensionManager._extension_manager = profile.extensionManager()

        print("Setting extensions for the profile...")
        # Here you would typically add the extensions to the manager
        for folder in listdir(ExtensionManager._extensions_dir):
            if folder == "__pycache__": continue

            folder_path = path.join(
                ExtensionManager._extensions_dir, folder)
            if path.isdir(folder_path):
                print(f"  - Adding Extension: {folder_path}")
                ExtensionManager._extension_manager.loadExtension(folder_path)

                curr_extension = ExtensionManager._extension_manager.extensions()[-1]
                if curr_extension.error():  # Empty if no error found while loading
                    print(f"INFO - Failed to load: {folder_path}", file=sys.stderr)
                    print(f"\t  ERROR: {curr_extension.error()}", file=sys.stderr)
                    continue

                ExtensionManager.extensions[curr_extension.id()] = curr_extension.name()

                # Configure extensions individually
                if folder == "darkreader-chrome": ExtensionManager._configure_dark_reader(curr_extension.id())

                print(f"\t  - Load Extension('{curr_extension.name()}') = {curr_extension.id()}")

    @staticmethod
    def list_extensions():
        print("-- Extensions directory:", ExtensionManager._extensions_dir)

        if path.isdir(ExtensionManager._extensions_dir):
            for folder in listdir(ExtensionManager._extensions_dir):
                folder_path = path.join(
                    ExtensionManager._extensions_dir, folder)
                if path.isdir(folder_path):
                    print(f"  - Extension found: {folder_path}")

    @staticmethod
    def _configure_dark_reader(extension_id):
        DarkReaderBridge(extension_id, ExtensionManager._profile)