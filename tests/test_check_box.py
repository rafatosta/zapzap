"""Behavior and rendering contracts for the shared CheckBox component."""

import unittest
from pathlib import Path

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QActionGroup, QColor, QFont, QImage, QPalette
from PyQt6.QtTest import QSignalSpy, QTest
from PyQt6.QtWidgets import QCheckBox, QMenu

from qt_test_case import QtTestCase
from zapzap.assets.themes.theme_stylesheet import ThemeStylesheet
from zapzap.features.donation.view import DonationView
from zapzap.ui.components import (
    CheckBox,
    CheckBoxSize,
    CheckBoxTone,
    CheckBoxVariant,
)


class CheckBoxTests(QtTestCase):

    def test_default_api_remains_qcheckbox_compatible(self):
        checkbox = CheckBox("Option")

        self.assertIsInstance(checkbox, QCheckBox)
        self.assertEqual(checkbox.text(), "Option")
        self.assertEqual(checkbox.variant(), CheckBoxVariant.CLASSIC)
        self.assertEqual(checkbox.controlSize(), CheckBoxSize.MEDIUM)
        self.assertEqual(checkbox.tone(), CheckBoxTone.ACCENT)
        self.assertEqual(checkbox.font().weight(), QFont.Weight.Normal)
        self.assertEqual(checkbox.focusPolicy(), Qt.FocusPolicy.StrongFocus)

    def test_typed_visual_properties_accept_enums_and_stable_values(self):
        checkbox = CheckBox()
        initial = checkbox.sizeHint()

        checkbox.setVariant("soft")
        checkbox.setControlSize("large")
        checkbox.setTone("neutral")

        self.assertEqual(checkbox.variant(), CheckBoxVariant.SOFT)
        self.assertEqual(checkbox.controlSize(), CheckBoxSize.LARGE)
        self.assertEqual(checkbox.tone(), CheckBoxTone.NEUTRAL)
        self.assertGreater(checkbox.sizeHint().height(), initial.height())
        with self.assertRaises(ValueError):
            checkbox.setVariant("unknown")

    def test_mouse_click_on_text_preserves_native_signals(self):
        checkbox = CheckBox("A translated option with a long label")
        toggled = QSignalSpy(checkbox.toggled)
        state_changed = QSignalSpy(checkbox.stateChanged)
        checkbox.show()
        self.app.processEvents()

        QTest.mouseClick(
            checkbox,
            Qt.MouseButton.LeftButton,
            pos=QPoint(checkbox.width() - 2, checkbox.height() // 2),
        )

        self.assertTrue(checkbox.isChecked())
        self.assertEqual(len(toggled), 1)
        self.assertEqual(len(state_changed), 1)

    def test_keyboard_space_and_focus_use_native_checkbox_behavior(self):
        checkbox = CheckBox("Keyboard option")
        checkbox.show()
        checkbox.setFocus()
        self.app.processEvents()

        self.assertTrue(checkbox.hasFocus())
        QTest.keyClick(checkbox, Qt.Key.Key_Space)

        self.assertTrue(checkbox.isChecked())
        focus = checkbox.focusRect()
        self.assertGreaterEqual(focus.left(), 0)
        self.assertGreaterEqual(focus.top(), 0)
        self.assertLessEqual(focus.right(), checkbox.width())
        self.assertLessEqual(focus.bottom(), checkbox.height())

    def test_tristate_preserves_partial_state_and_distinct_rendering(self):
        checkbox = CheckBox("Tri-state")
        checkbox.setTristate(True)
        checkbox.resize(checkbox.sizeHint())
        checkbox.show()

        checkbox.setCheckState(Qt.CheckState.Unchecked)
        unchecked = checkbox.grab().toImage()
        checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
        partial = checkbox.grab().toImage()
        checkbox.setCheckState(Qt.CheckState.Checked)
        checked = checkbox.grab().toImage()

        self.assertEqual(
            checkbox.checkState(),
            Qt.CheckState.Checked,
        )
        self.assertNotEqual(unchecked, partial)
        self.assertNotEqual(partial, checked)

    def test_disabled_state_ignores_input_and_restores_interaction(self):
        checkbox = CheckBox("Disabled")
        checkbox.resize(checkbox.sizeHint())
        checkbox.show()
        checkbox.setDisabled(True)
        self.app.processEvents()

        QTest.mouseClick(
            checkbox,
            Qt.MouseButton.LeftButton,
            pos=checkbox.rect().center(),
        )
        self.assertFalse(checkbox.isChecked())
        self.assertEqual(
            checkbox.cursor().shape(),
            Qt.CursorShape.ArrowCursor,
        )

        checkbox.setEnabled(True)
        QTest.mouseClick(
            checkbox,
            Qt.MouseButton.LeftButton,
            pos=checkbox.rect().center(),
        )
        self.assertTrue(checkbox.isChecked())

    def test_variants_have_distinct_checked_and_unchecked_surfaces(self):
        checked_images = []
        unchecked_images = []
        for variant in CheckBoxVariant:
            checkbox = CheckBox("Variant", variant=variant)
            checkbox.resize(checkbox.sizeHint())
            checkbox.show()
            checkbox.setChecked(False)
            unchecked_images.append(checkbox.grab().toImage())
            checkbox.setChecked(True)
            checked_images.append(checkbox.grab().toImage())

        for images in (checked_images, unchecked_images):
            self.assertTrue(
                all(
                    images[first] != images[second]
                    for first in range(len(images))
                    for second in range(first + 1, len(images))
                )
            )

    def test_hover_pressed_and_focus_have_distinct_feedback(self):
        checkbox = CheckBox("Interactive")
        checkbox.resize(checkbox.sizeHint())
        checkbox.show()
        self.app.processEvents()

        QTest.mouseMove(checkbox, checkbox.rect().center())
        self.app.processEvents()
        hovered = checkbox.grab().toImage()

        QTest.mousePress(
            checkbox,
            Qt.MouseButton.LeftButton,
            pos=checkbox.rect().center(),
        )
        pressed = checkbox.grab().toImage()
        QTest.mouseRelease(
            checkbox,
            Qt.MouseButton.LeftButton,
            pos=checkbox.rect().center(),
        )

        checkbox.setFocus()
        self.app.processEvents()
        focused = checkbox.grab().toImage()

        self.assertNotEqual(hovered, pressed)
        self.assertNotEqual(pressed, focused)

    def test_sizes_keep_square_indicator_and_larger_hit_area(self):
        previous_side = 0
        for size in CheckBoxSize:
            with self.subTest(size=size):
                checkbox = CheckBox(size=size)
                checkbox.resize(checkbox.sizeHint())
                indicator = checkbox.indicatorRect()

                self.assertEqual(indicator.width(), indicator.height())
                self.assertGreater(indicator.width(), previous_side)
                self.assertGreater(checkbox.height(), indicator.height())
                previous_side = indicator.width()

    def test_state_changes_do_not_move_indicator_and_large_font_is_not_clipped(self):
        checkbox = CheckBox("Long translated checkbox label")
        font = checkbox.font()
        font.setPixelSize(font.pixelSize() + 6)
        checkbox.setFont(font)
        checkbox.resize(checkbox.sizeHint())
        before = checkbox.indicatorRect()
        unchecked_size = checkbox.sizeHint()

        checkbox.setChecked(True)
        checked_size = checkbox.sizeHint()

        self.assertEqual(checkbox.indicatorRect(), before)
        self.assertEqual(checked_size, unchecked_size)
        self.assertGreaterEqual(
            checkbox.height(),
            checkbox.fontMetrics().height(),
        )

    def test_accent_neutral_and_palette_changes_are_not_hardcoded(self):
        checkbox = CheckBox()
        checkbox.setChecked(True)
        palette = checkbox.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#d946ef"))
        palette.setColor(
            QPalette.ColorRole.HighlightedText,
            QColor("#101010"),
        )
        checkbox.setPalette(palette)

        accent = checkbox._state_colors()
        self.assertEqual(accent["background"], QColor("#d946ef"))
        self.assertEqual(accent["mark"], QColor("#101010"))

        checkbox.setTone(CheckBoxTone.NEUTRAL)
        neutral = checkbox._state_colors()
        self.assertNotEqual(neutral["background"], accent["background"])

    def test_rtl_places_indicator_on_the_right(self):
        checkbox = CheckBox("خيار")
        checkbox.resize(checkbox.sizeHint())
        ltr = checkbox.indicatorRect()

        checkbox.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        rtl = checkbox.indicatorRect()

        self.assertLess(ltr.center().x(), checkbox.width() / 2)
        self.assertGreater(rtl.center().x(), checkbox.width() / 2)

    def test_donation_uses_the_discreet_soft_variant(self):
        donation = DonationView()

        self.assertEqual(
            donation.donationMessage.variant(),
            CheckBoxVariant.SOFT,
        )
        self.assertEqual(
            donation.donationMessage.controlSize(),
            CheckBoxSize.SMALL,
        )

    def test_menu_indicators_match_checkbox_and_radio_semantics(self):
        stylesheet = ThemeStylesheet.get_global_components_stylesheet()

        self.assertIn(
            "QMenu::indicator:non-exclusive:checked",
            stylesheet,
        )
        self.assertIn(
            "QMenu::indicator:exclusive:checked",
            stylesheet,
        )
        self.assertIn(
            f"width: {CheckBox.SIZE_TOKENS[CheckBoxSize.SMALL]['indicator']}px",
            stylesheet,
        )
        self.assertIn(
            f"border-radius: "
            f"{CheckBox.SIZE_TOKENS[CheckBoxSize.SMALL]['radius']}px",
            stylesheet,
        )
        self.assertNotIn("@menu-", stylesheet)
        self.assertIn("menu_check.svg", stylesheet)
        self.assertIn("menu_radio.svg", stylesheet)
        for icon_path in (
            ThemeStylesheet._MENU_CHECK_ICON,
            ThemeStylesheet._MENU_RADIO_ICON,
        ):
            with self.subTest(icon_path=icon_path):
                self.assertNotIn("file://", icon_path)
                self.assertTrue(Path(icon_path).is_file())
                self.assertFalse(QImage(icon_path).isNull())

        original_stylesheet = self.app.styleSheet()
        self.addCleanup(self.app.setStyleSheet, original_stylesheet)
        self.app.setStyleSheet(stylesheet)

        checkbox_image = self._render_checked_menu_action(exclusive=False)
        radio_image = self._render_checked_menu_action(exclusive=True)

        self.assertEqual(checkbox_image.size(), radio_image.size())
        self.assertNotEqual(checkbox_image, radio_image)

    def _render_checked_menu_action(self, *, exclusive):
        menu = QMenu()
        action = menu.addAction("Option")
        action.setCheckable(True)
        if exclusive:
            group = QActionGroup(menu)
            group.setExclusive(True)
            group.addAction(action)
        action.setChecked(True)

        menu.show()
        self.app.processEvents()
        image = menu.grab().toImage()
        menu.close()
        return image


if __name__ == "__main__":
    unittest.main()
