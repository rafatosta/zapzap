from PyQt6.QtWidgets import QDialog

from zapzap.services.SettingsManager import SettingsManager


class OnboardingManager:
    SETTING_KEY = "onboarding/completed"

    @staticmethod
    def should_show() -> bool:
        return not SettingsManager.get(OnboardingManager.SETTING_KEY, False)

    @staticmethod
    def show(parent=None) -> bool:
        if not OnboardingManager.should_show():
            return False

        # Lazy import to avoid circular dependency between services and controllers
        from zapzap.controllers.OnboardingDialog import OnboardingDialog

        dialog = OnboardingDialog(parent)
        result = dialog.exec()

        return result == QDialog.DialogCode.Accepted

    @staticmethod
    def mark_complete():
        SettingsManager.set(OnboardingManager.SETTING_KEY, True)

    @staticmethod
    def reset():
        SettingsManager.remove(OnboardingManager.SETTING_KEY)
