import base64
import binascii
import json
import random
from enum import Enum

from PyQt6.QtCore import QBuffer, QIODevice, QSize, Qt
from PyQt6.QtGui import (
    QIcon,
    QImage,
    QImageReader,
    QPainter,
    QPainterPath,
    QPixmap,
    qAlpha,
    qBlue,
    qGray,
    qGreen,
    qRed,
    qRgba,
)


class UserIcon:
    """Classe para manipulação e criação de ícones personalizados para usuários."""

    class Type(Enum):
        Default = 1

    PHOTO_PREFIX = "data:image/png;base64,"
    PROFILE_PREFIX = "zapzap-account-image:v1:"
    PHOTO_SIZE = 256

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
    SVG_NOTIFICATION = """
  <rect y="116.592" width="{width}" height="136.107" style="fill: rgb(255, 0, 0); stroke: rgb(255, 0, 0);" rx="19.653" ry="19.653" x="{x}"/>
  <text style="fill: rgb(255, 255, 255); font-family: Arial, sans-serif; font-size: 65.9885px; text-anchor: end; white-space: pre;" transform="matrix(2.154438, 0, 0, 1.833654, -279.152802, -210.015335)" x="244.638" y="238.631">{number}</text>
"""

    @staticmethod
    def get_new_icon_svg() -> str:
        """Gera um novo SVG com cores aleatórias."""
        svg = UserIcon.ICON_DEFAULT.replace(
            '#209232', UserIcon._generate_random_color())
        return svg.replace('#34c640', UserIcon._generate_random_color())

    @staticmethod
    def is_photo(icon_data: str) -> bool:
        """Return whether the selected account image is an embedded photo."""
        profile = UserIcon._profile(icon_data)
        if profile is not None:
            return profile["type"] == "photo"
        return UserIcon._is_raw_photo(icon_data)

    @staticmethod
    def default_icon(icon_data: str) -> str:
        """Return the colored default icon retained in persisted account data."""
        profile = UserIcon._profile(icon_data)
        if profile is not None:
            return profile["icon"]
        if UserIcon._has_profile_prefix(icon_data):
            return UserIcon.ICON_DEFAULT
        if UserIcon._is_raw_photo(icon_data):
            return UserIcon.ICON_DEFAULT
        return icon_data or UserIcon.ICON_DEFAULT

    @staticmethod
    def photo(icon_data: str):
        """Return the retained embedded photo, if any."""
        profile = UserIcon._profile(icon_data)
        if profile is not None:
            return profile["photo"]
        return icon_data if UserIcon._is_raw_photo(icon_data) else None

    @staticmethod
    def persisted_image(
        default_icon: str,
        photo_data: str = None,
        use_photo: bool = False,
    ) -> str:
        """Build the persisted representation while retaining both choices."""
        if not photo_data:
            return default_icon or UserIcon.ICON_DEFAULT
        profile = {
            "type": "photo" if use_photo else "icon",
            "icon": default_icon or UserIcon.ICON_DEFAULT,
            "photo": photo_data,
        }
        return UserIcon.PROFILE_PREFIX + json.dumps(
            profile,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    @staticmethod
    def _is_raw_photo(icon_data: str) -> bool:
        return bool(
            isinstance(icon_data, str)
            and icon_data.startswith(UserIcon.PHOTO_PREFIX)
        )

    @staticmethod
    def _profile(icon_data: str):
        if not UserIcon._has_profile_prefix(icon_data):
            return None
        try:
            profile = json.loads(icon_data[len(UserIcon.PROFILE_PREFIX):])
        except (TypeError, ValueError):
            return None
        if (
            not isinstance(profile, dict)
            or profile.get("type") not in ("icon", "photo")
            or not isinstance(profile.get("icon"), str)
            or not UserIcon._is_raw_photo(profile.get("photo"))
        ):
            return None
        return profile

    @staticmethod
    def _has_profile_prefix(icon_data: str) -> bool:
        return bool(
            isinstance(icon_data, str)
            and icon_data.startswith(UserIcon.PROFILE_PREFIX)
        )

    @staticmethod
    def photo_from_file(file_path: str) -> str:
        """Load, normalize and encode an account photo for persistence."""
        reader = QImageReader(file_path)
        reader.setAutoTransform(True)
        image = reader.read()
        if image.isNull():
            raise ValueError(reader.errorString() or "Invalid image")
        return UserIcon.photo_from_image(image)

    @staticmethod
    def photo_from_image(image: QImage) -> str:
        """Crop an image to a circle and encode it as a bounded PNG data URI."""
        if image.isNull():
            raise ValueError("Invalid image")

        side = min(image.width(), image.height())
        square = image.copy(
            (image.width() - side) // 2,
            (image.height() - side) // 2,
            side,
            side,
        ).scaled(
            QSize(UserIcon.PHOTO_SIZE, UserIcon.PHOTO_SIZE),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        result = QImage(
            UserIcon.PHOTO_SIZE,
            UserIcon.PHOTO_SIZE,
            QImage.Format.Format_ARGB32_Premultiplied,
        )
        result.fill(Qt.GlobalColor.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        clip = QPainterPath()
        clip.addEllipse(0, 0, UserIcon.PHOTO_SIZE, UserIcon.PHOTO_SIZE)
        painter.setClipPath(clip)
        painter.drawImage(0, 0, square)
        painter.end()

        buffer = QBuffer()
        if not buffer.open(QIODevice.OpenModeFlag.WriteOnly):
            raise ValueError("Could not encode image")
        try:
            if not result.save(buffer, "PNG"):
                raise ValueError("Could not encode image")
            encoded = bytes(buffer.data().toBase64()).decode("ascii")
        finally:
            buffer.close()
        return f"{UserIcon.PHOTO_PREFIX}{encoded}"

    @staticmethod
    def _generate_random_color():
        """Gera uma cor aleatória em rgb"""
        return f'rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})'

    @staticmethod
    def get_icon(icon_data: str = ICON_DEFAULT, icon_type=Type.Default, qtd: int = 0) -> QIcon:
        """Build an account icon from its persisted SVG or embedded photo."""
        profile = UserIcon._profile(icon_data)
        if profile is not None:
            icon_data = (
                profile["photo"]
                if profile["type"] == "photo"
                else profile["icon"]
            )
        elif UserIcon._has_profile_prefix(icon_data):
            icon_data = UserIcon.ICON_DEFAULT
        if UserIcon._is_raw_photo(icon_data):
            return UserIcon._build_photo_icon(icon_data, icon_type, qtd)

        svg_str = icon_data or UserIcon.ICON_DEFAULT
        if icon_type == UserIcon.Type.Default:
            qtd = 999 if qtd >= 1000 else qtd
            data = UserIcon._get_notification_data(qtd)
            notification = UserIcon.SVG_NOTIFICATION.format(
                x=data['x'], width=data['width'], number=qtd)
            svg = svg_str.format(notification if qtd > 0 else "")
        return UserIcon.__build(svg)

    @staticmethod
    def grayscale_icon(
        icon: QIcon,
        intensity: float = 1.0,
        opacity: float = 0.82,
    ) -> QIcon:
        """Return an in-memory grayscale copy without changing stored data."""
        sizes = icon.availableSizes()
        source_size = (
            max(sizes, key=lambda size: size.width() * size.height())
            if sizes
            else QSize(UserIcon.PHOTO_SIZE, UserIcon.PHOTO_SIZE)
        )
        source = icon.pixmap(source_size).toImage().convertToFormat(
            QImage.Format.Format_ARGB32
        )
        grayscale = QImage(source.size(), QImage.Format.Format_ARGB32)
        grayscale.fill(Qt.GlobalColor.transparent)

        intensity = max(0.0, min(1.0, intensity))
        opacity = max(0.0, min(1.0, opacity))
        for y in range(source.height()):
            for x in range(source.width()):
                pixel = source.pixel(x, y)
                gray = qGray(pixel)
                red = round(qRed(pixel) + (gray - qRed(pixel)) * intensity)
                green = round(
                    qGreen(pixel) + (gray - qGreen(pixel)) * intensity
                )
                blue = round(
                    qBlue(pixel) + (gray - qBlue(pixel)) * intensity
                )
                alpha = round(qAlpha(pixel) * opacity)
                grayscale.setPixel(
                    x,
                    y,
                    qRgba(red, green, blue, alpha),
                )

        return QIcon(QPixmap.fromImage(grayscale))

    @staticmethod
    def _build_photo_icon(icon_data: str, icon_type, qtd: int) -> QIcon:
        try:
            encoded = icon_data[len(UserIcon.PHOTO_PREFIX):]
            photo_bytes = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error):
            return UserIcon.get_icon(UserIcon.ICON_DEFAULT, icon_type, qtd)

        image = QImage.fromData(photo_bytes, "PNG")
        if image.isNull():
            return UserIcon.get_icon(UserIcon.ICON_DEFAULT, icon_type, qtd)
        image = image.scaled(
            QSize(UserIcon.PHOTO_SIZE, UserIcon.PHOTO_SIZE),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        if icon_type == UserIcon.Type.Default and qtd > 0:
            qtd = 999 if qtd >= 1000 else qtd
            data = UserIcon._get_notification_data(qtd)
            overlay = UserIcon.SVG_NOTIFICATION.format(
                x=data["x"], width=data["width"], number=qtd
            )
        else:
            overlay = ""

        if overlay:
            overlay_svg = (
                '<svg viewBox="0 0 256 256" '
                'xmlns="http://www.w3.org/2000/svg">'
                f"{overlay}</svg>"
            )
            overlay_image = QImage.fromData(
                overlay_svg.encode("utf-8"), "SVG"
            )
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.drawImage(0, 0, overlay_image)
            painter.end()

        pixmap = QPixmap.fromImage(image)
        return QIcon(
            pixmap.scaled(
                QSize(128, 128),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

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
