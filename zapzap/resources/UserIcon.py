from PyQt6.QtGui import QImage, QPixmap, QIcon
from PyQt6.QtCore import QSize
import random
from enum import Enum


class UserIcon:
    """Classe para manipulação e criação de ícones personalizados para usuários."""

    class Type(Enum):
        Default = 1
        Disable = 2
        Silence = 3

    # Constantes para SVGs
    ICON_DEFAULT = """<?xml version="1.0" encoding="utf-8"?>
<svg viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <linearGradient id="linearGradient3062" x1="8.3581467" y1="52.194504" x2="59.375187" y2="52.027035" gradientUnits="userSpaceOnUse" gradientTransform="matrix(4.508297, 0, 0, 4.246757, -24.681, -11.662596)" xlink:href="#linearGradient3060"/>
    <linearGradient id="linearGradient3060">
      <stop style="stop-color:#c0bfbc;stop-opacity:0.96470588;" offset="0" id="stop3056"/>
      <stop style="stop-color:#f6f5f4;stop-opacity:0.96470588;" offset="0.1216" id="stop10456"/>
      <stop style="stop-color:#c0bfbc;stop-opacity:0.96470588;" offset="0.2415" id="stop10458"/>
      <stop style="stop-color:#c0bfbc;stop-opacity:0.96470588;" offset="0.7285" id="stop10462"/>
      <stop style="stop-color:#f6f5f4;stop-opacity:0.96470588;" offset="0.8621" id="stop10460"/>
      <stop style="stop-color:#c0bfbc;stop-opacity:0.96470588;" offset="1" id="stop3058"/>
    </linearGradient>
    <linearGradient id="linearGradient15564" x1="33.867146" y1="51.861328" x2="33.867188" y2="12.729865" gradientUnits="userSpaceOnUse" gradientTransform="matrix(4.983321, 0, 0, 4.727647, -41.268536, -31.905169)" xlink:href="#linearGradient15562"/>
    <linearGradient id="linearGradient15562">
      <stop style="stop-color:#209232;stop-opacity:1;" offset="0" id="stop15558"/>
      <stop style="stop-color:#34c640;stop-opacity:1;" offset="1" id="stop15560"/>
    </linearGradient>
  </defs>
  <g>
    <path id="path2070" style="fill:url(#linearGradient3062);fill-opacity:1;stroke-width:0.208431" d="M 128.002 26.343 C 64.49 26.343 13 74.843 13 134.672 C 13.017 153.149 18.051 171.315 27.624 187.442 L 21.594 210.626 C 19.428 210.337 17.492 211.924 17.496 213.986 L 17.529 227.037 L 17.529 227.326 C 17.528 227.407 17.528 227.487 17.529 227.568 L 17.531 228.353 C 17.537 228.636 17.58 228.917 17.659 229.19 C 18.598 236.612 26.261 241.976 33.767 240.465 L 76.764 231.606 C 92.679 239.085 110.217 242.985 128.002 243 C 191.515 243 243 194.5 243 134.672 C 243 74.843 191.515 26.343 128.002 26.343 Z"/>
    <path id="path1677" style="fill-opacity: 1; stroke: none; stroke-width: 0.1; stroke-dasharray: none; stroke-opacity: 1; fill: rgb(255, 255, 255);" d="M 128.001 13 C 64.489 13 13.001 61.499 13 121.327 C 13.017 139.805 18.052 157.971 27.625 174.099 L 19.029 207.142 L 17.868 211.603 C 15.571 220.429 24.404 229.05 33.767 227.121 C 33.767 227.121 33.768 227.121 33.768 227.121 L 76.764 218.261 C 92.678 225.741 110.216 229.641 128.001 229.656 C 191.514 229.656 243 181.155 242.999 121.327 C 242.999 61.499 191.513 13 128.001 13 Z"/>
    <path id="path333" style="fill:url(#linearGradient15564);fill-opacity:1;stroke:none;stroke-width:0.05;stroke-linejoin:miter;stroke-dasharray:none;stroke-opacity:1" d="M 127.502 28.277 C 96.599 28.287 67.525 42.2 49.149 65.773 L 132.045 69.714 L 30.239 114.682 C 30.088 116.71 30.008 118.743 30 120.777 C 30 171.864 73.653 213.277 127.502 213.277 C 162.586 213.271 194.96 195.384 212.279 166.438 L 129.545 162.504 L 225 120.342 C 224.75 69.428 181.17 28.279 127.502 28.277 Z"/>
  </g>
  {}
</svg>
"""
    IMAGE_DISABLE = """<path d="M 150.063 90.451 H 182.371 V 150.128 H 246.989 V 179.967 H 182.371 V 239.645 H 150.063 V 179.967 H 85.445 V 150.128 H 150.063 Z" style="fill: rgb(255, 0, 0); stroke: rgb(0, 0, 0);" transform="matrix(0.715986, -0.698115, 0.698115, 0.715986, -68.014503, 162.914597)" bx:shape="cross 85.445 90.451 161.544 149.194 29.839 32.308 0.5 1@64eb8597"/>"""

    IMAGE_SILENCE = """ <path d="M 131.636 121.618 C 128.873 118.751 123.774 119.712 122.458 123.346 C 121.833 125.074 122.282 126.977 123.629 128.31 L 134.949 139.77 C 130.143 147.362 127.616 155.994 127.634 164.78 C 127.634 186.765 122.049 203.588 118.296 209.535 C 114.1 216.154 119.267 224.47 127.595 224.503 C 127.608 224.504 127.62 224.504 127.634 224.504 L 218.675 224.504 L 231.823 237.805 C 234.585 240.671 239.686 239.709 241 236.076 C 241.627 234.347 241.175 232.443 239.827 231.11 L 131.636 121.618 Z M 127.634 214.549 C 132.84 206.312 138.452 187.226 138.452 164.78 C 138.443 158.832 139.891 152.958 142.686 147.598 L 208.838 214.549 L 127.634 214.549 Z M 208.776 239.435 C 208.776 242.183 206.355 244.412 203.367 244.412 L 160.091 244.412 C 155.928 244.412 153.323 240.264 155.406 236.947 C 156.372 235.407 158.159 234.458 160.091 234.458 L 203.367 234.458 C 206.355 234.458 208.776 236.686 208.776 239.435 Z M 239.881 211.596 C 239.251 211.82 238.578 211.936 237.901 211.938 C 235.676 211.934 233.681 210.68 232.871 208.777 C 227.946 197.248 225.006 180.8 225.006 164.78 C 225.015 134.262 189.237 115.079 160.381 130.133 C 156.721 131.959 152.283 129.453 152.397 125.622 C 152.448 123.916 153.445 122.351 155.039 121.48 C 191.106 102.658 235.831 126.63 235.824 164.78 C 235.824 186.771 241.268 201.23 242.938 205.143 C 244.031 207.7 242.662 210.59 239.881 211.596 Z" style="fill: rgb(255, 0, 0); stroke-width: 4px; stroke: rgb(255, 0, 0);">
    <title>silence</title>
  </path> """

    SVG_NOTIFICATION = """
  <rect y="116.592" width="{width}" height="136.107" style="fill: rgb(255, 0, 0); stroke: rgb(255, 0, 0);" rx="19.653" ry="19.653" x="{x}"/>
  <text style="fill: rgb(255, 255, 255); font-family: Arial, sans-serif; font-size: 65.9885px; font-weight: 700; text-anchor: end; white-space: pre;" transform="matrix(2.154438, 0, 0, 1.833654, -279.152802, -210.015335)" x="244.638" y="238.631">{number}</text>
"""

    @staticmethod
    def get_new_icon_svg() -> str:
        """Gera um novo SVG com cores aleatórias."""
        svg = UserIcon.ICON_DEFAULT.replace(
            '#209232', UserIcon._generate_random_color())
        return svg.replace('#34c640', UserIcon._generate_random_color())

    @staticmethod
    def _generate_random_color():
        """Gera uma cor aleatória em rgb"""
        return f'rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})'

    @staticmethod
    def get_icon(svg_str: str = ICON_DEFAULT, icon_type=Type.Default, qtd: int = 0) -> QIcon:
        """Gera um QIcon a partir de um SVG."""
        if icon_type == UserIcon.Type.Default:
            qtd = 999 if qtd >= 1000 else qtd
            data = UserIcon._get_notification_data(qtd)
            notification = UserIcon.SVG_NOTIFICATION.format(
                x=data['x'], width=data['width'], number=qtd)
            svg = svg_str.format(notification if qtd > 0 else "")
        elif icon_type == UserIcon.Type.Disable:
            svg = svg_str.format(UserIcon.IMAGE_DISABLE)
        else:
            svg = svg_str.format(UserIcon.IMAGE_SILENCE)
        return UserIcon.__build(svg)

    @staticmethod
    def __build(svg_str: str) -> QIcon:
        """Constrói um QIcon a partir de um SVG."""
        svg_bytes = bytearray(svg_str, encoding='utf-8')
        qimg = QImage.fromData(svg_bytes, 'SVG')
        qpix = QPixmap.fromImage(qimg)
        return QIcon(qpix.scaled(QSize(128, 128)))

    @staticmethod
    def _get_notification_data(qtd: int) -> dict:
        """Helper para determinar o tamanho da notificação."""
        if len(str(qtd)) == 1:
            return dict(width=100.1, x=152.6)
        elif len(str(qtd)) == 2:
            return dict(width=180.3, x=72.5)
        else:
            return dict(width=249.428, x=3.286)
