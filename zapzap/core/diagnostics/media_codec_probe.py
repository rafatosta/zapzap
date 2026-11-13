"""Read-only media codec evidence collected from a loaded WebEngine page.

The probe only asks the engine which *container/codec pairs* it advertises
through ``HTMLMediaElement.canPlayType`` and ``MediaSource.isTypeSupported``.
It never reads page content, media files, network responses or storage, and it
does not change playback, flags or lifecycle. A page that never loaded keeps
``measured`` false so reports never present an unobserved capability as fact.
"""

from __future__ import annotations

from copy import deepcopy
import json
import logging


logger = logging.getLogger(__name__)

# Fixed evidence keys. WhatsApp Web media relies on H.264 video and AAC audio;
# anything outside this allowlist is discarded before it reaches a report.
CHECK_KEYS = ("h264", "aac")

CAN_PLAY_VALUES = ("probably", "maybe", "no")

PROBE_PROPERTY = "zapzapMediaCodecProbeRequested"

PROBE_SCRIPT = r"""
(function () {
  try {
    var canPlay = function (tag, mime) {
      try {
        var element = document.createElement(tag);
        if (!element.canPlayType) { return "no"; }
        var value = element.canPlayType(mime);
        return (value === "probably" || value === "maybe") ? value : "no";
      } catch (error) {
        return "no";
      }
    };
    var isTypeSupported = function (mime) {
      try {
        if (!window.MediaSource ||
            typeof window.MediaSource.isTypeSupported !== "function") {
          return null;
        }
        return !!window.MediaSource.isTypeSupported(mime);
      } catch (error) {
        return null;
      }
    };
    return JSON.stringify({
      can_play: {
        h264: canPlay("video", 'video/mp4; codecs="avc1.42E01E"'),
        aac: canPlay("audio", 'audio/mp4; codecs="mp4a.40.2"')
      },
      mse: {
        h264: isTypeSupported('video/mp4; codecs="avc1.42E01E"'),
        aac: isTypeSupported('audio/mp4; codecs="mp4a.40.2"')
      }
    });
  } catch (error) {
    return "";
  }
})()
"""


def _unmeasured(reason: str) -> dict:
    return {
        "measured": False,
        "reason": reason,
        "source": "page",
        "can_play": {},
        "mse": {},
        "missing": [],
    }


class MediaCodecProbe:
    """Store the latest allowlisted codec measurement for diagnostics only."""

    def __init__(self):
        self._snapshot = _unmeasured("not-run")

    def request(self, page) -> bool:
        """Ask a loaded page once; never raise or block the page."""
        if page is None:
            return False

        try:
            if page.property(PROBE_PROPERTY):
                return False
            page.setProperty(PROBE_PROPERTY, True)
            page.runJavaScript(PROBE_SCRIPT, self.record)
            return True
        except (AttributeError, RuntimeError, TypeError):
            self._mark_unavailable()
            return False

    def record(self, payload) -> None:
        """Normalize one probe reply, discarding anything outside the schema."""
        try:
            data = json.loads(payload) if isinstance(payload, str) else None
        except (TypeError, ValueError):
            data = None

        if not isinstance(data, dict):
            self._mark_unavailable()
            return

        can_play_data = data.get("can_play")
        mse_data = data.get("mse")
        if not isinstance(can_play_data, dict) or not isinstance(mse_data, dict):
            self._mark_unavailable()
            return

        can_play = {}
        for key in CHECK_KEYS:
            value = can_play_data.get(key)
            can_play[key] = value if value in CAN_PLAY_VALUES else "unknown"

        mse = {}
        for key in CHECK_KEYS:
            value = mse_data.get(key)
            mse[key] = value if isinstance(value, bool) else None

        missing = [
            key for key in CHECK_KEYS
            if can_play[key] == "no" and mse[key] is not True
        ]
        self._snapshot = {
            "measured": True,
            "reason": None,
            "source": "page",
            "can_play": can_play,
            "mse": mse,
            "missing": missing,
        }

    def snapshot(self) -> dict:
        """Return an immutable copy safe to read from another thread."""
        return deepcopy(self._snapshot)

    def reset(self) -> None:
        self._snapshot = _unmeasured("not-run")

    def _mark_unavailable(self) -> None:
        # Keep an earlier valid measurement; a later failure must not erase it.
        if not self._snapshot["measured"]:
            self._snapshot = _unmeasured("unavailable")


media_codecs = MediaCodecProbe()
