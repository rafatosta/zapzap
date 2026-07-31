"""Regression tests for the appearance settings hierarchy."""

import unittest
from unittest.mock import patch

from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QApplication, QBoxLayout

from qt_test_case import QtTestCase
from zapzap.ui.components import SUBSETTING_INDENT, SettingsDivider
from zapzap.features.settings.pages.appearance.controller import (
    AppearanceSettingsController,
)
from zapzap.features.settings.pages.appearance.view import (
    AppearanceSettingsView,
)


class FakeAppearanceSettingsModel:

    def __init__(self, tray_enabled=False, csr_enabled=False):
        self.browser_sidebar_visible = True
        self.menubar_visible = True
        self.scale = 100
        self.tray_icon_enabled = tray_enabled
        self.notification_counter_enabled = True
        self.grid_columns = 2
        self.csr_enabled = csr_enabled
        self.csr_button_theme = "default"
        self.csr_show_minimize_button = True
        self.csr_show_maximize_button = False
        self.csr_buttons_direction = "right"
        self.theme = "auto"
        self.tray_theme = "default"

    @staticmethod
    def available_csr_button_themes():
        return ["default", "adwaita"]

    @staticmethod
    def apply_tray_icon_enabled(_enabled):
        pass

    @staticmethod
    def apply_tray_theme(_theme):
        pass

    @staticmethod
    def apply_theme(_theme):
        pass

    @staticmethod
    def refresh_tray():
        pass


class AppearanceSettingsUiTests(QtTestCase):

    def _controller(self, **states):
        model = FakeAppearanceSettingsModel(**states)
        with patch(
            "zapzap.features.settings.pages.appearance.controller."
            "AppearanceSettingsModel",
            return_value=model,
        ):
            page = AppearanceSettingsController()
        return page, model

    def test_compound_settings_have_explicit_group_labels_and_clear_copy(self):
        page = AppearanceSettingsView()

        self.assertEqual(
            page.tray_groupBox.title_label.text(),
            "Show tray icon",
        )
        self.assertEqual(
            page.notificationCounter_row.title_label.text(),
            "Unread counter",
        )
        self.assertEqual(page.tray_style_header.title_label.text(), "Icon style")
        self.assertEqual(
            page.csr_groupBox.title_label.text(),
            "Use custom decoration",
        )
        self.assertEqual(
            page.csr_theme_row.title_label.text(),
            "Button style",
        )
        self.assertEqual(
            page.csr_visible_buttons_group.header.title_label.text(),
            "Visible buttons",
        )
        self.assertEqual(
            page.csr_direction_row.title_label.text(),
            "Button position",
        )

    def test_child_groups_have_no_dividers_and_share_the_same_indent(self):
        page = AppearanceSettingsView()

        for group in (page.tray_options_group, page.csr_options_group):
            self.assertEqual(
                group.layout.contentsMargins().left(),
                SUBSETTING_INDENT,
            )
            self.assertFalse(any(
                isinstance(group.layout.itemAt(index).widget(), SettingsDivider)
                for index in range(group.layout.count())
            ))

    @staticmethod
    def _resize_to_width(widget, width):
        """Resize and deliver the event without going through the queue.

        The group is nested several layouts deep, so a posted resize races
        with the parent layout reassigning the geometry.
        """
        previous = widget.size()
        widget.resize(width, previous.height())
        QApplication.sendEvent(widget, QResizeEvent(widget.size(), previous))

    def test_visible_button_group_wraps_when_narrow(self):
        page = AppearanceSettingsView()
        group = page.csr_visible_buttons_group

        self._resize_to_width(group, 600)
        self.assertEqual(
            group.rows_layout.direction(),
            QBoxLayout.Direction.LeftToRight,
        )
        self.assertTrue(all(
            row.maximumWidth() == group.MAX_COLUMN_WIDTH
            for row in group.rows
        ))

        self._resize_to_width(group, 420)
        self.assertEqual(
            group.rows_layout.direction(),
            QBoxLayout.Direction.TopToBottom,
        )
        self.assertTrue(all(
            row.maximumWidth() > group.MAX_COLUMN_WIDTH
            for row in group.rows
        ))
        page.close()

    def test_visible_button_group_keeps_independent_switches(self):
        page = AppearanceSettingsView()
        group = page.csr_visible_buttons_group

        self.assertIs(
            group.rows[0].checkbox,
            page.csr_show_minimize_checkBox,
        )
        self.assertIs(
            group.rows[1].checkbox,
            page.csr_show_maximize_checkBox,
        )
        page.close()

    def test_disabled_masters_preserve_all_child_values(self):
        page, model = self._controller(
            tray_enabled=False,
            csr_enabled=False,
        )

        self.assertFalse(page.tray_options_group.isEnabled())
        self.assertFalse(page.csr_options_group.isEnabled())
        self.assertTrue(page.notificationCounter.isChecked())
        self.assertTrue(page.csr_show_minimize_checkBox.isChecked())
        self.assertFalse(page.csr_show_maximize_checkBox.isChecked())

        page.tray_groupBox.checkbox.setChecked(True)
        page.csr_groupBox.checkbox.setChecked(True)

        self.assertTrue(page.tray_options_group.isEnabled())
        self.assertTrue(page.csr_options_group.isEnabled())
        self.assertTrue(page.notificationCounter.isChecked())
        self.assertTrue(page.csr_show_minimize_checkBox.isChecked())
        self.assertFalse(page.csr_show_maximize_checkBox.isChecked())
        self.assertTrue(model.notification_counter_enabled)
        self.assertTrue(model.csr_show_minimize_button)
        self.assertFalse(model.csr_show_maximize_button)

    def test_child_controls_have_accessible_names(self):
        page = AppearanceSettingsView()

        for row in (
            page.tray_groupBox,
            page.notificationCounter_row,
            page.csr_groupBox,
            page.csr_theme_row,
            page.csr_show_minimize_row,
            page.csr_show_maximize_row,
            page.csr_direction_row,
        ):
            self.assertEqual(
                row.control.accessibleName(),
                row.title_label.text(),
            )
            self.assertTrue(row.control.accessibleDescription())


if __name__ == "__main__":
    unittest.main()
