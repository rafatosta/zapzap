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
        "flatpak_help": (
            """
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="{fill_color}" viewBox="0 0 256 256">
                <path d="M236.8,188.09,149.35,36.16a24,24,0,0,0-41.57,0L20.33,188.09A24,24,0,0,0,41.11,224H216a24,24,0,0,0,20.8-35.91ZM128,108a8,8,0,0,1,8,8v40a8,8,0,0,1-16,0V116A8,8,0,0,1,128,108Zm0,88a12,12,0,1,1,12-12A12,12,0,0,1,128,196Z"></path>
            </svg>
            """
        ),
        "view_grid": (
            """
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="{fill_color}" viewBox="0 0 256 256">
                <path d="M104,40H48A8,8,0,0,0,40,48v56a8,8,0,0,0,8,8h56a8,8,0,0,0,8-8V48A8,8,0,0,0,104,40Zm-8,48H56V56h40ZM208,40H152a8,8,0,0,0-8,8v56a8,8,0,0,0,8,8h56a8,8,0,0,0,8-8V48A8,8,0,0,0,208,40Zm-8,48H160V56h40ZM104,144H48a8,8,0,0,0-8,8v56a8,8,0,0,0,8,8h56a8,8,0,0,0,8-8V152A8,8,0,0,0,104,144Zm-8,48H56V160h40ZM208,144H152a8,8,0,0,0-8,8v56a8,8,0,0,0,8,8h56a8,8,0,0,0,8-8V152A8,8,0,0,0,208,144Zm-8,48H160V160h40Z"></path>
            </svg>
            """
        ),
        "donation_heart": (
            """
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="{fill_color}" viewBox="0 0 256 256">
                <path d="M176,32a60,60,0,0,0-48,24A60,60,0,0,0,20,92c0,71.9,99.9,128.6,104.2,131a8,8,0,0,0,7.6,0C136.1,220.6,236,163.9,236,92A60.1,60.1,0,0,0,176,32Zm-48,174.7C110.4,196,36,147.7,36,92a44,44,0,0,1,84.6-17.2,8,8,0,0,0,14.8,0A44,44,0,0,1,220,92C220,147.6,145.6,196,128,206.7Z"/>
            </svg>
            """
        ),
        "donation_code": (
            """
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" stroke="{fill_color}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 256 256">
                <path d="M88 64 24 128l64 64M168 64l64 64-64 64M144 40l-32 176"/>
            </svg>
            """
        ),
        "donation_pix": (
            """
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="{fill_color}" viewBox="0 0 256 256">
                <path d="m221.7 112.6-78.3-78.3a21.8 21.8 0 0 0-30.8 0L34.3 112.6a21.8 21.8 0 0 0 0 30.8l78.3 78.3a21.8 21.8 0 0 0 30.8 0l78.3-78.3a21.8 21.8 0 0 0 0-30.8ZM210.4 132.1l-78.3 78.3a5.8 5.8 0 0 1-8.2 0l-78.3-78.3a5.8 5.8 0 0 1 0-8.2l78.3-78.3a5.8 5.8 0 0 1 8.2 0l78.3 78.3a5.8 5.8 0 0 1 0 8.2Z"/>
            </svg>
            """
        ),
        "donation_card": (
            """
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="{fill_color}" viewBox="0 0 256 256">
                <path d="M224 48H32A16 16 0 0 0 16 64v128a16 16 0 0 0 16 16h192a16 16 0 0 0 16-16V64a16 16 0 0 0-16-16Zm0 16v24H32V64Zm0 128H32v-88h192v88Zm-32-24a8 8 0 0 1-8 8h-32a8 8 0 0 1 0-16h32a8 8 0 0 1 8 8Z"/>
            </svg>
            """
        ),
        "donation_transfer": (
            """
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="{fill_color}" viewBox="0 0 256 256">
                <path d="M224 72a8 8 0 0 1-8 8H59.3l26.4 26.3a8 8 0 0 1-11.4 11.4l-40-40a8 8 0 0 1 0-11.4l40-40a8 8 0 0 1 11.4 11.4L59.3 64H216a8 8 0 0 1 8 8Zm-42.3 66.3a8 8 0 0 0-11.4 11.4l26.4 26.3H40a8 8 0 0 0 0 16h156.7l-26.4 26.3a8 8 0 0 0 11.4 11.4l40-40a8 8 0 0 0 0-11.4Z"/>
            </svg>
            """
        ),
        "donation_cup": (
            """
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="{fill_color}" viewBox="0 0 256 256">
                <path d="M208 72h-16V56a8 8 0 0 0-8-8H40a8 8 0 0 0-8 8v88a64.1 64.1 0 0 0 64 64h32a64.1 64.1 0 0 0 62-48H208a44 44 0 0 0 0-88Zm-80 120H96a48.1 48.1 0 0 1-48-48V64h128v80a48.1 48.1 0 0 1-48 48Zm80-48h-16V88h16a28 28 0 0 1 0 56Z"/>
            </svg>
            """
        ),
        "external_link": (
            """
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="{fill_color}" viewBox="0 0 256 256">
                <path d="M224 104a8 8 0 0 1-16 0V59.3l-74.3 74.4a8 8 0 0 1-11.4-11.4L196.7 48H152a8 8 0 0 1 0-16h64a8 8 0 0 1 8 8Zm-40 24a8 8 0 0 0-8 8v72H48V80h72a8 8 0 0 0 0-16H48a16 16 0 0 0-16 16v128a16 16 0 0 0 16 16h128a16 16 0 0 0 16-16v-72a8 8 0 0 0-8-8Z"/>
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
