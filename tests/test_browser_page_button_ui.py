"""Regression tests for account status indicators in the browser sidebar."""

from unittest.mock import patch

from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QImage, QPalette
from PyQt6.QtTest import QTest

from qt_test_case import QtTestCase
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.core.theme.theme_manager import ThemeManager
from zapzap.features.accounts.domain.user import User
from zapzap.ui.components.browser_page_button import (
    AccountIndicatorState,
    BrowserPageButton,
)


class BrowserPageButtonUiTests(QtTestCase):

    @staticmethod
    def _user(icon=UserIcon.ICON_DEFAULT, enabled=True):
        return User(name="Test account", icon=icon, enable=enabled)

    @staticmethod
    def _photo(color):
        image = QImage(320, 240, QImage.Format.Format_RGB32)
        image.fill(QColor(color))
        return UserIcon.photo_from_image(image)

    @staticmethod
    def _avatar_center(button):
        image = button.icon().pixmap(128, 128).toImage()
        return image.pixelColor(image.width() // 2, image.height() // 2)

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

    def test_indicator_is_limited_to_active_unmuted_accounts_with_activity(self):
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
            AccountIndicatorState.NONE,
        )

        button.user.enable = True
        with patch(
            "zapzap.ui.components.browser_page_button."
            "SettingsManager.get",
            return_value=False,
        ):
            button.update_user_icon()
            self.assertEqual(
                button.indicator_state,
                AccountIndicatorState.NONE,
            )
            self.assertFalse(
                self._avatar_center(button).red()
                == self._avatar_center(button).green()
                == self._avatar_center(button).blue()
            )
            self.assertIn(
                "muted",
                button.accessibleDescription().lower(),
            )

    def test_disabled_photo_is_grayscale_translucent_and_has_no_indicator(self):
        user = self._user(self._photo("#e11d48"))
        button = BrowserPageButton(user)
        active_color = self._avatar_center(button)

        self.assertNotEqual(active_color.red(), active_color.green())
        self.assertEqual(active_color.alpha(), 255)

        user.enable = False
        button.update_notifications(9)
        inactive_color = self._avatar_center(button)

        self.assertEqual(inactive_color.red(), inactive_color.green())
        self.assertEqual(inactive_color.green(), inactive_color.blue())
        self.assertAlmostEqual(
            inactive_color.alpha() / active_color.alpha(),
            button.INACTIVE_AVATAR_OPACITY,
            delta=0.01,
        )
        self.assertEqual(button.number_notifications, 9)
        self.assertEqual(button.indicator_state, AccountIndicatorState.NONE)

        inactive_avatar = button.icon().pixmap(128, 128).toImage()
        inactive_cache_key = button.icon().cacheKey()
        button.update_user_icon()
        self.assertEqual(button.icon().cacheKey(), inactive_cache_key)

        button.selected()
        self.assertEqual(
            button.icon().pixmap(128, 128).toImage(),
            inactive_avatar,
        )
        self.assertIn("palette(highlight)", button.styleSheet())

    def test_disabled_avatar_effect_is_independent_from_card_theme(self):
        button = BrowserPageButton(
            self._user(self._photo("#f97316"), enabled=False)
        )
        expected = button.icon().pixmap(128, 128).toImage()

        for background, alternate in (
            ("#ffffff", "#eeeeee"),
            ("#202020", "#303030"),
        ):
            with self.subTest(background=background):
                palette = button.palette()
                palette.setColor(
                    QPalette.ColorRole.Window,
                    QColor(background),
                )
                palette.setColor(
                    QPalette.ColorRole.AlternateBase,
                    QColor(alternate),
                )
                button.setPalette(palette)
                button._apply_state_style()

                self.assertEqual(
                    button.icon().pixmap(128, 128).toImage(),
                    expected,
                )

    def test_disabled_account_remains_clickable_and_keyboard_focusable(self):
        button = BrowserPageButton(
            self._user(self._photo("#0891b2"), enabled=False)
        )
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
        self.assertTrue(button.isEnabled())

    def test_reactivation_and_avatar_change_refresh_the_visual_effect(self):
        user = self._user(self._photo("#ef4444"), enabled=False)
        button = BrowserPageButton(user)
        first_gray = self._avatar_center(button)

        user.icon = self._photo("#2563eb")
        button.update_user_icon()
        changed_gray = self._avatar_center(button)
        self.assertNotEqual(first_gray.red(), changed_gray.red())
        self.assertEqual(changed_gray.red(), changed_gray.green())
        self.assertEqual(changed_gray.green(), changed_gray.blue())

        user.enable = True
        button.update_user_icon()
        active_color = self._avatar_center(button)
        self.assertNotEqual(active_color.red(), active_color.blue())
        self.assertEqual(active_color.alpha(), 255)

    def test_disabled_effect_preserves_transparent_avatar_shape(self):
        for icon in (UserIcon.ICON_DEFAULT, self._photo("#7c3aed")):
            with self.subTest(photo=UserIcon.is_photo(icon)):
                button = BrowserPageButton(
                    self._user(icon, enabled=False)
                )
                image = button.icon().pixmap(128, 128).toImage()
                center = image.pixelColor(64, 64)

                self.assertEqual(center.red(), center.green())
                self.assertEqual(center.green(), center.blue())
                self.assertEqual(image.pixelColor(0, 0).alpha(), 0)

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
