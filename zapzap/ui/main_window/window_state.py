"""Window state that survives a trip to the system tray."""


class WindowStateMemory:
    """Remembers whether a window was maximized while it stays hidden.

    ``QWidget.showNormal()`` shows a window "neither maximized nor minimized
    nor fullscreen", so restoring a window that was hidden to the tray while
    maximized brings it back in its normal size. Windows record their state as
    they are hidden and reapply it when they are shown again.
    """

    # Defined on the class so the attribute always resolves, even on wrappers
    # that forward unknown attributes to an inner window via ``__getattr__``.
    _restore_maximized = False

    def remember_window_state(self) -> None:
        """Capture the state to return to. Call before hiding the window."""
        self._restore_maximized = self.isMaximized()

    def show_in_remembered_state(self, fullscreen: bool = False) -> None:
        """Show the window in the state captured when it was hidden."""
        if fullscreen:
            self.showFullScreen()
        elif self._restore_maximized:
            self.showMaximized()
        else:
            self.showNormal()
