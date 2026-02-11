from zapzap.services.CustomizationsManager import CustomizationsManager


class ExtensionRuntimeManager:
    """Small wrapper for future extension management UI."""

    @staticmethod
    def get_manager(profile):
        if not profile:
            return None
        try:
            return profile.extensionManager()
        except (AttributeError, RuntimeError):
            return None

    @staticmethod
    def install_path(profile):
        manager = ExtensionRuntimeManager.get_manager(profile)
        if not manager:
            return CustomizationsManager.get_extensions_dir()

        try:
            return manager.installPath()
        except (AttributeError, RuntimeError):
            return CustomizationsManager.get_extensions_dir()

    @staticmethod
    def list_extensions(profile):
        manager = ExtensionRuntimeManager.get_manager(profile)
        if not manager:
            return []

        try:
            return list(manager.extensions())
        except (AttributeError, RuntimeError):
            return []

    @staticmethod
    def install_extension(profile, path):
        manager = ExtensionRuntimeManager.get_manager(profile)
        if manager:
            manager.installExtension(path)

    @staticmethod
    def load_extension(profile, path):
        manager = ExtensionRuntimeManager.get_manager(profile)
        if manager:
            manager.loadExtension(path)

    @staticmethod
    def set_enabled(profile, extension_info, enabled: bool):
        manager = ExtensionRuntimeManager.get_manager(profile)
        if manager:
            manager.setExtensionEnabled(extension_info, enabled)

    @staticmethod
    def uninstall_extension(profile, extension_info):
        manager = ExtensionRuntimeManager.get_manager(profile)
        if manager:
            manager.uninstallExtension(extension_info)
