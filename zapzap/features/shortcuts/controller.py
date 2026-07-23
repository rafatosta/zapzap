"""Controller for the keyboard shortcuts dialog."""

from zapzap.features.shortcuts.model import ShortcutsModel
from zapzap.features.shortcuts.view import ShortcutsView


class ShortcutsController(ShortcutsView):
    """Coordinates shortcut data and dialog presentation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = ShortcutsModel()
        self._load_shortcuts()

    def _load_shortcuts(self):
        self.set_whatsapp_shortcuts(self.model.whatsapp_shortcuts())
        self.set_zapzap_shortcuts(self.model.zapzap_shortcuts())
