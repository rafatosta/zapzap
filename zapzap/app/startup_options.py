"""Command-line option handling for ZapZap startup."""

import argparse

from zapzap.core.config.settings_manager import SettingsManager


def parse_startup_options():
    parser = argparse.ArgumentParser(
        description="Gerenciar configurações do zapzap")
    parser.add_argument("--setSettings", nargs=2, metavar=("chave",
                        "valor"), help="Define uma configuração específica")
    parser.add_argument("--wayland", action="store_true",
                        help="Força o uso do Wayland (QT_QPA_PLATFORM=wayland)")
    args, unknown = parser.parse_known_args()
    return args, unknown


def apply_startup_options(args):
    if args.setSettings:
        chave, valor = args.setSettings
        try:
            print(f"Configurando {chave} para {valor}")
            SettingsManager.set(chave, valor)
        except ValueError:
            print(f"Erro: O valor '{valor}' não é um número inteiro válido.")
