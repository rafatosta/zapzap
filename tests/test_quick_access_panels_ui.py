"""Structural and lifecycle regression coverage for the two reintroduced
Quick Access visual scaffolds: the floating monitoring panel and the
integrated account selector.

These tests only assert rendered structure, initial methods and
independent/coexisting visibility. They must not assert any future
functional behavior (account switching, monitoring data, persistence or
auto show/close), since the components only provide visual scaffolding at
this stage.
"""

from PyQt6.QtWidgets import QPushButton, QToolButton, QWidget

from qt_test_case import QtTestCase
from zapzap.ui.components import (
    FloatingMonitoringPanel,
    IntegratedAccountSelector,
)
from zapzap.ui.components.floating_monitoring_panel import (
    FloatingAccountEntry,
)
from zapzap.ui.primitives import CloseButton, Label


class FloatingMonitoringPanelUiTests(QtTestCase):

    def test_panel_renders_header_and_placeholder_structure(self):
        panel = FloatingMonitoringPanel()

        self.assertIsInstance(panel.title_label, Label)
        self.assertEqual(panel.title_label.text(), "Quick access")
        self.assertIsInstance(panel.close_button, CloseButton)
        self.assertIsInstance(panel.empty_state_label, Label)
        self.assertFalse(panel.empty_state_label.isHidden())
        self.assertEqual(panel.accessibleName(), "Monitoring panel")

    def test_panel_renders_add_account_row_and_footer_actions(self):
        panel = FloatingMonitoringPanel()

        self.assertEqual(panel.add_account_row.name_label.text(), "New account")
        self.assertFalse(panel.add_account_row.avatar_label.pixmap().isNull())

        for button in (
            panel.audio_button,
            panel.downloads_button,
            panel.settings_button,
        ):
            self.assertIsInstance(button, QPushButton)
            self.assertFalse(button.icon().isNull())

        self.assertEqual(panel.audio_button.text(), "Audio")
        self.assertEqual(panel.downloads_button.text(), "Downloads")
        self.assertEqual(panel.settings_button.text(), "Settings")

    def test_set_accounts_renders_rows_and_toggles_empty_state(self):
        panel = FloatingMonitoringPanel()

        panel.set_accounts(
            [
                FloatingAccountEntry("a1", "Rafael", unread_count=12),
                FloatingAccountEntry("a2", "Trabalho", unread_count=0, active=True),
            ]
        )

        self.assertTrue(panel.empty_state_label.isHidden())
        self.assertEqual(len(panel._account_rows), 2)

        first_row, second_row = panel._account_rows
        self.assertEqual(first_row.account_id, "a1")
        self.assertEqual(first_row.name_label.text(), "Rafael")
        self.assertFalse(first_row.badge.isHidden())
        self.assertEqual(first_row.badge.text(), "12")

        self.assertEqual(second_row.account_id, "a2")
        self.assertTrue(second_row.badge.isHidden())
        self.assertEqual(second_row.property("active"), True)

        panel.clear_accounts()
        self.assertEqual(panel._account_rows, [])
        self.assertFalse(panel.empty_state_label.isHidden())

    def test_account_row_activation_emits_signal_without_switching(self):
        panel = FloatingMonitoringPanel()
        panel.set_accounts([FloatingAccountEntry("a1", "Rafael")])
        activated = []
        panel.account_activation_requested.connect(activated.append)

        panel._account_rows[0].activated.emit()

        self.assertEqual(activated, ["a1"])

    def test_footer_and_add_account_only_emit_scaffolded_signals(self):
        panel = FloatingMonitoringPanel()
        signals = []
        panel.add_account_requested.connect(lambda: signals.append("add"))
        panel.audio_toggle_requested.connect(lambda: signals.append("audio"))
        panel.downloads_requested.connect(lambda: signals.append("downloads"))
        panel.settings_requested.connect(lambda: signals.append("settings"))

        panel.add_account_row.activated.emit()
        panel.audio_button.click()
        panel.downloads_button.click()
        panel.settings_button.click()

        self.assertEqual(signals, ["add", "audio", "downloads", "settings"])

    def test_panel_is_hidden_by_default_and_never_auto_shows(self):
        panel = FloatingMonitoringPanel()
        self.assertFalse(panel.isVisible())
        self.assertFalse(panel.is_panel_visible())

    def test_show_hide_toggle_methods_control_independent_visibility(self):
        panel = FloatingMonitoringPanel()

        panel.show_panel()
        self.assertTrue(panel.is_panel_visible())

        panel.hide_panel()
        self.assertFalse(panel.is_panel_visible())

        panel.toggle_panel()
        self.assertTrue(panel.is_panel_visible())
        panel.toggle_panel()
        self.assertFalse(panel.is_panel_visible())

    def test_close_button_hides_without_destroying_the_panel(self):
        panel = FloatingMonitoringPanel()
        panel.show_panel()

        panel.close_button.click()

        self.assertFalse(panel.is_panel_visible())
        # The panel is "permanent": hiding it must not delete or reset it.
        self.assertIsInstance(panel.empty_state_label, Label)

    def test_visibility_changed_signal_reports_both_transitions(self):
        panel = FloatingMonitoringPanel()
        observed = []
        panel.visibility_changed.connect(observed.append)

        panel.show_panel()
        panel.hide_panel()

        self.assertEqual(observed, [True, False])


