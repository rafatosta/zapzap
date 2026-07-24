"""Tests for the shared settings card row separators."""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QWidget

from zapzap.features.settings.components import (
    SUBSETTING_INDENT,
    SettingsCard,
    SettingsDivider,
    SettingsSubgroup,
)


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

    def test_add_group_indents_children_without_full_width_dividers(self):
        card = SettingsCard()
        parent_row = QWidget()
        first_child = QWidget()
        second_child = QWidget()

        subgroup = card.add_group(
            parent_row,
            (first_child, second_child),
        )

        self.assertIsInstance(subgroup, SettingsSubgroup)
        self.assertEqual(card.layout.count(), 2)
        self.assertIs(card.layout.itemAt(0).widget(), parent_row)
        self.assertIs(card.layout.itemAt(1).widget(), subgroup)
        self.assertEqual(
            subgroup.layout.contentsMargins().left(),
            SUBSETTING_INDENT,
        )
        self.assertEqual(subgroup.layout.count(), 2)
        self.assertFalse(any(
            isinstance(subgroup.layout.itemAt(index).widget(), SettingsDivider)
            for index in range(subgroup.layout.count())
        ))

    def test_group_can_separate_equivalent_children_and_next_top_level_item(self):
        card = SettingsCard()
        parent_row = QWidget()
        children = (QWidget(), QWidget(), QWidget())
        next_row = QWidget()

        subgroup = card.add_group(
            parent_row,
            children,
            child_dividers=True,
        )
        card.add_row(next_row)

        self.assertEqual(subgroup.layout.count(), 5)
        self.assertIsInstance(
            subgroup.layout.itemAt(1).widget(),
            SettingsDivider,
        )
        self.assertIsInstance(
            subgroup.layout.itemAt(3).widget(),
            SettingsDivider,
        )
        self.assertEqual(card.layout.count(), 4)
        self.assertIsInstance(card.layout.itemAt(2).widget(), SettingsDivider)
        self.assertIs(card.layout.itemAt(3).widget(), next_row)
        self.assertNotIsInstance(
            card.layout.itemAt(card.layout.count() - 1).widget(),
            SettingsDivider,
        )


if __name__ == "__main__":
    unittest.main()
