"""Persistent main-window geometry and layout state."""

from __future__ import annotations

from PyQt6.QtCore import QByteArray

from zapzap.core.config.settings.base import BaseSettings


class WindowSettings(BaseSettings):
    """Semantic access to the existing main-window state keys."""

    _GEOMETRY = ("main/geometry", QByteArray())
    _LAYOUT_STATE = ("main/windowState", QByteArray())

    @property
    def geometry(self) -> QByteArray:
        return self._get(self._GEOMETRY)

    @geometry.setter
    def geometry(self, value: QByteArray) -> None:
        self._set(self._GEOMETRY, value)

    @property
    def layout_state(self) -> QByteArray:
        return self._get(self._LAYOUT_STATE)

    @layout_state.setter
    def layout_state(self, value: QByteArray) -> None:
        self._set(self._LAYOUT_STATE, value)
