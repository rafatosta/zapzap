from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "zapzap/features/browser/web/scripts/theme_controller.js"
WEB_VIEW = ROOT / "zapzap/features/browser/web/web_view.py"
BROWSER_CONTROLLER = ROOT / "zapzap/features/browser/shell/browser_controller.py"


class QuickAccountsIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = SCRIPT.read_text(encoding="utf-8")
        cls.web_view = WEB_VIEW.read_text(encoding="utf-8")
        cls.browser_controller = BROWSER_CONTROLLER.read_text(encoding="utf-8")

    def test_script_uses_resilient_dom_entry_point(self):
        self.assertIn("const QuickAccountsController", self.script)
        self.assertIn("{quick_accounts_visible}", self.script)
        self.assertIn("findQuickAccountsMountPoint", self.script)
        self.assertIn("bounds.left <= 24", self.script)
        self.assertIn("bounds.height >= window.innerHeight * 0.5", self.script)
        self.assertIn("target.appendChild(button)", self.script)
        self.assertNotIn("target.insertBefore(button", self.script)
        self.assertIn("window.innerHeight - bounds.bottom + 90", self.script)
        self.assertIn("bounds.width - 46", self.script)
        self.assertIn('window.addEventListener("resize"', self.script)
        self.assertIn("button.parentElement !== target", self.script)
        self.assertIn("main > div:first-child", self.script)
        self.assertIn("new MutationObserver", self.script)
        self.assertIn("requestAnimationFrame", self.script)
        self.assertIn('data-zapzap-component", "quick-accounts"', self.script)
        self.assertIn("createButton(isFallback)", self.script)
        self.assertIn("button.innerHTML = `{quick_accounts_icon}`", self.script)
        self.assertIn("setIconColor(color)", self.script)
        self.assertIn("setState(visible, iconColor)", self.script)
        self.assertIn('"left:12px"', self.script)
        self.assertNotIn('"right:18px"', self.script)
        self.assertIn("open_recent_accounts", self.script)

    def test_script_does_not_own_account_management(self):
        controller = self.script.split("const QuickAccountsController", 1)[1].split(
            "const ThemeController", 1
        )[0]
        self.assertNotIn("localStorage", controller)
        self.assertNotIn("indexedDB", controller)
        self.assertNotIn("__reactFiber", controller)
        self.assertNotIn("location.", controller)

    def test_python_reuses_the_native_grid_entry_point(self):
        self.assertIn("open_recent_accounts_requested = pyqtSignal()", self.web_view)
        self.assertIn("def open_recent_accounts(self)", self.web_view)
        self.assertIn("open_recent_accounts.connect(self.show_grid_view)", self.browser_controller)
        self.assertIn("set_quick_accounts_button_visible", self.browser_controller)
        self.assertIn('"view_grid"', self.web_view)
        self.assertIn('"{quick_accounts_icon}"', self.web_view)
        self.assertIn("def sync_quick_accounts_state(self)", self.web_view)
        self.assertIn("def _quick_accounts_icon_color(color_scheme)", self.web_view)
        self.assertIn('f"setIconColor(\'{color}\')"', self.web_view)

    def test_web_script_is_registered_before_initial_navigation(self):
        setup_page = self.web_view.split("def _setup_page(self):", 1)[1]
        self.assertLess(
            setup_page.index("self._inject_web_theme_controller()"),
            setup_page.index("self.load_page()"),
        )

    def test_quick_accounts_boots_before_theme_controller(self):
        self.assertLess(
            self.script.index("QuickAccountsController.boot()"),
            self.script.index("ThemeController.boot()"),
        )


if __name__ == "__main__":
    unittest.main()
