"""Base model for context-oriented settings pages."""

from __future__ import annotations


class ContextSettingsModel:
    """Base model for settings contexts that do not need persistence yet."""

    def __init__(self, context: str):
        self.context = context
