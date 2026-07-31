from PyQt6.QtWidgets import QFrame, QVBoxLayout

from .settings_divider import SettingsDivider


SUBSETTING_INDENT = 20


class SettingsCard(QFrame):
    """Rounded card container with explicit row and subgroup hierarchy."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsCard")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 10, 16, 10)
        self.layout.setSpacing(0)
        self._has_rows = False
        self._apply_style()

    def add_row(self, row, divider=True):
        """Add a row, separating it from the previous one by default."""
        if self._has_rows and divider:
            self.layout.addWidget(SettingsDivider(self))
        self.layout.addWidget(row)
        self._has_rows = True

    def add_group(self, parent_row, child_rows, child_dividers=False):
        """Add one top-level setting and its indented dependent controls.

        A full-width divider may precede the parent when another top-level
        item already exists. Children live in a shared indented container, so
        their technical widget boundaries do not flatten the visual hierarchy.
        """
        self.add_row(parent_row)
        subgroup = SettingsSubgroup(self)
        for child_row in child_rows:
            subgroup.add_row(child_row, divider=child_dividers)
        self.layout.addWidget(subgroup)
        return subgroup

    def add_subrow(self, row):
        """Add a single indented supporting row without a full-width divider."""
        subgroup = SettingsSubgroup(self)
        subgroup.add_row(row)
        self.layout.addWidget(subgroup)
        return subgroup

    def add_space(self, width=10):
        self.layout.addSpacing(width)

    def _apply_style(self):
        self.setStyleSheet("""
            QFrame#SettingsCard {
                background: palette(base);
                border: 1px solid palette(mid);
                border-radius: 14px;
            }
        """)


class SettingsSubgroup(QFrame):
    """Indented controls that belong to one parent setting."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsSubgroup")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(SUBSETTING_INDENT, 0, 0, 4)
        self.layout.setSpacing(2)
        self._has_rows = False
        self.setStyleSheet("""
            QFrame#SettingsSubgroup {
                background: transparent;
                border: 0;
            }
        """)

    def add_row(self, row, divider=False):
        """Add a child, optionally separating equivalent sibling controls."""
        if self._has_rows and divider:
            self.layout.addWidget(SettingsDivider(self))
        self.layout.addWidget(row)
        self._has_rows = True
