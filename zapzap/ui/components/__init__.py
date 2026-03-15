"""
ZapZap UI components package.

Re-exports all public component classes so consumers can write:

    from zapzap.ui.components import PrimaryButton, SearchInput, AccountCard
"""

from .buttons import DangerButton, IconButton, PrimaryButton, SecondaryButton, TertiaryButton
from .cards import AccountCard, BaseCard, SettingCard
from .dialogs import BaseDialog, ConfirmDialog, InfoDialog, ToastNotification
from .inputs import FormField, SearchInput, ValidatedLineEdit

__all__ = [
    # buttons
    "PrimaryButton",
    "SecondaryButton",
    "TertiaryButton",
    "DangerButton",
    "IconButton",
    # inputs
    "SearchInput",
    "ValidatedLineEdit",
    "FormField",
    # cards
    "BaseCard",
    "AccountCard",
    "SettingCard",
    # dialogs
    "BaseDialog",
    "ConfirmDialog",
    "InfoDialog",
    "ToastNotification",
]
