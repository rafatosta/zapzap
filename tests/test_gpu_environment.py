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
preferred_render_node = _gpu_environment.preferred_render_node


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

    def test_single_gpu_dri_prime_does_not_add_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            drm = Path(tmp)
            self._add_gpu(
                drm, "card0", "renderD128", connected=True,
                vendor="0x1002", device_id="0x73e3",
            )

            self.assertIsNone(
                preferred_render_node(
                    drm, "/test/dev/dri", dri_prime="1002:73e3"
                )
            )

    def test_numeric_dri_prime_is_not_guessed(self):
        with tempfile.TemporaryDirectory() as tmp:
            drm = Path(tmp)
            self._add_gpu(drm, "card0", "renderD128", connected=True)
            self._add_gpu(drm, "card1", "renderD129", connected=True)

            self.assertIsNone(
                preferred_render_node(drm, "/test/dev/dri", dri_prime="1")
            )

    def test_empty_dri_prime_does_not_add_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            drm = Path(tmp)
            self._add_gpu(drm, "card0", "renderD128", connected=True)
            self._add_gpu(drm, "card1", "renderD129", connected=False)

            self.assertIsNone(
                preferred_render_node(drm, "/test/dev/dri", dri_prime="")
            )

    def test_dri_prime_vendor_device_overrides_ambiguous_connectors(self):
        with tempfile.TemporaryDirectory() as tmp:
            drm = Path(tmp)
            self._add_gpu(
                drm, "card0", "renderD128", connected=True,
                vendor="0x1002", device_id="0x73e3",
            )
            self._add_gpu(
                drm, "card1", "renderD129", connected=True,
                vendor="0x10de", device_id="0x2b85",
            )

            self.assertEqual(
                preferred_render_node(
                    drm, "/test/dev/dri", dri_prime="1002:73e3!"
                ),
                Path("/test/dev/dri/renderD128"),
            )

    def test_dri_prime_pci_selector_maps_to_render_node(self):
        with tempfile.TemporaryDirectory() as tmp:
            drm = Path(tmp)
            self._add_gpu(
                drm, "card0", "renderD128", connected=True,
                pci_slot="0000:05:00.0",
            )
            self._add_gpu(
                drm, "card1", "renderD129", connected=True,
                pci_slot="0000:01:00.0",
            )

            self.assertEqual(
                preferred_render_node(
                    drm, "/test/dev/dri", dri_prime="pci-0000_05_00_0"
                ),
                Path("/test/dev/dri/renderD128"),
            )

    def test_duplicate_vendor_device_selector_is_ambiguous(self):
        with tempfile.TemporaryDirectory() as tmp:
            drm = Path(tmp)
            self._add_gpu(
                drm, "card0", "renderD128", connected=True,
                vendor="0x1002", device_id="0x73e3",
            )
            self._add_gpu(
                drm, "card1", "renderD129", connected=True,
                vendor="0x1002", device_id="0x73e3",
            )

            self.assertIsNone(
                preferred_render_node(
                    drm, "/test/dev/dri", dri_prime="1002:73e3"
                )
            )

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

    def _add_gpu(
        self, drm, card, render, connected, connector=True,
        vendor=None, device_id=None, pci_slot=None,
    ):
        device = drm / "devices" / (pci_slot or card)
        device.mkdir(parents=True, exist_ok=True)
        if vendor is not None:
            device.joinpath("vendor").write_text(vendor + "\n", encoding="utf-8")
        if device_id is not None:
            device.joinpath("device").write_text(device_id + "\n", encoding="utf-8")
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
