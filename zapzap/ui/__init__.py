"""
ZapZap UI package — Phase 1 foundation.

Exports:

* DesignTokens      — single source of truth for design tokens
* AccessibilityManager — WCAG helpers
* components        — reusable widget library (buttons, inputs, cards, dialogs)
"""

from .design_tokens import DesignTokens
from .accessibility import AccessibilityManager
from . import components

__all__ = [
    "DesignTokens",
    "AccessibilityManager",
    "components",
]
