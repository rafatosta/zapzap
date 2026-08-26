"""Deterministic, identity-free crash fingerprints."""

import hashlib
import traceback


def crash_fingerprint(exc_type, exc_traceback, component: str = "application") -> str:
    frames = traceback.extract_tb(exc_traceback)[-5:] if exc_traceback else []
    stable_frames = [f"{frame.name}:{frame.filename.rsplit('/', 1)[-1]}" for frame in frames]
    source = "\n".join((exc_type.__name__, component, *stable_frames))
    return hashlib.sha256(source.encode("utf-8", errors="replace")).hexdigest()
