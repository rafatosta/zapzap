"""Escalate repeated renderer crashes to a safer GPU configuration.

The ``renderProcessTerminated`` signal fires when a Chromium renderer dies
(SIGTRAP/SIGSEGV in ``QtWebEngineProcess``) while the browser process stays
alive. Reloading the page is the right first response, but when crashes
repeat in a tight loop the reload itself just burns CPU and coredumps
without ever recovering. This guard counts recent crashes per view and,
once a threshold is crossed, persists ``--disable-gpu-compositing`` so the
next startup renders without the GPU compositing path that usually traps.

Design notes (see ``docs/webengine-crash-investigation.md``):

- Renderer crashes are a separate group from browser-process SIGSEGV,
  video/GPU aborts, reentrant navigation, and shutdown races. This module
  only tracks ``renderProcessTerminated`` events.
- The decision is monotonic: once escalated, the setting stays on until
  the user changes it in Settings → Performance. No automatic re-enable,
  no timer-based reset.
- State is process-local (crash timestamps per guard instance). The only
  persisted effect is the ``performance/auto_gpu_workaround``-adjacent
  settings flag, written through ``SettingsManager`` so it survives
  restarts and shows up in the existing Performance UI.
"""

from __future__ import annotations

import time
from collections import deque
from typing import Deque

#: How many renderer crashes inside ``WINDOW_SECONDS`` trigger escalation.
CRASH_THRESHOLD = 3
#: Sliding window (seconds) in which crashes are counted.
WINDOW_SECONDS = 300.0


class RendererCrashGuard:
    """Count recent renderer crashes and escalate once when looping."""

    def __init__(
        self,
        threshold: int = CRASH_THRESHOLD,
        window_seconds: float = WINDOW_SECONDS,
        clock=time.monotonic,
    ) -> None:
        self._threshold = max(1, int(threshold))
        self._window = max(1.0, float(window_seconds))
        self._clock = clock
        self._crashes: Deque[float] = deque()
        self._escalated = False

    def record_crash(self) -> bool:
        """Record one renderer crash.

        Returns True exactly once, on the crash that crosses the
        threshold. Later calls return False until the window slides
        past old crashes and a new burst crosses again.
        """
        now = self._clock()
        cutoff = now - self._window
        while self._crashes and self._crashes[0] <= cutoff:
            self._crashes.popleft()
        self._crashes.append(now)
        if len(self._crashes) >= self._threshold and not self._escalated:
            self._escalated = True
            return True
        if len(self._crashes) < self._threshold:
            self._escalated = False
        return False

    def record_recovery(self) -> None:
        """Clear crash history after a page loads successfully."""
        self._crashes.clear()
        self._escalated = False

    @property
    def recent_crash_count(self) -> int:
        """Number of crashes inside the current window (for diagnostics)."""
        cutoff = self._clock() - self._window
        return sum(1 for stamp in self._crashes if stamp > cutoff)
