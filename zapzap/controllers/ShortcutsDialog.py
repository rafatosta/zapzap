from PyQt6.QtWidgets import QDialog, QHeaderView, QTableWidgetItem
from zapzap.views.ui_shortcuts_dialog import Ui_ShortcutsDialog


class ShortcutsDialog(QDialog, Ui_ShortcutsDialog):
    # Shortcuts
    shortcuts = [
        # Conversations
        ("New conversation", "Ctrl + Alt + N"),
        ("Mark as unread", "Ctrl + Alt + Shift + U"),
        ("Archive conversation", "Ctrl + Alt + Shift + E"),
        ("Pin conversation", "Ctrl + Alt + Shift + P"),
        ("Next conversation", "Ctrl + Alt + Tab"),
        ("Close conversation", "Escape"),
        ("Search in conversation", "Ctrl + Alt + Shift + F"),
        ("Previous conversation", "Ctrl + Alt + Shift + Tab"),
        ("Delete conversation", "Ctrl + Alt + Backspace"),

        # Settings and Profiles
        ("Profile and status", "Ctrl + Alt + P"),
        ("Settings", "Ctrl + Alt + ,"),

        # Voice Messages
        ("Decrease speed of selected voice message", "Shift + ,"),
        ("Increase speed of selected voice message", "Shift + ."),

        # Media Tools
        ("Emoji panel", "Ctrl + Alt + E"),
        ("Sticker panel", "Ctrl + Alt + S"),
        ("GIF panel", "Ctrl + Alt + G"),

        # Others
        ("Lock the app", "Ctrl + Alt + L"),
        ("Mute", "Ctrl + Alt + Shift + M"),
        ("Search", "Ctrl + Alt + /"),
        ("New group", "Ctrl + Alt + Shift + N"),
        ("Extended search", "Alt + K"),
    ]

    shortcuts_zapzap = [
        # Settings and Navigation
        ("Settings", "Ctrl + P"),
        ("Hide", "Ctrl + W"),
        ("Exit", "Ctrl + Q"),

        # View
        ("Fullscreen", "F11"),
        ("Reset zoom", "Ctrl + 0"),
        ("Zoom in", "Ctrl + +"),
        ("Zoom out", "Ctrl + -"),

        # Refresh
        ("Reload pages", "F5"),
        ("New conversation by phone number", "Ctrl + M"),

        # Account
        ("New user", "Ctrl + U"),
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
