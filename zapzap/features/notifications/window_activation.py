"""Desktop activation helpers shared by Linux notification backends."""

from __future__ import annotations

import ctypes
import ctypes.util
from collections.abc import Mapping, Sequence
from contextlib import contextmanager
from os import environ

from PyQt6.QtCore import Qt
from PyQt6.QtDBus import QDBusVariant
from PyQt6.QtGui import QGuiApplication


_MISSING = object()
_XDG_ACTIVATION_TOKEN = "XDG_ACTIVATION_TOKEN"


def _unwrap_dbus_variant(value):
    while isinstance(value, QDBusVariant):
        value = value.variant()
    return value


def platform_activation_token(platform_data) -> str | None:
    """Extract an activation token from D-Bus platform data."""
    platform_data = _unwrap_dbus_variant(platform_data)
    if not isinstance(platform_data, Mapping):
        return None

    for key in ("activation-token", "desktop-startup-id"):
        token = _unwrap_dbus_variant(platform_data.get(key))
        if isinstance(token, str) and token:
            return token

    return None


def portal_activation_token(parameters) -> str | None:
    """Extract the portal platform activation token from an ``av`` payload."""
    if not isinstance(parameters, Sequence) or isinstance(
        parameters, (str, bytes, bytearray)
    ):
        return None

    for parameter in parameters:
        token = platform_activation_token(parameter)
        if token:
            return token

    return None


def _platform_name() -> str:
    return QGuiApplication.platformName().lower()


@contextmanager
def _temporary_environment(name: str, value: str):
    previous = environ.get(name, _MISSING)
    environ[name] = value
    try:
        yield
    finally:
        if previous is _MISSING:
            environ.pop(name, None)
        else:
            environ[name] = previous


class _XClientMessageData(ctypes.Union):
    _fields_ = [
        ("bytes", ctypes.c_char * 20),
        ("shorts", ctypes.c_short * 10),
        ("longs", ctypes.c_long * 5),
    ]


class _XClientMessageEvent(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int),
        ("serial", ctypes.c_ulong),
        ("send_event", ctypes.c_int),
        ("display", ctypes.c_void_p),
        ("window", ctypes.c_ulong),
        ("message_type", ctypes.c_ulong),
        ("format", ctypes.c_int),
        ("data", _XClientMessageData),
    ]


class _XEvent(ctypes.Union):
    _fields_ = [
        ("type", ctypes.c_int),
        ("xclient", _XClientMessageEvent),
        ("padding", ctypes.c_long * 24),
    ]


def _complete_x11_startup(startup_id: str) -> bool:
    """Finish X11 startup feedback without adding an Xlib Python dependency."""
    library_names = (
        ctypes.util.find_library("X11"),
        "libX11.so.6",
        "libX11.so",
    )

    xlib = None
    for library_name in library_names:
        if not library_name:
            continue
        try:
            xlib = ctypes.CDLL(library_name)
            break
        except OSError:
            continue

    if xlib is None:
        return False

    try:
        xlib.XOpenDisplay.argtypes = [ctypes.c_char_p]
        xlib.XOpenDisplay.restype = ctypes.c_void_p
        xlib.XDefaultScreen.argtypes = [ctypes.c_void_p]
        xlib.XDefaultScreen.restype = ctypes.c_int
        xlib.XRootWindow.argtypes = [ctypes.c_void_p, ctypes.c_int]
        xlib.XRootWindow.restype = ctypes.c_ulong
        xlib.XInternAtom.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_int,
        ]
        xlib.XInternAtom.restype = ctypes.c_ulong
        xlib.XSendEvent.argtypes = [
            ctypes.c_void_p,
            ctypes.c_ulong,
            ctypes.c_int,
            ctypes.c_long,
            ctypes.POINTER(_XEvent),
        ]
        xlib.XSendEvent.restype = ctypes.c_int
        xlib.XFlush.argtypes = [ctypes.c_void_p]
        xlib.XCloseDisplay.argtypes = [ctypes.c_void_p]

        display = xlib.XOpenDisplay(None)
        if not display:
            return False

        try:
            screen = xlib.XDefaultScreen(display)
            root = xlib.XRootWindow(display, screen)
            begin_atom = xlib.XInternAtom(
                display, b"_NET_STARTUP_INFO_BEGIN", False
            )
            continuation_atom = xlib.XInternAtom(
                display, b"_NET_STARTUP_INFO", False
            )
            message = f"remove: ID={startup_id}".encode() + b"\0"

            for offset in range(0, len(message), 20):
                event = _XEvent()
                event.xclient.type = 33  # ClientMessage
                event.xclient.display = display
                event.xclient.window = root
                event.xclient.message_type = (
                    begin_atom if offset == 0 else continuation_atom
                )
                event.xclient.format = 8
                chunk = message[offset:offset + 20]
                ctypes.memmove(
                    ctypes.addressof(event.xclient.data),
                    chunk,
                    len(chunk),
                )
                xlib.XSendEvent(
                    display,
                    root,
                    False,
                    1 << 22,  # PropertyChangeMask
                    ctypes.byref(event),
                )

            xlib.XFlush(display)
            return True
        finally:
            xlib.XCloseDisplay(display)
    except (AttributeError, OSError):
        return False


def _show_without_activating(window):
    """Map a hidden QWidget without starting a second activation request."""
    if window.isVisible():
        return

    attribute = Qt.WidgetAttribute.WA_ShowWithoutActivating
    already_set = window.testAttribute(attribute)
    if not already_set:
        window.setAttribute(attribute, True)

    try:
        window.show()
    finally:
        if not already_set:
            window.setAttribute(attribute, False)


def _present_and_activate(window):
    _show_without_activating(window)
    window.raise_()
    window.activateWindow()


def activate_window(window, activation_token: str | None = None):
    """Present a window and consume notification activation feedback."""
    platform = _platform_name()

    if activation_token and platform.startswith("wayland"):
        with _temporary_environment(
            _XDG_ACTIVATION_TOKEN, activation_token
        ):
            _present_and_activate(window)
        return

    if activation_token and platform == "xcb":
        _present_and_activate(window)
        _complete_x11_startup(activation_token)
        return

    _present_and_activate(window)
