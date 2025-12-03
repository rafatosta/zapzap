from os import path, listdir
from zapzap import APP_PATH
import sys


class ExtensionManager:

    _domain = "zapzap"
    _extensions_dir = path.join(APP_PATH, "extensions")
    _profile = None

    @staticmethod
    def set_extensions(profile):
        ExtensionManager._profile = profile.extensionManager()
        print("Setting extensions for the profile...")
        # Here you would typically add the extensions to the manager
        for folder in listdir(ExtensionManager._extensions_dir):
            folder_path = path.join(
                ExtensionManager._extensions_dir, folder)
            if path.isdir(folder_path):
                print(f"  - Adding Extension: {folder_path}")
                ExtensionManager._profile.installExtension(folder_path)

                curr_extension = ExtensionManager._profile.extensions()[-1]
                if curr_extension.error(): # Empty if no error found while loading
                    print(f"INFO - Failed to install: {folder_path}", file=sys.stderr)
                    print(f"\t  ERROR: {curr_extension.error()}", file=sys.stderr)
                    continue

                print(f"\t  - loadExtension('{curr_extension.path()}') = {curr_extension.id()}")


    @staticmethod
    def list_extensions():
        print("-- Extensions directory:", ExtensionManager._extensions_dir)

        if path.isdir(ExtensionManager._extensions_dir):
            for folder in listdir(ExtensionManager._extensions_dir):
                folder_path = path.join(
                    ExtensionManager._extensions_dir, folder)
                if path.isdir(folder_path):
                    print(f"  - Extension found: {folder_path}")
    