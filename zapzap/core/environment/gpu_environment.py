"""Linux GPU topology helpers used before Qt WebEngine starts."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Set, Union


_SYS_CLASS_DRM = Path("/sys/class/drm")


def has_headless_secondary_gpu(drm_path: Union[str, Path] = _SYS_CLASS_DRM) -> bool:
    """Return True for multi-GPU systems with a display-less render GPU.

    The probe is intentionally conservative: if sysfs is unavailable, has a
    single render GPU, or does not expose connector status for every render GPU,
    it returns ``False`` so single-GPU systems and unusual environments are not
    changed.
    """

    try:
        drm_dir = Path(drm_path)
        render_devices = _render_devices(drm_dir)
        if len(render_devices) < 2:
            return False

        connector_states = _connector_states_by_device(drm_dir)
        if not connector_states:
            return False

        has_connected_gpu = False
        has_headless_gpu = False

        for device in render_devices:
            states = connector_states.get(device)
            if not states:
                return False
            if any(state == "connected" for state in states):
                has_connected_gpu = True
            else:
                has_headless_gpu = True

        return has_connected_gpu and has_headless_gpu
    except OSError:
        return False


def _render_devices(drm_dir: Path) -> Set[Path]:
    devices: Set[Path] = set()
    for render_node in drm_dir.glob("renderD*"):
        if not render_node.name[7:].isdigit():
            continue
        devices.add(_device_path(render_node))
    return devices


def _connector_states_by_device(drm_dir: Path) -> Dict[Path, List[str]]:
    states_by_device: Dict[Path, List[str]] = {}
    for connector in drm_dir.glob("card*-*"):
        status_file = connector / "status"
        if not status_file.is_file():
            continue

        card_name = connector.name.split("-", 1)[0]
        card = drm_dir / card_name
        if not card.exists():
            continue

        state = status_file.read_text(encoding="utf-8").strip().lower()
        states_by_device.setdefault(_device_path(card), []).append(state)

    return states_by_device


def _device_path(drm_node: Path) -> Path:
    return (drm_node / "device").resolve(strict=True)
