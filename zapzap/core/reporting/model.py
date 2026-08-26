"""Canonical report representation shared by preview and GitHub handoff."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


def _freeze(value):
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value):
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class ReportDocument:
    """Immutable, sanitized content reviewed before local GitHub handoff."""

    data: Mapping[str, Any]

    def __post_init__(self):
        object.__setattr__(self, "data", _freeze(dict(self.data)))

    def payload(self) -> dict[str, Any]:
        """Return a serializable copy used by local storage and formatting."""
        return _thaw(self.data)
