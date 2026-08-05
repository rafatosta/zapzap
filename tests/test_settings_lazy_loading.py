from types import SimpleNamespace
from unittest.mock import Mock, patch

from PyQt6.QtWidgets import QWidget

from qt_test_case import QtTestCase
from zapzap.app.main_window_controller import MainWindowController
from zapzap.features.settings.shell import settings_controller as settings_module
from zapzap.features.settings.shell.settings_controller import SettingsController


PAGE_TYPES = (
    (
        "zapzap.features.settings.pages.accounts.controller",
        "AccountsSettingsController",
    ),
    (
        "zapzap.features.settings.pages.appearance.controller",
        "AppearanceSettingsController",
    ),
    (
        "zapzap.features.settings.pages.notifications.controller",
        "NotificationsSettingsController",
    ),
    (
        "zapzap.features.settings.pages.permissions.controller",
        "PermissionsSettingsController",
    ),
    (
        "zapzap.features.settings.pages.system_startup.controller",
        "SystemStartupSettingsController",
    ),
    (
        "zapzap.features.settings.pages.language_downloads.controller",
        "LanguageDownloadSettingsController",
    ),
    (
        "zapzap.features.settings.pages.network_privacy.controller",
        "NetworkPrivacySettingsController",
    ),
    (
        "zapzap.features.settings.pages.advanced_customizations.controller",
        "AdvancedCustomizationsSettingsController",
    ),
    (
        "zapzap.features.settings.pages.performance_experimental.controller",
        "PerformanceExperimentalSettingsController",
    ),
    (
        "zapzap.features.settings.pages.debugging.controller",
        "DebuggingSettingsController",
    ),
    (
        "zapzap.features.settings.pages.about.controller",
        "AboutSettingsController",
    ),
)


class SettingsLazyLoadingTest(QtTestCase):
    EXPECTED_LABELS = [
        "Accounts",
        "Appearance",
        "Notifications",
        "Permissions",
        "System and startup",
        "Language and Download",
        "Privacy and Network",
        "Advanced Customizations",
        "Performance experimental",
        "Debugging",
        "About",
    ]

    def setUp(self):
        self.constructions = {}
        self.imported_modules = []
        self.page_types = {}
        self.modules = {}
        for module_name, controller_name in PAGE_TYPES:
            page_type = self._page_type(module_name, controller_name)
            self.page_types[controller_name] = page_type
            self.modules[module_name] = SimpleNamespace(
                **{controller_name: page_type}
            )

        self.window = SimpleNamespace(
            request_quit=Mock(),
            close_settings=Mock(),
        )
        self.app.getWindow = Mock(return_value=self.window)
        self.addCleanup(delattr, self.app, "getWindow")
        self.import_patch = patch.object(
            settings_module,
            "import_module",
            side_effect=self._import_module,
        )
        self.import_patch.start()
        self.addCleanup(self.import_patch.stop)

    def _page_type(self, module_name, controller_name):
        constructions = self.constructions

        def init(page):
            QWidget.__init__(page)
            constructions[controller_name] = (
                constructions.get(controller_name, 0) + 1
            )
            page.focus_calls = 0

        def focus_spellchecker_management(page):
            page.focus_calls += 1

        return type(
            controller_name,
            (QWidget,),
            {
                "__module__": module_name,
                "__init__": init,
                "focus_spellchecker_management": focus_spellchecker_management,
            },
        )

    def _import_module(self, module_name):
        self.imported_modules.append(module_name)
        return self.modules[module_name]

    def _settings(self):
        settings = SettingsController()
        self.addCleanup(settings.deleteLater)
        return settings

    def test_initial_shell_creates_and_imports_only_default_page(self):
        settings = self._settings()

        self.assertEqual(settings.pages.count(), 1)
        self.assertEqual(list(settings._page_instances), ["accounts"])
        self.assertEqual(
            self.imported_modules,
            ["zapzap.features.settings.pages.accounts.controller"],
        )
        self.assertEqual(
            [button.text() for button in settings.page_buttons.values()],
            self.EXPECTED_LABELS,
        )
        self.assertEqual(settings.current_page_id, "accounts")

    def test_navigation_constructs_once_and_reuses_page_and_signal(self):
        settings = self._settings()
        button = settings.page_buttons["appearance"]

        button.click()
        first = settings.page_instance("appearance")
        button.click()

        self.assertIs(settings.page_instance("appearance"), first)
        self.assertEqual(self.constructions["AppearanceSettingsController"], 1)
        self.assertEqual(settings.pages.count(), 2)
        self.assertEqual(settings.current_page_id, "appearance")

    def test_public_target_helpers_create_and_select_lazy_pages(self):
        settings = self._settings()

        about = settings.open_about()
        language = settings.open_language_downloads()

        self.assertIs(about, settings.page_instance("about"))
        self.assertIs(language, settings.page_instance("language_downloads"))
        self.assertEqual(language.focus_calls, 1)
        self.assertEqual(settings.current_page_id, "language_downloads")
        self.assertEqual(settings.pages.count(), 3)

    def test_open_page_type_matches_uninstantiated_descriptor(self):
        settings = self._settings()
        page_type = self.page_types["PermissionsSettingsController"]

        page = settings.open_page_type(page_type)

        self.assertIsInstance(page, page_type)
        self.assertIs(page, settings.page_instance("permissions"))
        self.assertEqual(self.constructions["PermissionsSettingsController"], 1)

    def test_factory_error_keeps_current_page_and_reports_it(self):
        settings = self._settings()
        failing_module = (
            "zapzap.features.settings.pages.notifications.controller"
        )
        self.modules.pop(failing_module)

        with patch.object(settings_module.AlertManager, "critical") as alert:
            page = settings.open_page_id("notifications")

        self.assertIsNone(page)
        self.assertEqual(settings.current_page_id, "accounts")
        self.assertEqual(settings.pages.count(), 1)
        self.assertTrue(settings.page_buttons["notifications"].isEnabled())
        alert.assert_called_once()

    def test_close_settings_drops_main_window_reference_and_schedules_delete(self):
        settings = Mock()
        browser = object()
        main_window = SimpleNamespace(
            app_settings=settings,
            browser=browser,
            stackedWidget=Mock(),
        )

        MainWindowController.close_settings(main_window)

        self.assertIsNone(main_window.app_settings)
        main_window.stackedWidget.removeWidget.assert_called_once_with(settings)
        settings.deleteLater.assert_called_once_with()
        main_window.stackedWidget.setCurrentWidget.assert_called_once_with(
            browser
        )
