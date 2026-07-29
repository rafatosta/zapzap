"""Regression tests for account status indicators in the browser sidebar."""

from unittest.mock import patch

from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QImage, QPalette
from PyQt6.QtTest import QTest

from qt_test_case import QtTestCase
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.core.theme.theme_manager import ThemeManager
from zapzap.features.accounts.domain.user import User
from zapzap.features.browser.components.browser_page_button import (
    AccountIndicatorState,
    BrowserPageButton,
)


class BrowserPageButtonUiTests(QtTestCase):

    @staticmethod
    def _user(icon=UserIcon.ICON_DEFAULT, enabled=True):
        return User(name="Test account", icon=icon, enable=enabled)

    def test_unread_count_is_not_rendered_inside_avatar(self):
        button = BrowserPageButton(self._user())
        button.update_notifications(42)

        rendered_avatar = button.icon().pixmap(128, 128).toImage()
        plain_avatar = UserIcon.get_icon(
            UserIcon.ICON_DEFAULT,
        ).pixmap(128, 128).toImage()
        numbered_avatar = UserIcon.get_icon(
            UserIcon.ICON_DEFAULT,
            qtd=42,
        ).pixmap(128, 128).toImage()

        self.assertEqual(rendered_avatar, plain_avatar)
        self.assertNotEqual(rendered_avatar, numbered_avatar)
        self.assertEqual(
            button.indicator_state,
            AccountIndicatorState.ACTIVITY,
        )

    def test_real_account_states_map_to_activity_inactive_or_no_dot(self):
        button = BrowserPageButton(self._user())
        self.assertEqual(button.indicator_state, AccountIndicatorState.NONE)

        button.update_notifications(1)
        self.assertEqual(
            button.indicator_state,
            AccountIndicatorState.ACTIVITY,
        )

        button.user.enable = False
        button.update_user_icon()
        self.assertEqual(
            button.indicator_state,
            AccountIndicatorState.INACTIVE,
        )

    def test_indicator_is_proportional_top_right_and_clear_of_card_edge(self):
        button = BrowserPageButton(self._user())
        button.update_notifications(3)
        card_gap = max(
            button.MIN_INDICATOR_CARD_GAP,
            button.BUTTON_SIZE * button.INDICATOR_CARD_GAP_RATIO,
        )

        for icon_size in (28, button.ICON_SIZE, 40):
            with self.subTest(icon_size=icon_size):
                button.setIconSize(QSize(icon_size, icon_size))
                indicator = button.indicator_rect()
                avatar = QRectF(
                    (button.width() - icon_size) / 2,
                    (button.height() - icon_size) / 2,
                    icon_size,
                    icon_size,
                )
                dot_size = max(
                    button.MIN_INDICATOR_SIZE,
                    icon_size * button.INDICATOR_RATIO,
                )

                self.assertGreaterEqual(dot_size, icon_size * 0.20)
                self.assertLessEqual(dot_size, icon_size * 0.25)
                self.assertGreater(indicator.left(), button.width() / 2)
                self.assertLess(indicator.bottom(), button.height() / 2)
                self.assertGreaterEqual(indicator.top(), card_gap)
                self.assertLessEqual(
                    indicator.right(),
                    button.width() - card_gap,
                )
                self.assertTrue(indicator.intersects(avatar))
                self.assertFalse(avatar.contains(indicator))

        self.assertEqual(button.minimumWidth(), button.BUTTON_SIZE)
        self.assertEqual(button.maximumWidth(), button.BUTTON_SIZE)
        self.assertEqual(button.minimumHeight(), button.BUTTON_SIZE)
        self.assertEqual(button.maximumHeight(), button.BUTTON_SIZE)

        normal_rect = button.indicator_rect()
        button.selected()
        self.assertEqual(button.indicator_rect(), normal_rect)

    def test_indicator_uses_theme_activity_and_card_background_colors(self):
        button = BrowserPageButton(self._user())
        button.update_notifications(2)
        palette = button.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#fafafa"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#303030"))
        button.setPalette(palette)

        with patch.object(
            ThemeManager,
            "get_color",
            return_value="#007C83",
        ):
            self.assertEqual(
                button.indicator_color(),
                QColor("#007C83"),
            )
        self.assertEqual(
            button._indicator_border_color(),
            QColor("#fafafa"),
        )

        button.selected()
        self.assertEqual(
            button._indicator_border_color(),
            QColor("#303030"),
        )
        self.assertIn("palette(highlight)", button.styleSheet())

        button._is_selected = False
        button._apply_state_style(hovered=True)
        self.assertEqual(
            button._indicator_border_color(),
            QColor("#303030"),
        )
        button._apply_state_style(pressed=True)
        self.assertEqual(
            button._indicator_border_color(),
            palette.color(QPalette.ColorRole.Highlight),
        )

    def test_activity_color_is_distinct_from_selection_in_both_themes(self):
        for colors in (
            ThemeManager._LIGHT_PALETTE_COLORS,
            ThemeManager._DARK_PALETTE_COLORS,
        ):
            with self.subTest(activity=colors["activity"]):
                self.assertTrue(QColor(colors["activity"]).isValid())
                self.assertNotEqual(colors["activity"], colors["highlight"])

    def test_indicator_does_not_change_click_or_keyboard_focus(self):
        button = BrowserPageButton(self._user())
        button.update_notifications(1)
        clicks = []
        button.clicked.connect(lambda: clicks.append(True))

        button.show()
        QTest.mouseClick(
            button,
            Qt.MouseButton.LeftButton,
            pos=button.rect().center(),
        )

        self.assertEqual(clicks, [True])
        self.assertEqual(button.focusPolicy(), Qt.FocusPolicy.StrongFocus)
        self.assertEqual(button.findChildren(type(button)), [])

    def test_svg_and_photo_avatars_share_the_same_overlay_geometry(self):
        photo = QImage(320, 240, QImage.Format.Format_RGB32)
        photo.fill(QColor("#6d28d9"))
        photo_data = UserIcon.persisted_image(
            UserIcon.ICON_DEFAULT,
            UserIcon.photo_from_image(photo),
            use_photo=True,
        )
        svg_button = BrowserPageButton(self._user())
        photo_button = BrowserPageButton(self._user(photo_data))

        svg_button.update_notifications(1)
        photo_button.update_notifications(1)

        self.assertEqual(
            svg_button.indicator_rect(),
            photo_button.indicator_rect(),
        )
        self.assertFalse(photo_button.icon().isNull())

    def test_accessibility_describes_state_without_relying_on_color(self):
        button = BrowserPageButton(self._user())
        button.update_notifications(7)

        self.assertEqual(button.accessibleName(), "Test account")
        self.assertIn("7", button.accessibleDescription())

        button.user.enable = False
        button.update_user_icon()
        self.assertIn("disabled", button.accessibleDescription().lower())
