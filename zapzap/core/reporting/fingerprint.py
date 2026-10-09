"""Deterministic, identity-free crash fingerprints."""

import hashlib
import html
import json
import re
import traceback


def crash_fingerprint(exc_type, exc_traceback, component: str = "application") -> str:
    frames = traceback.extract_tb(exc_traceback)[-5:] if exc_traceback else []
    stable_frames = [f"{frame.name}:{frame.filename.rsplit('/', 1)[-1]}" for frame in frames]
    source = "\n".join((exc_type.__name__, component, *stable_frames))
    return hashlib.sha256(source.encode("utf-8", errors="replace")).hexdigest()


def native_crash_signature(logs: str) -> dict:
    """Classify only the final faulthandler record, never a historical tail.

    Python frames describe a dispatch boundary, not a proven native cause.
    Paths, line numbers, thread addresses and message contents are excluded.
    """
    logs = html.unescape(logs)
    records = re.split(r"(?=Fatal Python error: )", logs)
    record = records[-1] if len(records) > 1 else ""
    signal_names = {
        "Segmentation fault": "SIGSEGV", "Aborted": "SIGABRT",
        "Bus error": "SIGBUS", "Illegal instruction": "SIGILL",
        "Floating point exception": "SIGFPE",
    }
    header = re.match(r"Fatal Python error: ([^\n]+)", record)
    signal_name = signal_names.get(header[1].strip(), "unknown") if header else "unknown"
    # all_threads output can start with unrelated worker threads. Prefer the
    # explicitly current thread, without borrowing frames from other threads.
    current = re.search(r"^Current thread[^\n]*:\n", record, re.MULTILINE)
    if current:
        stack = record[current.end():]
    else:
        stack = ""
    stack = re.split(r"\n(?:Thread |Current thread |Extension modules:|Current thread's C)", stack)[0]
    matches = re.findall(r'File "([^"]+)", line \d+ in ([^\n]+)', stack)
    frames = []
    for path, function in matches[:5]:
        path = path.replace("\\", "/")
        # Only application paths enter the signature. Foreign paths are not
        # useful identifiers and can contain usernames or arbitrary content.
        if "zapzap/" in path:
            path = "zapzap/" + path.rsplit("zapzap/", 1)[1]
            if re.fullmatch(r"[\w./-]+", path) and re.fullmatch(r"[\w<>]+", function):
                frames.append(f"{path}:{function}")
    if any("_teardown_webengine" in f or f.endswith(":close_pages") or f.endswith(":shutdown") for f in frames):
        component = "webengine-shutdown"
    elif any("browser/web/" in f or "webengine/" in f for f in frames):
        component = "webengine-dispatch"
    else:
        component = "application" if frames else "unknown"
    return {"signal": signal_name, "component": component, "frames": frames,
            "evidence": "python-boundary" if frames else "unresolved"}


def native_crash_fingerprints(signature: dict, system: dict) -> tuple[str, str]:
    """Keep a cross-version family and a separate loaded-library variant."""
    family = {key: signature[key] for key in ("signal", "component", "frames")}
    encoded = json.dumps(family, sort_keys=True, separators=(",", ":"))
    fingerprint = hashlib.sha256(encoded.encode()).hexdigest()
    versions = {key: system.get(key) for key in (
        "qt_runtime_version", "qt_webengine_version", "chromium_version",
        "pyqt_version", "pyqt_webengine_version", "sip_version",
    )}
    variant = hashlib.sha256((encoded + json.dumps(versions, sort_keys=True)).encode()).hexdigest()
    return fingerprint, variant
