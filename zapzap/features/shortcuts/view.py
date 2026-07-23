"""View for the keyboard shortcuts dialog."""

from gettext import gettext as _

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QAbstractItemView
from PyQt6.QtWidgets import QDialog
from PyQt6.QtWidgets import QDialogButtonBox
from PyQt6.QtWidgets import QGroupBox
from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QTableWidget
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtWidgets import QVBoxLayout

from zapzap.ui.components import Label


class ShortcutsView(QDialog):
    """Presents shortcut data without owning application behavior."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("ShortcutsView")
        self.resize(798, 575)
        self.setWindowTitle(_("Dialog"))

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        self.label = Label(_("Keyboard shortcuts"), parent=self)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        self.groupBox = QGroupBox(_("WhatsApp Web"), parent=self)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.table_whatsapp = self._create_table(
            self.groupBox,
            "table_whatsapp",
        )
        self.verticalLayout_2.addWidget(self.table_whatsapp)
        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(_("ZapZap"), parent=self)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout = QHBoxLayout(self.groupBox_2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.table_zapzap = self._create_table(
            self.groupBox_2,
            "table_zapzap",
        )
        self.horizontalLayout.addWidget(self.table_zapzap)
        self.verticalLayout.addWidget(self.groupBox_2)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok,
            Qt.Orientation.Horizontal,
            parent=self,
        )
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.verticalLayout.addWidget(self.buttonBox)

    @staticmethod
    def _create_table(parent, object_name):
        table = QTableWidget(parent=parent)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setObjectName(object_name)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setStretchLastSection(False)
        return table

    def set_whatsapp_shortcuts(self, shortcuts):
        self._populate_table(self.table_whatsapp, shortcuts)

    def set_zapzap_shortcuts(self, shortcuts):
        self._populate_table(self.table_zapzap, shortcuts)

    @staticmethod
    def _populate_table(table, shortcuts):
        """Render a shortcut collection in the specified table."""
        table.setColumnCount(2)
        table.setRowCount(len(shortcuts))

        for row, (action, shortcut) in enumerate(shortcuts):
            table.setItem(row, 0, QTableWidgetItem(action))
            table.setItem(row, 1, QTableWidgetItem(shortcut))

        table.resizeColumnsToContents()
        table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )
        table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
