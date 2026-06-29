import sys

from tools.flatpak_runner import FlatpakRunner

def run(args):
    """Usage: python run.py [args...]"""

    runner = FlatpakRunner(sys.argv[1:])
    runner.run()


def main():
    """Main entry point for the script."""

    args = sys.argv[1:]

    methods = {}

    selected_method = run

    # Procura argumentos especiais independentemente da ordem
    for key, method in methods.items():
        if key in args:
            selected_method = method
            args.remove(key)
            break

    selected_method(args)


if __name__ == "__main__":
    main()
