from os import path, listdir
from zapzap import APP_PATH


class ExtensionManager:

    _domain = "zapzap"
    _extensions_dir = path.join(APP_PATH, "extensions")

    @staticmethod
    def set_extensions(profile):
        manager = profile.extensionManager()
        print("Setting extensions for the profile...")
        # Here you would typically add the extensions to the manager
        for folder in listdir(ExtensionManager._extensions_dir):
            folder_path = path.join(
                ExtensionManager._extensions_dir, folder)
            if path.isdir(folder_path):
                print(f"  - Adding Extension: {folder_path}")
                ok = manager.loadExtension(folder_path)
                print(f"\t  - loadExtension('{folder_path}') = {ok}")


    @staticmethod
    def list_extensions():
        # TODO: Add environment variables for the Chronium flags with the extension
        """
        extension_dir = os.path.abspath("self.extension_folder")
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = f"--load-extension={extension_dir}"
        """

        print("-- Extensions directory:", ExtensionManager._extensions_dir)

        if path.isdir(ExtensionManager._extensions_dir):
            for folder in listdir(ExtensionManager._extensions_dir):
                folder_path = path.join(
                    ExtensionManager._extensions_dir, folder)
                if path.isdir(folder_path):
                    print(f"  - Extension found: {folder_path}")
    