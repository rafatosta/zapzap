#!/usr/bin/env bash
# ── Lanzador ÚNICO de ZapZap ─────────────────────────────────────────────────
# Fuente única de verdad = este repo (/mnt/sda1/repos/zapzap). El menú (.desktop),
# el MCP (fallback) y cualquier script arrancan por acá, así el código que corre
# es SIEMPRE el del repo, con el Control D-Bus y los métodos no-focus por cuenta.
# El AppImage congelado quedó retirado.
#
# Setea el entorno gráfico defensivamente: cuando se lanza desde un shell sin
# sesión (MCP, ssh, cron) faltan DISPLAY/WAYLAND_DISPLAY y la GUI Qt no puede
# crear ventana y sale en silencio — por eso se exportan con defaults.
export DISPLAY="${DISPLAY:-:0}"
export XDG_SESSION_TYPE="${XDG_SESSION_TYPE:-wayland}"
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"

REPO="/mnt/sda1/repos/zapzap"
cd "$REPO" || exit 1
# Instancia única: si ya corre, el propio ZapZap reenvía los args (abrir chat,
# etc.) por su canal single-instance en vez de abrir otra ventana.
exec env PYTHONPATH="$REPO" python3 -m zapzap "$@"
