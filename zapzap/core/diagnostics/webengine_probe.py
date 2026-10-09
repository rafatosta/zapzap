"""Opt-in local WebEngine evidence; never change lifecycle or handle signals."""

from contextlib import contextmanager
from enum import Enum
import json
import logging
import os
from pathlib import Path
import re
import threading
import time


MODES = ("baseline", "no-event-override", "consume-native-gestures")


def diagnostic_mode():
    value = os.environ.get("ZAPZAP_WEBENGINE_EVENT_MODE", "baseline")
    return value if value in MODES else "baseline"


class WebEngineProbe:
    MAX_BYTES = 4 * 1024 * 1024
    FIELDS = frozenset({"owner", "event_type", "gesture_type", "shutting_down",
                       "depth", "status", "exit_code", "accepted", "main_frame",
                       "mode", "phase", "kind", "clear_cache", "internal"})

    def __init__(self):
        self.enabled = False
        self.path = None
        self._fd = None
        self._size = 0
        self._objects = {}
        self._watched = set()
        self._counter = 0
        self._local = threading.local()
        self._lock = threading.RLock()

    def configure(self, directory, session_id):
        self.close()
        if os.environ.get("ZAPZAP_WEBENGINE_TRACE") != "1":
            return
        try:
            self.path = Path(directory) / f"webengine-{session_id}.jsonl"
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            self._size = self.path.stat().st_size
            self.enabled = True
            self.record("session_start", mode=diagnostic_mode())
            # Three recent sessions (each may have one rotated segment).
            files = sorted(
                (path for path in self.path.parent.glob("webengine-*.jsonl")
                 if re.fullmatch(r"webengine-[0-9a-f]{32}(?:\.previous)?\.jsonl", path.name)),
                key=lambda path: path.stat().st_mtime_ns, reverse=True,
            )
            for stale in files[6:]:
                stale.unlink()
        except OSError:
            self.close()
            logging.getLogger(__name__).warning("WebEngine trace unavailable", exc_info=True)

    def key(self, obj):
        object_id = id(obj)
        if object_id not in self._objects:
            self._counter += 1
            self._objects[object_id] = f"object-{self._counter}"
        return self._objects[object_id]

    def watch(self, obj, kind, owner=None):
        if not self.enabled:
            return
        object_id = id(obj)
        key = self.key(obj)
        if key in self._watched:
            if owner is not None:
                self.record("ownership", obj, owner=self.key(owner))
            return
        self._watched.add(key)
        self.record("created", obj, kind=kind, owner=self.key(owner) if owner is not None else None)

        def destroyed(_object=None):
            # Do not capture/query the destroyed QObject or call page()/profile().
            self._write("destroyed", key, {})
            if self._objects.get(object_id) == key:
                self._objects.pop(object_id, None)
            self._watched.discard(key)

        try:
            obj.destroyed.connect(destroyed)
            if kind.endswith("timer"):
                obj.timeout.connect(lambda: self._write("timer_timeout", key, {}))
        except (AttributeError, RuntimeError, TypeError):
            self.record("destroyed_signal_unavailable", obj)

    def record(self, action, obj=None, **fields):
        if not self.enabled:
            return
        safe = {}
        for name, value in fields.items():
            if name not in self.FIELDS:
                continue
            if isinstance(value, Enum):
                safe[name] = value.name
            elif isinstance(value, (str, int, bool)) or value is None:
                safe[name] = value
            else:
                safe[name] = getattr(value, "name", None)
        self._write(action, self.key(obj) if obj is not None else None, safe)

    def _write(self, action, key, fields):
        if not self.enabled:
            return
        entry = {"time_ns": time.monotonic_ns(), "thread": threading.get_ident(),
                 "action": action, "object": key, **fields}
        data = (json.dumps(entry, sort_keys=True) + "\n").encode()
        try:
            with self._lock:
                if not self.enabled or self._fd is None:
                    return
                if self._size + len(data) > self.MAX_BYTES:
                    os.close(self._fd)
                    self._fd = None
                    self.path.replace(self.path.with_suffix(".previous.jsonl"))
                    self._fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
                    self._size = 0
                # Unbuffered append: evidence before C++ dispatch survives a hard death.
                os.write(self._fd, data)
                self._size += len(data)
        except OSError:
            self.close()
            logging.getLogger(__name__).warning("WebEngine trace stopped after I/O failure", exc_info=True)

    @contextmanager
    def scope(self, action, obj, **fields):
        if not self.enabled:
            yield
            return
        depth = getattr(self._local, "depth", 0) + 1
        self._local.depth = depth
        self.record(action + "_enter", obj, depth=depth, **fields)
        try:
            yield
        finally:
            self.record(action + "_leave", obj, depth=depth)
            self._local.depth = depth - 1

    def dispatch_event(self, obj, event, dispatch):
        if not self.enabled:
            return dispatch(event)
        event_type = event.type()
        gesture = None
        if getattr(event_type, "name", "") == "NativeGesture":
            try:
                gesture = event.gestureType()
            except AttributeError:
                pass
        with self.scope("event", obj, event_type=event_type, gesture_type=gesture,
                        shutting_down=bool(getattr(obj, "_shutting_down", False))):
            return dispatch(event)

    def close(self):
        with self._lock:
            self.enabled = False
            if self._fd is not None:
                try:
                    os.close(self._fd)
                except OSError:
                    pass
            self._fd = None


probe = WebEngineProbe()
