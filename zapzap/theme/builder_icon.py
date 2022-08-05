
import random

from zapzap.theme.icons import ICON_DEFAULT


def getNewIconSVG():
    newSVG = ICON_DEFAULT.replace('#209232', getColor())
    newSVG = newSVG.replace('#34c640', getColor())
    return newSVG


# retorna uma cor
def getColor():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'rgb({r}, {g}, {b})'
