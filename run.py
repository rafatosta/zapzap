import sys

from tools.flatpak_runner import FlatpakRunner

def main():
    """Build and launch the checkout in Flatpak with the supplied arguments."""
    FlatpakRunner(sys.argv[1:]).run()


if __name__ == "__main__":
    main()
