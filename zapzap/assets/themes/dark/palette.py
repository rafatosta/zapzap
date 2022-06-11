from PyQt6.QtGui import QPalette, QColor
_palette = QPalette()

# base
_palette.setColor(QPalette.ColorRole.WindowText, QColor("#e4e7eb"))
_palette.setColor(QPalette.ColorRole.Button, QColor("#202124"))
_palette.setColor(QPalette.ColorRole.Text, QColor("#eff1f1"))
_palette.setColor(QPalette.ColorRole.ButtonText, QColor("#8ab4f7"))
_palette.setColor(QPalette.ColorRole.Base, QColor("#202124"))
_palette.setColor(QPalette.ColorRole.Window, QColor("#202124"))
_palette.setColor(QPalette.ColorRole.Highlight, QColor("#8ab4f7"))
_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#202124"))
_palette.setColor(QPalette.ColorRole.Link, QColor("#202124"))
_palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#292b2e"))
_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#292a2d"))
_palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#e4e7eb"))
_palette.setColor(QPalette.ColorRole.LinkVisited, QColor("#c58af8"))
_palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#292a2d"))
_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#e4e7eb"))
if hasattr(QPalette.ColorRole, "Foreground"):
    _palette.setColor(QPalette.ColorRole.Foreground,
                      QColor("#e4e7eb"))  # type: ignore
if hasattr(QPalette.ColorRole, "PlaceholderText"):
    _palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#8a8b8d"))

_palette.setColor(QPalette.ColorRole.Light, QColor("#3f4042"))
_palette.setColor(QPalette.ColorRole.Midlight, QColor("#3f4042"))
_palette.setColor(QPalette.ColorRole.Dark, QColor("#e4e7eb"))
_palette.setColor(QPalette.ColorRole.Mid, QColor("#3f4042"))
_palette.setColor(QPalette.ColorRole.Shadow, QColor("#3f4042"))

# disabled
_palette.setColor(QPalette.ColorGroup.Disabled,
                  QPalette.ColorRole.WindowText, QColor("#697177"))
_palette.setColor(QPalette.ColorGroup.Disabled,
                  QPalette.ColorRole.Text, QColor("#697177"))
_palette.setColor(QPalette.ColorGroup.Disabled,
                  QPalette.ColorRole.ButtonText, QColor("#3f4042"))
_palette.setColor(QPalette.ColorGroup.Disabled,
                  QPalette.ColorRole.Highlight, QColor("#53575b"))
_palette.setColor(QPalette.ColorGroup.Disabled,
                  QPalette.ColorRole.HighlightedText, QColor("#697177"))
_palette.setColor(QPalette.ColorGroup.Disabled,
                  QPalette.ColorRole.Link, QColor("#697177"))
_palette.setColor(QPalette.ColorGroup.Disabled,
                  QPalette.ColorRole.LinkVisited, QColor("#697177"))

# inactive
_palette.setColor(QPalette.ColorGroup.Inactive,
                  QPalette.ColorRole.Highlight, QColor("#393d41"))

PALETTE_DARK = _palette
