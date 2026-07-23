from zapzap.ui.typography import Typography


class ThemeStylesheet:
    """Global styles for Qt-owned widgets that cannot be wrapped reliably."""

    GLOBAL_COMPONENTS = """
        QToolTip {
            background-color: palette(base);
            color: palette(text);
            border: 1px solid palette(mid);
            border-radius: 10px;
            padding: 8px 10px;
            font-size: @font-small;
            opacity: 245;
        }

        QScrollArea {
            background: palette(window);
            border: 0;
        }
        QScrollArea > QWidget > QWidget {
            background: palette(window);
        }
        QScrollBar:vertical {
            background: transparent;
            width: 10px;
            margin: 2px;
            border: 0;
        }
        QScrollBar::handle:vertical {
            background: palette(mid);
            min-height: 24px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical:hover {
            background: palette(highlight);
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
            background: transparent;
            border: 0;
        }
        QScrollBar:horizontal {
            background: transparent;
            height: 10px;
            margin: 2px;
            border: 0;
        }
        QScrollBar::handle:horizontal {
            background: palette(mid);
            min-width: 24px;
            border-radius: 5px;
        }
        QScrollBar::handle:horizontal:hover {
            background: palette(highlight);
        }
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {
            width: 0;
            background: transparent;
            border: 0;
        }
        QMenuBar {
            background-color: palette(window);
            color: palette(text);
            border: none;
            border-bottom: 1px solid palette(mid);
            padding: 2px 6px;
            spacing: 2px;
            font-size: @font-body;
        }
        QMenuBar::item {
            background: transparent;
            color: palette(text);
            padding: 6px 10px;
            margin: 2px 1px;
            border-radius: 8px;
        }
        QMenuBar::item:selected {
            background-color: palette(alternate-base);
            color: palette(highlight);
        }
        QMenuBar::item:pressed {
            background-color: palette(highlight);
            color: palette(highlighted-text);
        }
        QMenuBar::item:disabled {
            color: palette(placeholder-text);
        }
        QMenu {
            background-color: palette(base);
            border: 1px solid palette(mid);
            border-radius: 10px;
            padding: 6px;
            color: palette(text);
            font-size: @font-body;
        }
        QMenu::item {
            background-color: transparent;
            padding: 8px 28px 8px 12px;
            margin: 2px 0;
            border-radius: 7px;
        }
        QMenu::item:selected {
            background-color: palette(alternate-base);
            color: palette(highlight);
        }
        QMenu::item:pressed {
            background-color: palette(highlight);
            color: palette(highlighted-text);
        }
        QMenu:disabled {
            background-color: palette(base);
            border: 1px solid palette(mid);
            color: palette(placeholder-text);
        }
        QMenu::item:disabled {
            color: palette(placeholder-text);
            background-color: transparent;
        }
        QMenu::separator {
            height: 1px;
            background-color: palette(mid);
            margin: 6px 8px;
        }
        QMenu::indicator {
            width: 12px;
            height: 12px;
            border: 2px solid palette(mid);
            border-radius: 6px;
            background-color: palette(base);
        }
        QMenu::indicator:checked {
            background-color: palette(highlight);
            border: 2px solid palette(highlight);
        }
        QMenu::indicator:unchecked {
            background-color: palette(base);
            border: 2px solid palette(mid);
        }
        QMenu::right-arrow {
            padding-left: 8px;
        }
        QMessageBox {
            background-color: palette(window);
            color: palette(text);
            font-size: @font-body;
        }
        QMessageBox QLabel {
            background-color: transparent;
            color: palette(text);
        }
        QMessageBox QLabel#qt_msgbox_label,
        QMessageBox QLabel#qt_msgbox_informativelabel {
            max-width: 560px;
            padding: 2px 0;
        }
        QMessageBox QDialogButtonBox {
            background-color: transparent;
            button-layout: 0;
        }
        QMessageBox QPushButton {
            min-width: 84px;
            min-height: 26px;
            border: 1px solid palette(mid);
            border-radius: 8px;
            padding: 6px 12px;
            background-color: palette(button);
            color: palette(button-text);
        }
        QMessageBox QPushButton:hover {
            border-color: palette(highlight);
            background-color: palette(alternate-base);
        }
        QMessageBox QPushButton:pressed,
        QMessageBox QPushButton:default {
            border-color: palette(highlight);
            background-color: palette(highlight);
            color: palette(highlighted-text);
        }
        QMessageBox QPushButton:disabled {
            border-color: palette(mid);
            background-color: palette(window);
            color: palette(placeholder-text);
        }
        QMessageBox QCheckBox {
            background-color: transparent;
            color: palette(text);
            spacing: 8px;
        }
        QMessageBox QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid palette(mid);
            border-radius: 4px;
            background-color: palette(base);
        }
        QMessageBox QCheckBox::indicator:checked {
            background-color: palette(highlight);
            border-color: palette(highlight);
        }
    """.replace("@font-small", Typography.px(Typography.SMALL)).replace("@font-body", Typography.px(Typography.BODY))

    @staticmethod
    def get_global_components_stylesheet() -> str:
        """Return global QSS for Qt-owned popups and menu widgets."""
        return ThemeStylesheet.GLOBAL_COMPONENTS
