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
        self.assertNotIn("window.innerHeight - bounds.bottom + 90", self.script)
        self.assertIn("parent.insertBefore(button, anchor)", self.script)
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
        self.assertIn("appearance_settings.sidebar_button_mode == \"integrated\"", self.web_view)

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


from qt_test_case import QtTestCase
from PyQt6.QtCore import QEventLoop, QTimer
from PyQt6 import sip
from PyQt6.QtWebEngineWidgets import QWebEngineView


class QuickAccountsAppearanceTests(QtTestCase):
    def javascript(self, page, script):
        result = []
        loop = QEventLoop()
        page.runJavaScript(script, lambda value: (result.append(value), loop.quit()))
        QTimer.singleShot(15000, loop.quit)
        loop.exec()
        self.assertEqual(len(result), 1)
        return result[0]

    def test_icon_tracks_navigation_styles_and_falls_back(self):
        view = QWebEngineView()
        self.addCleanup(lambda: sip.delete(view))
        view.resize(800, 600)
        view.show()
        page = view.page()
        loop = QEventLoop()
        loaded = []
        page.loadFinished.connect(lambda ok: (loaded.append(ok), loop.quit()))
        page.setHtml("""<style>
            nav svg { fill: rgb(12, 34, 56); width:24px; height:24px }
            body.dark nav svg { fill: rgb(210, 220, 230); width:28px; height:28px }
            nav { display:flex; flex-direction:column; width:64px; height:100vh }
            .bottom { display:flex; flex-direction:column; margin-top:auto; gap:8px }
            .bottom > * { min-height:40px; flex-shrink:0 }
            </style><nav role="navigation"><button><svg></svg></button>
            <div class="bottom"><button id="extra">Bug</button>
            <button id="settings">Settings</button><span>BETA</span>
            <button id="profile">Profile</button></div></nav>""")
        QTimer.singleShot(15000, loop.quit)
        loop.exec()
        self.assertEqual(loaded, [True])
        controller = SCRIPT.read_text().split("    const QuickAccountsController =", 1)[1]
        controller = controller.split("    const ThemeController =", 1)[0]
        controller = controller.replace("{quick_accounts_visible}", "true").replace(
            "{quick_accounts_icon}", '<svg viewBox="0 0 24 24"></svg>'
        )
        self.javascript(page, "const QuickAccountsController =" + controller +
                        "QuickAccountsController.boot();")
        snapshot = """(() => {
            const icon = document.querySelector('[data-zapzap-component] svg');
            const style = getComputedStyle(icon);
            return [style.fill, style.width, style.height];
        })()"""
        self.assertEqual(self.javascript(page, snapshot),
                         ["rgb(12, 34, 56)", "24px", "24px"])
        self.javascript(page, 'document.body.className = "dark";')
        # Wait for the real MutationObserver and requestAnimationFrame, without
        # invoking ensureButton explicitly.
        wait = QEventLoop()
        QTimer.singleShot(250, wait.quit)
        wait.exec()
        self.assertEqual(self.javascript(page, snapshot),
                         ["rgb(210, 220, 230)", "28px", "28px"])
        layout = """(() => {
            const button = document.querySelector('[data-zapzap-component]');
            const box = button.getBoundingClientRect();
            const others = [...document.querySelectorAll('.bottom > :not([data-zapzap-component])')];
            return getComputedStyle(button).position === 'static' && others.every(item => {
                const rect = item.getBoundingClientRect();
                return rect.bottom <= box.top || rect.top >= box.bottom;
            });
        })()"""
        self.assertTrue(self.javascript(page, layout))
        self.javascript(page, """
            const extra = document.createElement('button');
            extra.textContent = 'Another action';
            document.querySelector('.bottom').prepend(extra);
        """)
        view.resize(800, 450)
        wait = QEventLoop()
        QTimer.singleShot(250, wait.quit)
        wait.exec()
        self.assertTrue(self.javascript(page, layout))
        # A plain-div rail must be found without nav/aside/ARIA landmarks.
        self.javascript(page, """
            const nav = document.querySelector('nav');
            const rail = document.createElement('div');
            rail.id = 'plain-rail';
            rail.style.cssText = 'display:flex;flex-direction:column;width:64px;height:100vh';
            while (nav.firstChild) rail.appendChild(nav.firstChild);
            nav.replaceWith(rail);
            QuickAccountsController.ensureButton();
        """)
        self.assertEqual(self.javascript(page,
            "QuickAccountsController.findQuickAccountsMountPoint().id"), "plain-rail")
        # Simulate a fixed-height wrapper that clips the injected child.
        self.javascript(page, """
            const bottom = document.querySelector('.bottom');
            bottom.style.cssText = 'height:40px;overflow:hidden;flex-shrink:0';
            QuickAccountsController.ensureButton();
        """)
        visible = """(() => {
            const button = document.querySelector('[data-zapzap-component]');
            const rect = button.getBoundingClientRect();
            return rect.height > 0 && rect.top >= 0 && rect.bottom <= innerHeight &&
                button.contains(document.elementFromPoint(rect.left + rect.width / 2,
                                                          rect.top + rect.height / 2));
        })()"""
        self.assertTrue(self.javascript(page, visible))
        self.assertEqual(self.javascript(page,
            "document.querySelector('[data-zapzap-component]').parentElement.tagName"), "BODY")
        self.javascript(page, """
            window.calls = 0;
            QuickAccountsController.setBridge({open_recent_accounts: () => window.calls++});
            document.querySelector('[data-zapzap-component]').click();
        """)
        self.assertEqual(self.javascript(page, "window.calls"), 1)
        # Repeated DOM checks must neither duplicate nor lose the fallback.
        self.javascript(page, "QuickAccountsController.ensureButton();")
        self.assertTrue(self.javascript(page, visible))
        self.assertEqual(self.javascript(page,
            "document.querySelectorAll('[data-zapzap-component]').length"), 1)
        self.javascript(page, "document.querySelector('[data-zapzap-component]').remove()")
        wait = QEventLoop()
        QTimer.singleShot(250, wait.quit)
        wait.exec()
        self.assertTrue(self.javascript(page, visible))
        self.javascript(page, "QuickAccountsController.setVisible(false)")
        self.assertEqual(self.javascript(page,
            "document.querySelector('[data-zapzap-component]').getBoundingClientRect().height"), 0)
        self.javascript(page, "QuickAccountsController.setVisible(true)")
        self.javascript(page, """
            document.querySelector('#plain-rail > button').remove();
            QuickAccountsController.setIconColor('#abcdef');
            QuickAccountsController.ensureButton();
        """)
        self.assertEqual(self.javascript(page, snapshot),
                         ["rgb(171, 205, 239)", "20px", "20px"])


if __name__ == "__main__":
    unittest.main()
