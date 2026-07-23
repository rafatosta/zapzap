"""Data model for the keyboard shortcuts dialog."""

from gettext import gettext as _


class ShortcutsModel:
    """Provides the shortcuts displayed by the application."""

    def whatsapp_shortcuts(self):
        """Return shortcuts handled by WhatsApp Web."""
        return [
            (_("New conversation"), "Ctrl + Alt + N"),
            (_("Mark as unread"), "Ctrl + Alt + Shift + U"),
            (_("Archive conversation"), "Ctrl + Alt + Shift + E"),
            (_("Pin conversation"), "Ctrl + Alt + Shift + P"),
            (_("Next conversation"), "Ctrl + Alt + Tab"),
            (_("Close conversation"), "Escape"),
            (_("Search in conversation"), "Ctrl + Alt + Shift + F"),
            (_("Previous conversation"), "Ctrl + Alt + Shift + Tab"),
            (_("Delete conversation"), "Ctrl + Alt + Backspace"),
            (_("Profile and status"), "Ctrl + Alt + P"),
            (_("Settings"), "Ctrl + Alt + ,"),
            (_("Decrease speed of selected voice message"), "Shift + ,"),
            (_("Increase speed of selected voice message"), "Shift + ."),
            (_("Emoji panel"), "Ctrl + Alt + E"),
            (_("Sticker panel"), "Ctrl + Alt + S"),
            (_("GIF panel"), "Ctrl + Alt + G"),
            (_("Lock the app"), "Ctrl + Alt + L"),
            (_("Mute"), "Ctrl + Alt + Shift + M"),
            (_("Search"), "Ctrl + Alt + /"),
            (_("New group"), "Ctrl + Alt + Shift + N"),
            (_("Extended search"), "Alt + K"),
        ]

    def zapzap_shortcuts(self):
        """Return shortcuts handled by ZapZap."""
        return [
            (_("Settings"), "Ctrl + P"),
            (_("Hide"), "Ctrl + W"),
            (_("Exit"), "Ctrl + Q"),
            (_("Fullscreen"), "F11"),
            (_("Automatic theme"), "Ctrl + Alt + 1"),
            (_("Light theme"), "Ctrl + Alt + 2"),
            (_("Dark theme"), "Ctrl + Alt + 3"),
            (_("Reset zoom"), "Ctrl + 0"),
            (_("Zoom in"), "Ctrl + +"),
            (_("Zoom out"), "Ctrl + -"),
            (_("Reload pages"), "F5"),
            (_("New conversation by phone number"), "Ctrl + M"),
            (_("New account"), "Ctrl + U"),
        ]
