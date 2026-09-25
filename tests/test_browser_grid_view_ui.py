from unittest.mock import Mock

from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

from qt_test_case import QtTestCase
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.features.accounts.domain.user import User
from zapzap.ui.components.browser_grid_view import AccountCard
from zapzap.ui.components.browser_page_button import BrowserPageButton


class BrowserGridViewUiTests(QtTestCase):
    def test_card_reuses_avatar_name_and_unread_state(self):
        user = User(name="Rafael", icon=UserIcon.ICON_DEFAULT)
        button = BrowserPageButton(user)
        card = AccountCard(user, button)
        card.resize(260, 280)
        card.show()

        self.assertEqual(card.name_label.text(), "Rafael")
        self.assertFalse(card.unread_label.isVisible())

        button.update_notifications(5)
        self.assertEqual(card.unread_label.text(), "5")
        self.assertTrue(card.unread_label.isVisible())

    def test_click_uses_the_persisted_account_id(self):
        user = User(id="account-id", name="Rafael", icon=UserIcon.ICON_DEFAULT)
        button = BrowserPageButton(user)
        card = AccountCard(user, button)
        callback = Mock()
        card.clicked.connect(lambda: callback(user.id))
        card.show()

        QTest.mouseClick(
            card,
            Qt.MouseButton.LeftButton,
            pos=card.rect().center(),
        )

        callback.assert_called_once_with("account-id")