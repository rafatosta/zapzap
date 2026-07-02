

from zapzap.views.components import ComboBox
from ._base_row import _BaseRow

class SelectRow(_BaseRow):
    def __init__(self, title, description="", items=None, parent=None):
        self.combo = ComboBox()
        if items:
            self.combo.addItems(items)
        super().__init__(title, description, self.combo, parent)
