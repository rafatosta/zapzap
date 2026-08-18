"""Transactional orchestration for the shared spellcheck language picker."""

from __future__ import annotations

from typing import Callable

from PyQt6.QtWidgets import QDialog, QWidget

from zapzap.features.dictionaries.dictionaries_manager import DictionariesManager
from zapzap.ui.components.spellcheck_language_picker_dialog import (
    SpellcheckLanguagePickerDialog,
)


def open_dictionary_settings() -> None:
    """Open the shared dictionary manager without a Settings dependency."""
    from zapzap.features.dictionaries.dictionary_manager import (
        open_dictionary_manager,
    )

    open_dictionary_manager()


def open_spellcheck_language_picker(
    parent: QWidget | None = None,
    *,
    on_applied: Callable[[], None] | None = None,
    on_manage: Callable[[], None] | None = None,
) -> bool:
    """Open the picker, committing its staged state only after acceptance."""
    options = DictionariesManager.options()
    original_selected = DictionariesManager.get_selected_languages()
    dialog = SpellcheckLanguagePickerDialog(
        options,
        original_selected,
        DictionariesManager.get_recent_languages(),
        parent,
        maximum_selected=DictionariesManager.MAX_SELECTED_LANGUAGES,
        maximum_recent=DictionariesManager.MAX_RECENT_LANGUAGES,
    )

    def manage_dictionaries():
        dialog.reject()
        (on_manage or open_dictionary_settings)()

    dialog.manage_button.clicked.connect(manage_dictionaries)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return False

    selected = dialog.selected_languages
    DictionariesManager.set_selected_languages(selected)
    newly_selected = [code for code in selected if code not in original_selected]
    recent_order = newly_selected + [
        code for code in selected if code not in newly_selected
    ]
    DictionariesManager.update_recent_languages(recent_order)
    if on_applied is not None:
        on_applied()
    return True
