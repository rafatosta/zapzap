import os

class ExtensionManager:

    extension_folder =  "zapzap/extensions"

    @staticmethod
    def apply():
        print("Applying Extension Manager settings...")
        # TODO: Add environment variables for the Chronium flags with the extension
        """
        extension_dir = os.path.abspath("self.extension_folder")
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = f"--load-extension={extension_dir}"
        """

    