class IntegratedAccountSelectorUiTests(QtTestCase):

    def test_selector_renders_add_account_affordance_and_empty_state(self):
        selector = IntegratedAccountSelector()

        self.assertIsInstance(selector.add_account_button, QToolButton)
        self.assertFalse(selector.add_account_button.icon().isNull())
        self.assertIsInstance(selector.empty_state_label, Label)
        self.assertEqual(selector.empty_state_label.text(), "No accounts yet")
        self.assertEqual(
            selector.accessibleName(), "Account selector"
        )

    def test_selector_is_hidden_by_default_and_never_auto_shows(self):
        selector = IntegratedAccountSelector()
        self.assertFalse(selector.isVisible())
        self.assertFalse(selector.is_selector_visible())

    def test_show_hide_toggle_methods_control_independent_visibility(self):
        selector = IntegratedAccountSelector()

        selector.show_selector()
        self.assertTrue(selector.is_selector_visible())

        selector.hide_selector()
        self.assertFalse(selector.is_selector_visible())

        selector.toggle_selector()
        self.assertTrue(selector.is_selector_visible())
        selector.toggle_selector()
        self.assertFalse(selector.is_selector_visible())

    def test_add_account_button_only_emits_the_scaffolded_signal(self):
        selector = IntegratedAccountSelector()
        requests = []
        selector.add_account_requested.connect(lambda: requests.append(True))

        selector.add_account_button.click()

        self.assertEqual(requests, [True])

    def test_reposition_anchors_selector_to_parent_width_without_sidebar_state(self):
        host = QWidget()
        host.resize(400, 300)
        selector = IntegratedAccountSelector(host)

        selector.show_selector()

        self.assertEqual(selector.width(), host.width())
        self.assertEqual(selector.x(), 0)
        self.assertEqual(selector.y(), selector.MARGIN)

    def test_visibility_changed_signal_reports_both_transitions(self):
        selector = IntegratedAccountSelector()
        observed = []
        selector.visibility_changed.connect(observed.append)

        selector.show_selector()
        selector.hide_selector()

        self.assertEqual(observed, [True, False])


class QuickAccessScaffoldsCoexistenceTests(QtTestCase):

    def test_panel_and_selector_have_independent_lifecycle_and_can_coexist(self):
        host = QWidget()
        host.resize(500, 400)
        host.show()
        panel = FloatingMonitoringPanel()
        selector = IntegratedAccountSelector(host)

        panel.show_panel()
        self.assertTrue(panel.is_panel_visible())
        self.assertFalse(selector.is_selector_visible())

        selector.show_selector()
        self.assertTrue(panel.is_panel_visible())
        self.assertTrue(selector.is_selector_visible())

        panel.hide_panel()
        self.assertFalse(panel.is_panel_visible())
        self.assertTrue(selector.is_selector_visible())

        selector.hide_selector()
        self.assertFalse(panel.is_panel_visible())
        self.assertFalse(selector.is_selector_visible())

    def test_components_do_not_couple_to_browser_sidebar_state(self):
        import inspect

        from zapzap.ui.components import (
            floating_monitoring_panel,
            integrated_account_selector,
        )

        coupling_markers = (
            "BrowserSidebar",
            "browser_sidebar",
            "system/sidebar",
        )
        for module in (floating_monitoring_panel, integrated_account_selector):
            source = inspect.getsource(module)
            for marker in coupling_markers:
                self.assertNotIn(marker, source)
