from zapzap.controllers.main_window_components.builder_icon import getIconTray
from PyQt6.QtGui import QImage, QPixmap, QIcon
from PyQt6.QtCore import QSize
import zapzap
import random

from zapzap.theme.icons import ICON_DEFAULT, SVG_NOTIFICATION


def getNewIconSVG():
    newSVG = ICON_DEFAULT.replace('#209232', getColor())
    newSVG = newSVG.replace('#34c640', getColor())
    return newSVG


def getImageQPixmap(svg_str=ICON_DEFAULT) -> QPixmap:
    svg_bytes = bytearray(svg_str, encoding='utf-8')
    qimg = QImage.fromData(svg_bytes, 'SVG')
    return QPixmap.fromImage(qimg)


def getImageQIcon(svg_str=ICON_DEFAULT, scaled=[256, 256], qtd=0) -> QIcon:

    if len(str(qtd)) == 1:
        data = dict(width=100.1, x=152.6)
    elif len(str(qtd)) == 2:
        data = dict(width=180.3, x=72.5)
    else:
        data = dict(width=249.428, x=3.286)

    notification = SVG_NOTIFICATION.format(
        x=data['x'], width=data['width'], number=qtd)

    n = notification if qtd > 0 else ""

    qpix = getImageQPixmap(svg_str.format(n))
    qicon = QIcon(qpix.scaled(QSize(scaled[0], scaled[1])))
    return qicon


def getColor():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'rgb({r}, {g}, {b})'

def getIconDefaultURLNotification() -> str:
    try:
        qIcon = getIconTray()
        qpix = qIcon.pixmap(QSize(128, 128))
        path = zapzap.path_tmp+'/com.rtosta.zapzap.png'
        qpix.save(path)
        return path
    except Exception as e:
        print(e)
        return ""