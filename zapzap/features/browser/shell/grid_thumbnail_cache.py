"""Bounded in-memory thumbnails for the browser grid."""

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap


GRID_THUMBNAIL_MAX_PHYSICAL_SIZE = QSize(480, 300)


class GridThumbnailCache:
    """Own at most one normalized grid thumbnail per account."""

    def __init__(self, max_physical_size=GRID_THUMBNAIL_MAX_PHYSICAL_SIZE):
        self._max_physical_size = QSize(max_physical_size)
        self._thumbnails = {}

    def store(self, user_id, capture):
        """Replace an account thumbnail with a bounded, DPR-neutral pixmap."""
        self.invalidate(user_id)
        thumbnail = self._normalized(capture)
        if thumbnail is not None:
            self._thumbnails[user_id] = thumbnail
        return thumbnail

    def get(self, user_id):
        return self._thumbnails.get(user_id)

    def invalidate(self, user_id):
        self._thumbnails.pop(user_id, None)

    def clear(self):
        self._thumbnails.clear()

    def __len__(self):
        return len(self._thumbnails)

    def _normalized(self, capture):
        if capture is None or capture.isNull():
            return None

        max_width = self._max_physical_size.width()
        max_height = self._max_physical_size.height()
        if capture.width() > max_width or capture.height() > max_height:
            capture = capture.scaled(
                self._max_physical_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        else:
            capture = QPixmap(capture)

        # QPixmap dimensions describe the native buffer. Resetting DPR makes
        # its logical size match that bounded buffer instead of multiplying the
        # grid's memory budget on HiDPI displays. At 32 bpp, each entry retains
        # at most 480 * 300 * 4 bytes (about 563 KiB).
        capture.setDevicePixelRatio(1.0)
        return capture
