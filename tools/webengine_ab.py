#!/usr/bin/env python3
"""Launch one process-only A/B variant in the installed Flatpak runtime."""

import argparse
import os
from pathlib import Path
import shlex
import subprocess


VARIANTS = ("baseline", "no-event-override", "consume-native-gestures")


def build_command(checkout, variant, trace=False):
    if variant not in VARIANTS:
        raise ValueError("Unknown A/B variant")
    checkout = Path(checkout).resolve()
    return [
        "flatpak", "run", f"--filesystem={checkout}", "--command=python3",
        f"--env=PYTHONPATH={checkout}",
        f"--env=ZAPZAP_WEBENGINE_EVENT_MODE={variant}",
        f"--env=ZAPZAP_WEBENGINE_TRACE={int(trace)}",
        "com.rtosta.zapzap", "-m", "zapzap",
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=VARIANTS, default="baseline")
    parser.add_argument("--trace", action="store_true", help="Enable local event/lifecycle JSONL evidence")
    parser.add_argument("--dry-run", action="store_true", help="Print command without starting ZapZap")
    parser.add_argument("--checkout", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    command = build_command(args.checkout, args.variant, args.trace)
    print(shlex.join(command), flush=True)
    if args.dry_run:
        return 0
    # No override, build, update, install, shell interpolation or persisted setting.
    # Let Qt/Chromium keep their existing renderer and sandbox configuration.
    environment = dict(os.environ)
    environment.pop("ZAPZAP_WEBENGINE_EVENT_MODE", None)
    environment.pop("ZAPZAP_WEBENGINE_TRACE", None)
    return subprocess.call(command, env=environment)


if __name__ == "__main__":
    raise SystemExit(main())
