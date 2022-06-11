from PyQt6.QtGui import QPalette, QColor
_palette = QPalette()

# base
_palette.setColor(QPalette.ColorRole.WindowText, QColor("#4d5157"))
_palette.setColor(QPalette.ColorRole.Button, QColor("#f8f9fa"))
_palette.setColor(QPalette.ColorRole.Text, QColor("#4d5157"))
_palette.setColor(QPalette.ColorRole.ButtonText, QColor("#0081db"))
_palette.setColor(QPalette.ColorRole.Base, QColor("#f8f9fa"))
_palette.setColor(QPalette.ColorRole.Window, QColor("#f8f9fa"))
_palette.setColor(QPalette.ColorRole.Highlight, QColor("#0081db"))
_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#f8f9fa"))
_palette.setColor(QPalette.ColorRole.Link, QColor("#f8f9fa"))
_palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#e9ecef"))
_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
_palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#4d5157"))
_palette.setColor(QPalette.ColorRole.LinkVisited, QColor("#660098"))
_palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))
_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#4d5157"))
if hasattr(QPalette.ColorRole, "Foreground"):
    _palette.setColor(QPalette.ColorRole.Foreground,
                      QColor("#4d5157"))  # type: ignore
if hasattr(QPalette.ColorRole, "PlaceholderText"):
    _palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#696a6c"))

_palette.setColor(QPalette.ColorRole.Light, QColor("#dadce0"))
_palette.setColor(QPalette.ColorRole.Midlight, QColor("#dadce0"))
_palette.setColor(QPalette.ColorRole.Dark, QColor("#4d5157"))
_palette.setColor(QPalette.ColorRole.Mid, QColor("#dadce0"))
_palette.setColor(QPalette.ColorRole.Shadow, QColor("#dadce0"))

# disabled
_palette.setColor(QPalette.ColorGroup.Disabled,
                  QPalette.ColorRole.WindowText, QColor("#babdc2"))
_palette.setColor(QPalette.ColorGroup.Disabled,
                  QPalette.ColorRole.Text, QColor("#babdc2"))
_palette.setColor(QPalette.ColorGroup.Disabled,
                  QPalette.ColorRole.ButtonText, QColor("#dadce0"))
_palette.setColor(QPalette.ColorGroup.Disabled,
                  QPalette.ColorRole.Highlight, QColor("#dadce0"))
_palette.setColor(QPalette.ColorGroup.Disabled,
                  QPalette.ColorRole.HighlightedText, QColor("#babdc2"))
_palette.setColor(QPalette.ColorGroup.Disabled,
                  QPalette.ColorRole.Link, QColor("#babdc2"))
_palette.setColor(QPalette.ColorGroup.Disabled,
                  QPalette.ColorRole.LinkVisited, QColor("#babdc2"))

# inactive
_palette.setColor(QPalette.ColorGroup.Inactive,
                  QPalette.ColorRole.Highlight, QColor("#e4e6f2"))

PALETTE_LIGHT = _palette
