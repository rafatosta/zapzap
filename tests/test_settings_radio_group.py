"""Tests for shared dividers inside settings radio groups."""

import unittest

from qt_test_case import QtTestCase
from zapzap.ui.components import (
    SettingsDivider,
    SettingsRadioGroup,
)
from zapzap.ui.primitives import RadioButton


class SettingsRadioGroupTests(QtTestCase):

    def test_radio_options_use_shared_dividers(self):
        buttons = (
            RadioButton("First"),
            RadioButton("Second"),
            RadioButton("Third"),
        )

        group = SettingsRadioGroup(*buttons)

        self.assertEqual(group.layout.count(), 5)
        self.assertIs(group.layout.itemAt(0).widget(), buttons[0])
        self.assertIsInstance(
            group.layout.itemAt(1).widget(),
            SettingsDivider,
        )
        self.assertIs(group.layout.itemAt(2).widget(), buttons[1])
        self.assertIsInstance(
            group.layout.itemAt(3).widget(),
            SettingsDivider,
        )
        self.assertIs(group.layout.itemAt(4).widget(), buttons[2])

    def test_single_radio_option_has_no_divider(self):
        group = SettingsRadioGroup(RadioButton("Only option"))

        self.assertEqual(group.layout.count(), 1)
        self.assertNotIsInstance(
            group.layout.itemAt(0).widget(),
            SettingsDivider,
        )


if __name__ == "__main__":
    unittest.main()
