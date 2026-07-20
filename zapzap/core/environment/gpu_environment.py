"""Linux GPU topology helpers used before Qt WebEngine starts."""

from __future__ import annotations

from os import getenv
from pathlib import Path
from typing import Dict, List, Optional, Set, Union


_SYS_CLASS_DRM = Path("/sys/class/drm")
_DEV_DRI = Path("/dev/dri")


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


def preferred_render_node(
    drm_path: Union[str, Path] = _SYS_CLASS_DRM,
    dev_dri_path: Union[str, Path] = _DEV_DRI,
    dri_prime: Optional[str] = None,
) -> Optional[Path]:
    """Return the render node requested by an unambiguous DRI_PRIME.

    Qt WebEngine does not always propagate Mesa's device selection to its
    Chromium GPU process. Mirror unambiguous PCI and vendor/device DRI_PRIME
    selectors as a Chromium render-node override on multi-GPU systems.
    """

    selector = getenv("DRI_PRIME", "") if dri_prime is None else dri_prime
    if not selector.strip():
        return None

    try:
        drm_dir = Path(drm_path)
        render_nodes = _render_nodes_by_device(drm_dir)
        if len(render_nodes) < 2:
            return None
        selected = _render_node_for_dri_prime(render_nodes, selector)
        if selected is not None:
            return Path(dev_dri_path) / selected.name
    except OSError:
        return None

    return None


def _render_devices(drm_dir: Path) -> Set[Path]:
    return set(_render_nodes_by_device(drm_dir))


def _render_nodes_by_device(drm_dir: Path) -> Dict[Path, Path]:
    nodes: Dict[Path, Path] = {}
    for render_node in sorted(drm_dir.glob("renderD*")):
        if not render_node.name[7:].isdigit():
            continue
        nodes[_device_path(render_node)] = render_node
    return nodes


def _render_node_for_dri_prime(
    render_nodes: Dict[Path, Path], selector: str
) -> Optional[Path]:
    selector = selector.strip().lower()
    if selector.endswith("!"):
        selector = selector[:-1]
    if not selector:
        return None

    if selector.startswith("pci-"):
        parts = selector[4:].split("_")
        if len(parts) != 4:
            return None
        try:
            slot = f"{int(parts[0], 16):04x}:{int(parts[1], 16):02x}:"
            slot += f"{int(parts[2], 16):02x}.{int(parts[3], 16):x}"
        except ValueError:
            return None
        for device, render_node in render_nodes.items():
            if device.name.lower() == slot:
                return render_node
        return None

    ids = selector.split(":")
    if len(ids) != 2:
        return None
    try:
        requested_vendor = int(ids[0], 16)
        requested_device = int(ids[1], 16)
    except ValueError:
        return None

    matches: List[Path] = []
    for device, render_node in render_nodes.items():
        try:
            vendor = int(device.joinpath("vendor").read_text(encoding="utf-8"), 0)
            device_id = int(device.joinpath("device").read_text(encoding="utf-8"), 0)
        except (OSError, ValueError):
            continue
        if vendor == requested_vendor and device_id == requested_device:
            matches.append(render_node)
    return matches[0] if len(matches) == 1 else None


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
