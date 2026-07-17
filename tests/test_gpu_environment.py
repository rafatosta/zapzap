"""Tests for conservative Linux GPU topology detection."""

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

_GPU_ENVIRONMENT_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "zapzap",
    "core",
    "environment",
    "gpu_environment.py",
)
_SPEC = importlib.util.spec_from_file_location("zapzap_gpu_environment", _GPU_ENVIRONMENT_PATH)
_gpu_environment = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_gpu_environment)

has_headless_secondary_gpu = _gpu_environment.has_headless_secondary_gpu


class GpuEnvironmentTests(unittest.TestCase):
    def test_single_gpu_returns_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            drm = Path(tmp)
            self._add_gpu(drm, "card0", "renderD128", connected=True)

            self.assertFalse(has_headless_secondary_gpu(drm))

    def test_headless_secondary_gpu_returns_true(self):
        with tempfile.TemporaryDirectory() as tmp:
            drm = Path(tmp)
            self._add_gpu(drm, "card0", "renderD128", connected=True)
            self._add_gpu(drm, "card1", "renderD129", connected=False)

            self.assertTrue(has_headless_secondary_gpu(drm))

    def test_both_gpus_with_displays_return_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            drm = Path(tmp)
            self._add_gpu(drm, "card0", "renderD128", connected=True)
            self._add_gpu(drm, "card1", "renderD129", connected=True)

            self.assertFalse(has_headless_secondary_gpu(drm))

    def test_missing_connector_info_returns_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            drm = Path(tmp)
            self._add_gpu(drm, "card0", "renderD128", connected=True)
            self._add_gpu(drm, "card1", "renderD129", connected=False, connector=False)

            self.assertFalse(has_headless_secondary_gpu(drm))

    def test_redundant_render_nodes_for_one_gpu_return_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            drm = Path(tmp)
            device = drm / "devices" / "pci0000:00" / "0000:00:02.0"
            self._add_node(drm, "card0", device)
            self._add_node(drm, "renderD128", device)
            self._add_node(drm, "renderD129", device)
            connector = drm / "card0-HDMI-A-1"
            connector.mkdir()
            (connector / "status").write_text("connected\n", encoding="utf-8")

            self.assertFalse(has_headless_secondary_gpu(drm))

    def _add_gpu(self, drm, card, render, connected, connector=True):
        device = drm / "devices" / card
        self._add_node(drm, card, device)
        self._add_node(drm, render, device)
        if connector:
            output = drm / f"{card}-HDMI-A-1"
            output.mkdir()
            output.joinpath("status").write_text(
                ("connected" if connected else "disconnected") + "\n",
                encoding="utf-8",
            )

    def _add_node(self, drm, name, device):
        device.mkdir(parents=True, exist_ok=True)
        node = drm / name
        node.mkdir()
        node.joinpath("device").symlink_to(device, target_is_directory=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
