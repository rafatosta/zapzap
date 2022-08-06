from PyQt6.QtGui import QImage, QPixmap, QIcon
from PyQt6.QtCore import QSize
import random

from zapzap.theme.icons import ICON_DEFAULT


def getNewIconSVG():
    newSVG = ICON_DEFAULT.replace('#209232', getColor())
    newSVG = newSVG.replace('#34c640', getColor())
    return newSVG


def getImageQPixmap(svg_str=ICON_DEFAULT) -> QPixmap:
    svg_bytes = bytearray(svg_str, encoding='utf-8')
    qimg = QImage.fromData(svg_bytes, 'SVG')
    return QPixmap.fromImage(qimg)


def getImageQIcon(svg_str=ICON_DEFAULT, scaled=[128, 128]) -> QIcon:
    qpix = getImageQPixmap(svg_str)
    qicon = QIcon(qpix.scaled(QSize(scaled[0], scaled[1])))
    return qicon


def getColor():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'rgb({r}, {g}, {b})'
