
from enum import Enum
from PyQt6.QtGui import QImage, QPixmap, QIcon
from PyQt6.QtCore import QSize


class TrayIcon:

    class Type(Enum):
        Default = "default"
        SLight = "symbolic_light"
        SDark = "symbolic_dark"

    _DEFAULT = """<?xml version="1.0" encoding="utf-8"?>
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
  {notify}
</svg>
"""

    _SYMBOLIC = """<?xml version="1.0" encoding="utf-8"?>
<svg viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <g id="layer1" transform="matrix(6.791338, 0, 0, 6.791338, 13.000002, 13.000012)">
    <path id="path-1" style="fill-opacity: 1; stroke: none; stroke-width: 0.0663829; stroke-dasharray: none; stroke-opacity: 1; fill: {color};" d="M 16.933333,5.7553998e-7 A 16.933245,16.933245 0 0 0 2.3333327e-7,16.933333 16.933245,16.933245 0 0 0 2.1534007,25.182072 l -1.26573497,5.1653 -0.17059912,0.697255 A 1.9466245,1.8017893 48.483562 0 0 3.0581261,33.470436 L 9.3890022,32.085281 A 16.933245,16.933245 0 0 0 16.933333,33.866666 16.933245,16.933245 0 0 0 33.866667,16.933333 16.933245,16.933245 0 0 0 16.933333,5.7553998e-7 Z M 16.933884,3.9446912 A 12.988273,12.988273 0 0 1 29.921425,16.872247 l -12.715134,5.920339 11.02015,0.551969 A 12.988273,12.988273 0 0 1 16.933884,29.921425 12.988273,12.988273 0 0 1 3.9452411,16.933333 12.988273,12.988273 0 0 1 3.9771597,16.077586 L 17.538685,9.7632198 6.4959724,9.2101487 A 12.988273,12.988273 0 0 1 16.933884,3.9446912 Z"/>
  </g>
  {notify}
</svg>
"""

    _DEFAULT_NOTIFICATION = """
  <rect y="116.592" width="{width}" height="136.107" style="fill: rgb(255, 0, 0); stroke: rgb(255, 0, 0);" rx="19.653" ry="19.653" x="{x}"/>
  <text style="fill: rgb(255, 255, 255); font-family: Arial, sans-serif; font-size: 65.9885px; font-weight: 700; text-anchor: end; white-space: pre;" transform="matrix(2.154438, 0, 0, 1.833654, -279.152802, -210.015335)" x="244.638" y="238.631">{number}</text>
"""

    @staticmethod
    def getIcon(theme=Type.Default, qtd=0) -> QIcon:
        """
        theme: default, symbolic_light, symbolic_dark
        qtd: quantidade
        """

        qtd = 999 if qtd >= 1000 else qtd

        # Determine notification size based on qtd
        data = TrayIcon._getNotificationData(qtd)
        notification = TrayIcon._DEFAULT_NOTIFICATION.format(
            x=data['x'], width=data['width'], number=qtd)
        n = notification if qtd > 0 else ""

        # Select the correct SVG template based on theme
        svg_str = TrayIcon._getSvgByTheme(theme, n)
        return TrayIcon.__build(svg_str)

    @staticmethod
    def _getNotificationData(qtd) -> dict:
        """Helper function to determine notification size based on qtd"""
        if len(str(qtd)) == 1:
            return dict(width=100.1, x=152.6)
        elif len(str(qtd)) == 2:
            return dict(width=180.3, x=72.5)
        else:
            return dict(width=249.428, x=3.286)

    @staticmethod
    def _getSvgByTheme(theme, notify) -> str:
        """Helper function to get SVG string based on theme"""
        if theme == TrayIcon.Type.Default:
            return TrayIcon._DEFAULT.format(notify=notify)
        elif theme == TrayIcon.Type.SLight:
            return TrayIcon._SYMBOLIC.format(color='#ffffff', notify=notify)
        else:
            return TrayIcon._SYMBOLIC.format(color='#241f31', notify=notify)

    @staticmethod
    def __build(svg_str) -> QIcon:
        svg_bytes = bytearray(svg_str, encoding='utf-8')
        qimg = QImage.fromData(svg_bytes, 'SVG')
        qpix = QPixmap.fromImage(qimg)
        return QIcon(qpix.scaled(QSize(128, 128)))
