"""Tests for the reusable ZapZap segmented control."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QLineEdit, QVBoxLayout, QWidget

from qt_test_case import QtTestCase
from zapzap.ui.primitives import (
    SegmentOption,
    SegmentedControl,
    SegmentedControlRadius,
    SegmentedControlSize,
)


class SegmentedControlTests(QtTestCase):

    OPTIONS = (
        SegmentOption("first", "First"),
        SegmentOption("second", "Second"),
        SegmentOption("third", "Third"),
    )

    def test_initial_value_programmatic_selection_and_signals(self):
        control = SegmentedControl(self.OPTIONS, value="second")
        values = []
        indexes = []
        control.valueChanged.connect(values.append)
        control.currentIndexChanged.connect(indexes.append)

        self.assertEqual(control.value(), "second")
        self.assertEqual(control.currentIndex(), 1)
        self.assertEqual(control.options(), self.OPTIONS)
        self.assertTrue(control.segmentButton(1).isChecked())

        control.setValue("third")
        self.assertEqual(values, ["third"])
        self.assertEqual(indexes, [2])

        control.setCurrentIndex(2)
        self.assertEqual(values, ["third"])
        self.assertEqual(indexes, [2])

    def test_mouse_click_changes_value_without_redundant_signal(self):
        control = SegmentedControl(self.OPTIONS)
        values = []
        control.valueChanged.connect(values.append)
        control.show()

        QTest.mouseClick(
            control.segmentButton(1),
            Qt.MouseButton.LeftButton,
        )
        QTest.mouseClick(
            control.segmentButton(1),
            Qt.MouseButton.LeftButton,
        )

        self.assertEqual(control.value(), "second")
        self.assertEqual(values, ["second"])
        self.assertEqual(
            control.focusPolicy(),
            Qt.FocusPolicy.StrongFocus,
        )

    def test_keyboard_navigation_skips_disabled_options(self):
        control = SegmentedControl(
            (
                SegmentOption("first", "First"),
                SegmentOption("second", "Second", enabled=False),
                SegmentOption("third", "Third"),
            )
        )
        control.show()
        control.setFocus()

        QTest.keyClick(control, Qt.Key.Key_Right)
        self.assertEqual(control.value(), "third")

        QTest.keyClick(control, Qt.Key.Key_Left)
        self.assertEqual(control.value(), "first")

        QTest.keyClick(control, Qt.Key.Key_End)
        self.assertEqual(control.value(), "third")

        QTest.keyClick(control, Qt.Key.Key_Home)
        self.assertEqual(control.value(), "first")

        QTest.keyClick(control, Qt.Key.Key_Space)
        QTest.keyClick(control, Qt.Key.Key_Return)
        self.assertEqual(control.value(), "first")

    def test_tab_uses_one_control_focus_stop(self):
        window = QWidget()
        layout = QVBoxLayout(window)
        before = QLineEdit()
        control = SegmentedControl(self.OPTIONS)
        after = QLineEdit()
        layout.addWidget(before)
        layout.addWidget(control)
        layout.addWidget(after)
        window.show()
        window.activateWindow()
        before.setFocus()
        self.app.processEvents()

        QTest.keyClick(before, Qt.Key.Key_Tab)
        self.app.processEvents()

        self.assertIs(self.app.focusWidget(), control)
        self.assertTrue(all(
            control.segmentButton(index).focusPolicy()
            == Qt.FocusPolicy.NoFocus
            for index in range(3)
        ))

    def test_invalid_values_and_options_are_rejected(self):
        control = SegmentedControl(self.OPTIONS)

        with self.assertRaises(ValueError):
            control.setValue("missing")
        with self.assertRaises(IndexError):
            control.setCurrentIndex(99)
        with self.assertRaises(TypeError):
            control.setOptions(("not-an-option",))
        with self.assertRaises(ValueError):
            control.setOptions(
                (
                    SegmentOption("same", "First"),
                    SegmentOption("same", "Duplicate"),
                )
            )
        with self.assertRaises(ValueError):
            SegmentedControl((SegmentOption(None, "None"),))

    def test_replacing_options_preserves_or_rehomes_selection(self):
        control = SegmentedControl(self.OPTIONS, value="second")
        values = []
        control.valueChanged.connect(values.append)

        control.setOptions(
            (
                SegmentOption("second", "Second renamed"),
                SegmentOption("fourth", "Fourth"),
            )
        )
        self.assertEqual(control.value(), "second")
        self.assertEqual(control.currentIndex(), 0)
        self.assertEqual(values, [])

        control.setOptions((SegmentOption("fourth", "Fourth"),))
        self.assertEqual(control.value(), "fourth")
        self.assertEqual(values, ["fourth"])

        control.setOptions(())
        self.assertIsNone(control.value())
        self.assertEqual(control.currentIndex(), -1)
        self.assertEqual(values, ["fourth", None])

    def test_individual_and_whole_control_disabled_states(self):
        control = SegmentedControl(self.OPTIONS)
        values = []
        control.valueChanged.connect(values.append)

        control.setOptionEnabled(0, False)
        self.assertFalse(control.optionEnabled(0))
        self.assertEqual(control.value(), "second")
        self.assertEqual(values, ["second"])
        with self.assertRaises(ValueError):
            control.setCurrentIndex(0)

        control.setOptionEnabled(1, False)
        control.setOptionEnabled(2, False)
        self.assertIsNone(control.value())
        self.assertFalse(any(
            control.segmentButton(index).isChecked()
            for index in range(3)
        ))

        control.setOptionEnabled(2, True)
        self.assertEqual(control.value(), "third")
        control.setEnabled(False)
        self.assertEqual(control.value(), "third")
        self.assertFalse(control.segmentButton(2).isEnabled())

    def test_sizes_radii_uniformity_and_long_text(self):
        heights = []
        widths = []
        for size in SegmentedControlSize:
            control = SegmentedControl(
                (
                    SegmentOption("short", "Short"),
                    SegmentOption(
                        "long",
                        "A translated label that is substantially longer",
                    ),
                ),
                size=size,
            )
            heights.append(control.sizeHint().height())
            widths.append(control.sizeHint().width())
            self.assertEqual(
                control.segmentButton(0).minimumWidth(),
                control.segmentButton(1).minimumWidth(),
            )

        self.assertEqual(heights, sorted(heights))
        self.assertEqual(widths, sorted(widths))

        control = SegmentedControl(self.OPTIONS, uniform=False)
        self.assertLess(
            control.segmentButton(0).minimumWidth(),
            control.sizeHint().width(),
        )
        for radius in SegmentedControlRadius:
            control.setRadius(radius)
            self.assertEqual(control.radius(), radius)

        control.setControlSize(SegmentedControlSize.LARGE)
        self.assertEqual(
            control.controlSize(),
            SegmentedControlSize.LARGE,
        )
        self.assertFalse(control.uniformSegments())
        control.setUniformSegments(True)
        self.assertTrue(control.uniformSegments())

    def test_palette_rendering_and_accessibility_use_native_state(self):
        control = SegmentedControl(self.OPTIONS, value="second")
        control.setAccessibleName("Account status")
        control.resize(control.sizeHint())

        for background, button, highlight in (
            ("#ffffff", "#f4f4f5", "#2563eb"),
            ("#202020", "#353535", "#60a5fa"),
        ):
            with self.subTest(background=background):
                palette = control.palette()
                palette.setColor(
                    QPalette.ColorRole.AlternateBase,
                    QColor(background),
                )
                palette.setColor(
                    QPalette.ColorRole.Button,
                    QColor(button),
                )
                palette.setColor(
                    QPalette.ColorRole.Highlight,
                    QColor(highlight),
                )
                control.setPalette(palette)
                control.show()
                self.app.processEvents()

                self.assertFalse(control.grab().isNull())
                self.assertEqual(control.accessibleName(), "Account status")
                self.assertEqual(control.accessibleDescription(), "Second")
                self.assertEqual(
                    control.segmentButton(1).accessibleName(),
                    "Second",
                )
                self.assertTrue(control.segmentButton(1).isCheckable())
                self.assertTrue(control.segmentButton(1).isChecked())
                self.assertEqual(
                    control.focusPolicy(),
                    Qt.FocusPolicy.StrongFocus,
                )
                self.assertEqual(
                    control.segmentButton(1).focusPolicy(),
                    Qt.FocusPolicy.NoFocus,
                )


if __name__ == "__main__":
    import unittest

    unittest.main()
