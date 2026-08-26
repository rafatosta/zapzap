"""Canonical report representation shared by preview and submission."""

from __future__ import annotations

from dataclasses import dataclass
import json
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
    """Immutable payload; the UI renders this exact object before sending it."""

    data: Mapping[str, Any]

    def __post_init__(self):
        object.__setattr__(self, "data", _freeze(dict(self.data)))

    def payload(self) -> dict[str, Any]:
        """Return the only serializable representation accepted by submitters."""
        return _thaw(self.data)

    def to_json(self, *, pretty: bool = False) -> str:
        return json.dumps(
            self.payload(),
            ensure_ascii=False,
            indent=2 if pretty else None,
            sort_keys=True,
        )
