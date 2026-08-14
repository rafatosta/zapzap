"""Persistent main-window geometry and layout state."""

from __future__ import annotations

import logging
from typing import Any

from PyQt6.QtCore import QByteArray

from zapzap.core.config.settings.base import BaseSettings


logger = logging.getLogger(__name__)


def _normalize_byte_array(value: Any) -> tuple[QByteArray, bool]:
    if isinstance(value, QByteArray):
        return value, True
    if isinstance(value, (bytes, bytearray, memoryview)):
        return QByteArray(bytes(value)), True
    return QByteArray(), False


class WindowSettings(BaseSettings):
    """Semantic access to the existing main-window state keys."""

    _GEOMETRY = ("main/geometry", QByteArray())
    _LAYOUT_STATE = ("main/windowState", QByteArray())

    @property
    def geometry(self) -> QByteArray:
        geometry, valid = _normalize_byte_array(self._get(self._GEOMETRY))
        if not valid:
            logger.warning(
                "Invalid stored window geometry; replacing it with an empty state"
            )
            self.geometry = geometry
        return geometry

    @geometry.setter
    def geometry(self, value: QByteArray) -> None:
        geometry, _valid = _normalize_byte_array(value)
        self._set(self._GEOMETRY, geometry)

    @property
    def layout_state(self) -> QByteArray:
        layout_state, valid = _normalize_byte_array(
            self._get(self._LAYOUT_STATE)
        )
        if not valid:
            logger.warning(
                "Invalid stored window layout; replacing it with an empty state"
            )
            self.layout_state = layout_state
        return layout_state

    @layout_state.setter
    def layout_state(self, value: QByteArray) -> None:
        layout_state, _valid = _normalize_byte_array(value)
        self._set(self._LAYOUT_STATE, layout_state)
