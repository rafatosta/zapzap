"""Detecção de topologia multi-GPU para evitar crash de GBM/EGL no Chromium.

Em máquinas com mais de uma GPU onde a GPU secundária é "headless" (sem monitor
conectado) enquanto outra GPU controla a tela, o processo de GPU do Chromium
pode selecionar o render node da GPU errada para alocar buffers GBM. O import
entre dispositivos distintos falha (gbm_bo_import -> EGL_BAD_MATCH) e o processo
de GPU aborta, derrubando o aplicativo na inicialização.

Detectar essa topologia permite aplicar apenas a flag mínima
``--disable-gpu-compositing`` quando (e somente quando) ela é necessária,
preservando a aceleração completa para a maioria (máquinas com uma única GPU).

Usa apenas leituras de sysfs (ABI estável do Linux); funciona em X11 e Wayland,
sem dependências novas e sem privilégios de root.
"""
from __future__ import annotations

import glob
import os


def _pci_slot(drm_name: str) -> str | None:
    """Slot PCI (ex.: '0000:03:00.0') de um nó DRM ('card1' ou 'renderD128')."""
    try:
        return os.path.basename(
            os.path.realpath(os.path.join("/sys/class/drm", drm_name, "device"))
        )
    except OSError:
        return None


def _slots_driving_a_connected_display() -> set[str]:
    """Slots PCI cujas GPUs possuem ao menos uma saída (connector) conectada."""
    slots: set[str] = set()
    for status_path in glob.glob("/sys/class/drm/card*-*/status"):
        try:
            with open(status_path, "r") as fh:
                if fh.read().strip() != "connected":
                    continue
        except OSError:
            continue
        # Ex.: '/sys/class/drm/card1-HDMI-A-2/status' -> 'card1'
        connector = os.path.basename(os.path.dirname(status_path))  # 'card1-HDMI-A-2'
        card = connector.split("-", 1)[0]
        slot = _pci_slot(card)
        if slot:
            slots.add(slot)
    return slots


def has_headless_secondary_gpu() -> bool:
    """Retorna ``True`` quando existe um render node cuja GPU não controla
    nenhuma tela conectada enquanto outra GPU controla a tela — exatamente a
    topologia que dispara o crash cross-GPU ``gbm_bo_import`` / ``EGL_BAD_MATCH``
    no processo de GPU do Chromium.

    Falha em segurança (retorna ``False``) em qualquer erro de leitura de sysfs,
    em máquinas com uma única GPU e quando não há informação de conector, de modo
    que máquinas single-GPU (a maioria dos usuários) nunca são afetadas.
    """
    render_nodes = glob.glob("/dev/dri/renderD*")
    if len(render_nodes) <= 1:
        return False  # GPU única: mantém aceleração completa

    render_slots = {
        slot
        for node in render_nodes
        if (slot := _pci_slot(os.path.basename(node)))
    }
    if len(render_slots) <= 1:
        return False  # nós redundantes da mesma GPU

    display_slots = _slots_driving_a_connected_display()
    if not display_slots:
        return False  # sem informação de conector -> não interferir

    # Alguma GPU com render node não controla nenhuma tela conectada?
    return any(slot not in display_slots for slot in render_slots)
