from PyQt6.QtWidgets import QDialog, QHeaderView, QTableWidgetItem
from zapzap.views.ui_shortcuts_dialog import Ui_ShortcutsDialog
from gettext import gettext as _


class ShortcutsDialog(QDialog, Ui_ShortcutsDialog):
    # Shortcuts
    shortcuts = [
        # Conversations
        (_("New conversation"), "Ctrl + Alt + N"),
        (_("Mark as unread"), "Ctrl + Alt + Shift + U"),
        (_("Archive conversation"), "Ctrl + Alt + Shift + E"),
        (_("Pin conversation"), "Ctrl + Alt + Shift + P"),
        (_("Next conversation"), "Ctrl + Alt + Tab"),
        (_("Close conversation"), "Escape"),
        (_("Search in conversation"), "Ctrl + Alt + Shift + F"),
        (_("Previous conversation"), "Ctrl + Alt + Shift + Tab"),
        (_("Delete conversation"), "Ctrl + Alt + Backspace"),

        # Settings and Profiles
        (_("Profile and status"), "Ctrl + Alt + P"),
        (_("Settings"), "Ctrl + Alt + ,"),

        # Voice Messages
        (_("Decrease speed of selected voice message"), "Shift + ,"),
        (_("Increase speed of selected voice message"), "Shift + ."),

        # Media Tools
        (_("Emoji panel"), "Ctrl + Alt + E"),
        (_("Sticker panel"), "Ctrl + Alt + S"),
        (_("GIF panel"), "Ctrl + Alt + G"),

        # Others
        (_("Lock the app"), "Ctrl + Alt + L"),
        (_("Mute"), "Ctrl + Alt + Shift + M"),
        (_("Search"), "Ctrl + Alt + /"),
        (_("New group"), "Ctrl + Alt + Shift + N"),
        (_("Extended search"), "Alt + K"),
    ]

    shortcuts_zapzap = [
        # Settings and Navigation
        (_("Settings"), "Ctrl + P"),
        (_("Hide"), "Ctrl + W"),
        (_("Exit"), "Ctrl + Q"),

        # View
        (_("Fullscreen"), "F11"),
        (_("Reset zoom"), "Ctrl + 0"),
        (_("Zoom in"), "Ctrl + +"),
        (_("Zoom out"), "Ctrl + -"),

        # Refresh
        (_("Reload pages"), "F5"),
        (_("New conversation by phone number"), "Ctrl + M"),

        # Account
        (_("New account"), "Ctrl + U"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Adicionando atalhos na tabela
        self.add_shortcuts_to_table(self.table_whatsapp, self.shortcuts)
        self.add_shortcuts_to_table(self.table_zapzap, self.shortcuts_zapzap)

    def add_shortcuts_to_table(self, table, shortcuts):
        """Adiciona atalhos à tabela especificada."""
        table.setColumnCount(2)
        table.setRowCount(len(shortcuts))

        for row, (action, shortcut) in enumerate(shortcuts):
            table.setItem(row, 0, QTableWidgetItem(action))
            table.setItem(row, 1, QTableWidgetItem(shortcut))

        table.resizeColumnsToContents()
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
