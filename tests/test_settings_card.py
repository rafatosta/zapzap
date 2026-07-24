"""Tests for the shared settings card row separators."""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QWidget

from zapzap.features.settings.components import SettingsCard, SettingsDivider


class SettingsCardTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_add_row_inserts_shared_divider_between_rows(self):
        card = SettingsCard()
        first_row = QWidget()
        second_row = QWidget()

        card.add_row(first_row)
        card.add_row(second_row)

        self.assertEqual(card.layout.count(), 3)
        self.assertIs(card.layout.itemAt(0).widget(), first_row)
        self.assertIsInstance(
            card.layout.itemAt(1).widget(),
            SettingsDivider,
        )
        self.assertIs(card.layout.itemAt(2).widget(), second_row)

    def test_add_row_can_disable_divider(self):
        card = SettingsCard()
        first_row = QWidget()
        supporting_row = QWidget()

        card.add_row(first_row)
        card.add_row(supporting_row, divider=False)

        self.assertEqual(card.layout.count(), 2)
        self.assertIs(card.layout.itemAt(1).widget(), supporting_row)


if __name__ == "__main__":
    unittest.main()
