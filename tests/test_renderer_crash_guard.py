"""Tests for RendererCrashGuard: repeated-crash escalation logic."""

import importlib.util
import os
import unittest

_GUARD_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "zapzap",
    "core",
    "environment",
    "renderer_crash_guard.py",
)
_SPEC = importlib.util.spec_from_file_location("zapzap_renderer_crash_guard", _GUARD_PATH)
_guard_module = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_guard_module)

RendererCrashGuard = _guard_module.RendererCrashGuard


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class RendererCrashGuardTests(unittest.TestCase):
    def test_single_crash_does_not_escalate(self):
        guard = RendererCrashGuard(clock=FakeClock())
        self.assertFalse(guard.record_crash())
        self.assertEqual(guard.recent_crash_count, 1)

    def test_three_rapid_crashes_escalate_once(self):
        clock = FakeClock()
        guard = RendererCrashGuard(clock=clock)
        self.assertFalse(guard.record_crash())
        clock.advance(10)
        self.assertFalse(guard.record_crash())
        clock.advance(10)
        self.assertTrue(guard.record_crash())
        # Already escalated: further crashes in the same burst stay False.
        clock.advance(10)
        self.assertFalse(guard.record_crash())

    def test_old_crashes_slide_out_of_window(self):
        clock = FakeClock()
        guard = RendererCrashGuard(clock=clock)
        guard.record_crash()
        guard.record_crash()
        clock.advance(400)  # past the 300s window
        self.assertFalse(guard.record_crash())
        self.assertEqual(guard.recent_crash_count, 1)

    def test_recovery_clears_history(self):
        clock = FakeClock()
        guard = RendererCrashGuard(clock=clock)
        guard.record_crash()
        guard.record_crash()
        guard.record_recovery()
        self.assertEqual(guard.recent_crash_count, 0)
        clock.advance(10)
        self.assertFalse(guard.record_crash())

    def test_new_burst_after_quiet_period_escalates_again(self):
        clock = FakeClock()
        guard = RendererCrashGuard(clock=clock)
        guard.record_crash()
        guard.record_crash()
        self.assertTrue(guard.record_crash())
        clock.advance(400)
        guard.record_crash()
        guard.record_crash()
        self.assertTrue(guard.record_crash())


if __name__ == "__main__":
    unittest.main()
