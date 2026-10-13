"""In-process UserNotifications adapter; no helper identity or Siri donation."""
from __future__ import annotations

import ctypes
from pathlib import Path
import platform
import sys

from PyQt6.QtCore import QByteArray, QBuffer, QIODevice, QObject, Qt, pyqtSignal
from PyQt6.QtGui import QImage


def avatar_png(image: QImage) -> bytes:
    if image.isNull():
        return b""
    if image.width() > 512 or image.height() > 512:
        image = image.scaled(
            512, 512, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    array = QByteArray()
    buffer = QBuffer(array)
    if not buffer.open(QIODevice.OpenModeFlag.WriteOnly) or not image.save(buffer, "PNG"):
        raise ValueError("notification image encoding failed")
    return bytes(array)


class NativeMacNotifications(QObject):
    event = pyqtSignal(str, int, int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        version = platform.mac_ver()[0].split(".")
        if sys.platform != "darwin" or not version[0].isdigit() or int(version[0]) < 12:
            raise OSError("native communication notifications require macOS 12 or later")
        library = Path(__file__).with_name("libZapZapNotifications.dylib")
        self.library = ctypes.CDLL(str(library))
        callback_type = ctypes.CFUNCTYPE(
            None, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        )
        self._callback = callback_type(self._receive)
        self.library.zn_install.argtypes = [callback_type]
        self.library.zn_install.restype = ctypes.c_int
        self.library.zn_send.argtypes = [
            ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p,
            ctypes.c_void_p, ctypes.c_size_t,
        ]
        self.library.zn_send.restype = ctypes.c_int
        self.library.zn_send_message.argtypes = [
            ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p,
            ctypes.c_void_p, ctypes.c_size_t, ctypes.c_char_p,
            ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t,
        ]
        self.library.zn_send_message.restype = ctypes.c_int
        self.library.zn_remove.argtypes = [ctypes.c_char_p]
        self.library.zn_remove.restype = None
        if not self.library.zn_install(self._callback):
            raise OSError("native notifications require the main application bundle")

    def _receive(self, identifier, event, error, attachments, authorization):
        self.event.emit(identifier.decode("ascii"), event, error, attachments, authorization)

    def send(
        self, identifier, title, body, image, *, decorate=True,
        conversation_id=None, sender_name=None, group_name=None, group_image=None,
    ):
        """Group roles are explicit; hidden/app images must not be decorated."""
        png = avatar_png(image)
        data = ctypes.create_string_buffer(png) if png else None
        if decorate and png:
            group_png = avatar_png(group_image) if group_image is not None and group_name else b""
            group_data = ctypes.create_string_buffer(group_png) if group_png else None

            def encode(value):
                return value.encode("utf-8") if value else None

            return bool(self.library.zn_send_message(
                identifier.encode("ascii"), title.encode("utf-8"), body.encode("utf-8"),
                data, len(png), encode(conversation_id), encode(sender_name),
                encode(group_name), group_data, len(group_png),
            ))
        return bool(self.library.zn_send(
            identifier.encode("ascii"), title.encode("utf-8"), body.encode("utf-8"),
            data, len(png),
        ))

    def remove(self, identifier):
        self.library.zn_remove(identifier.encode("ascii"))
