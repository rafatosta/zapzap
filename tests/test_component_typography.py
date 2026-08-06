"""Regression tests for shared component font weights."""

import unittest

from PyQt6.QtGui import QFont

from qt_test_case import QtTestCase
from zapzap.features.settings.pages.advanced_customizations.view import (
    AdvancedCustomizationsSettingsView,
)
from zapzap.features.shortcuts.view import ShortcutsView
from zapzap.ui.primitives import CheckBox, ComboBox, LineEdit, TextEdit
from zapzap.ui.components.main_window import MainWindowView


class ComponentTypographyTests(QtTestCase):

    def test_body_text_components_use_normal_weight(self):
        components = (LineEdit(), TextEdit(), CheckBox(), ComboBox())

        for component in components:
            with self.subTest(component=type(component).__name__):
                self.assertEqual(
                    component.font().weight(),
                    QFont.Weight.Normal,
                )

    def test_combo_box_popup_uses_normal_weight(self):
        combo_box = ComboBox()

        self.assertEqual(
            combo_box.view().font().weight(),
            QFont.Weight.Normal,
        )

    def test_menu_bar_and_its_menus_use_normal_weight(self):
        window = MainWindowView()

        self.assertEqual(
            window.menubar.font().weight(),
            QFont.Weight.Normal,
        )
        self.assertEqual(
            window.menuFile.font().weight(),
            QFont.Weight.Normal,
        )

    def test_shortcuts_dialog_uses_semantic_native_weights(self):
        dialog = ShortcutsView()

        self.assertEqual(
            dialog.groupBox.font().weight(),
            QFont.Weight.DemiBold,
        )
        self.assertEqual(
            dialog.table_whatsapp.font().weight(),
            QFont.Weight.Normal,
        )
        for button in dialog.buttonBox.buttons():
            self.assertEqual(
                button.font().weight(),
                QFont.Weight.Medium,
            )

    def test_customization_tabs_use_native_weight(self):
        page = AdvancedCustomizationsSettingsView()

        self.assertEqual(
            page.customization_tabs.tabBar().font().weight(),
            QFont.Weight.DemiBold,
        )
        for index in range(page.customization_tabs.count()):
            self.assertEqual(
                page.customization_tabs.widget(index).font().weight(),
                QFont.Weight.Normal,
            )


if __name__ == "__main__":
    unittest.main()
