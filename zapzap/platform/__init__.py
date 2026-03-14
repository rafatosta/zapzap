"""
Platform detection helpers for cross-platform support.
Import from here instead of testing sys.platform directly.
"""
import sys

IS_WINDOWS = sys.platform == "win32"
IS_LINUX   = sys.platform.startswith("linux")
IS_MAC     = sys.platform == "darwin"
