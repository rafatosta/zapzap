from PyQt6.QtGui import QImage, QPixmap, QIcon
from PyQt6.QtCore import QSize
from enum import Enum


class SystemIcon:
    """Classe para manipulação e criação de ícones personalizados do sistema."""

    class Type(Enum):
        Light = "light"
        Dark = "dark"

    SVG_ICONS = {
        "new_account": (
            """
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="{fill_color}" viewBox="0 0 256 256">
                <path d="M256,136a8,8,0,0,1-8,8H232v16a8,8,0,0,1-16,0V144H200a8,8,0,0,1,0-16h16V112a8,8,0,0,1,16,0v16h16A8,8,0,0,1,256,136Zm-57.87,58.85a8,8,0,0,1-12.26,10.3C165.75,181.19,138.09,168,108,168s-57.75,13.19-77.87,37.15a8,8,0,0,1-12.25-10.3c14.94-17.78,33.52-30.41,54.17-37.17a68,68,0,1,1,71.9,0C164.6,164.44,183.18,177.07,198.13,194.85ZM108,152a52,52,0,1,0-52-52A52.06,52.06,0,0,0,108,152Z"></path>
            </svg>
            """
        ),
        "open_settings": (
            """
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="{fill_color}" viewBox="0 0 256 256">
                <path d="M136,120v96a8,8,0,0,1-16,0V120a8,8,0,0,1,16,0Zm64,72a8,8,0,0,0-8,8v16a8,8,0,0,0,16,0V200A8,8,0,0,0,200,192Zm24-32H208V40a8,8,0,0,0-16,0V160H176a8,8,0,0,0,0,16h48a8,8,0,0,0,0-16ZM56,160a8,8,0,0,0-8,8v48a8,8,0,0,0,16,0V168A8,8,0,0,0,56,160Zm24-32H64V40a8,8,0,0,0-16,0v88H32a8,8,0,0,0,0,16H80a8,8,0,0,0,0-16Zm72-48H136V40a8,8,0,0,0-16,0V80H104a8,8,0,0,0,0,16h48a8,8,0,0,0,0-16Z"></path>
            </svg>
            """
        ),
        "new_chat": (
            """
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="{fill_color}" viewBox="0 0 256 256">
                <path d="M216,48H40A16,16,0,0,0,24,64V224a15.84,15.84,0,0,0,9.25,14.5A16.05,16.05,0,0,0,40,240a15.89,15.89,0,0,0,10.25-3.78.69.69,0,0,0,.13-.11L82.5,208H216a16,16,0,0,0,16-16V64A16,16,0,0,0,216,48ZM40,224h0ZM216,192H82.5a16,16,0,0,0-10.3,3.75l-.12.11L40,224V64H216Z"></path>
            </svg>
            """
        ),
        "new_chat_number": (
            """
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="{fill_color}" viewBox="0 0 256 256">
                <path d="M222.36,158.46l-47.1-21.11-.12-.06a16,16,0,0,0-15.18,1.4,8.12,8.12,0,0,0-.75.56L134.87,160c-15.42-7.49-31.34-23.29-38.83-38.51l20.78-24.71c.2-.25.39-.5.57-.77a16,16,0,0,0,1.32-15.06.61.61,0,0,1,0-.12L97.54,33.64a16,16,0,0,0-16.62-9.52A56.26,56.26,0,0,0,32,80c0,79.4,64.6,144,144,144a56.26,56.26,0,0,0,55.88-48.92A16,16,0,0,0,222.36,158.46ZM176,208A128.14,128.14,0,0,1,48,80A40.2,40.2,0,0,1,82.87,40a.61.61,0,0,0,0,.12l21,47L83.2,111.86a6.13,6.13,0,0,0-.57.77,16,16,0,0,0-1,15.7c9.06,18.53,27.73,37.06,46.46,46.11a16,16,0,0,0,15.75-1.14,6.92,6.92,0,0,0,.74-.57L168.89,152l47,21.06h0s.08,0,.11,0A40.21,40.21,0,0,1,176,208ZM144,72a8,8,0,0,1,8-8h24V40a8,8,0,0,1,16,0V64h24a8,8,0,0,1,0,16H192v24a8,8,0,0,1-16,0V80H152A8,8,0,0,1,144,72Z"></path>
            </svg>
            """
        ),
    }

    @staticmethod
    def get_icon(icon_name: str, theme: Type = Type.Light) -> QIcon:
        """Retorna um QIcon baseado no nome do ícone e no tema."""
        if icon_name not in SystemIcon.SVG_ICONS:
            raise ValueError(f"Ícone '{icon_name}' não encontrado.")
        fill_color = "#202C33" if theme == SystemIcon.Type.Light else "#f7f5f3"
        svg_str = SystemIcon.SVG_ICONS[icon_name].format(fill_color=fill_color)
        return SystemIcon.__build(svg_str)

    @staticmethod
    def __build(svg_str: str) -> QIcon:
        """Constrói um QIcon a partir de um SVG."""
        svg_bytes = bytearray(svg_str, encoding="utf-8")
        qimg = QImage.fromData(svg_bytes, "SVG")
        qpix = QPixmap.fromImage(qimg)
        return QIcon(qpix.scaled(QSize(128, 128)))
