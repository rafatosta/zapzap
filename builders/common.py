from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


UI_FILES = [
    ("zapzap/ui/ui_mainwindow.ui", "zapzap/views/ui_mainwindow.py"),
    ("zapzap/ui/ui_page_general.ui", "zapzap/views/ui_page_general.py"),
    ("zapzap/ui/ui_page_network.ui", "zapzap/views/ui_page_network.py"),
]


ADDITIONAL_DATA = [
    ("zapzap/po", "zapzap/po"),
    ("zapzap/ui", "zapzap/ui"),
    ("zapzap/resources", "zapzap/resources"),
    (
        "zapzap/webengine/webrtc_shield.js",
        "zapzap/webengine",
    ),
    (
        "zapzap/webengine/theme_controller.js",
        "zapzap/webengine",
    ),
]


def create_build_info():
    build_channel = "Local"
    build_provider = "Unknown"
    build_repository = ""

    import os

    build_channel = os.getenv(
        "BUILD_CHANNEL",
        build_channel,
    )

    build_provider = os.getenv(
        "BUILD_PROVIDER",
        build_provider,
    )

    build_repository = os.getenv(
        "BUILD_REPOSITORY",
        build_repository,
    )

    build_info = ROOT_DIR / "zapzap" / "BuildInfo.py"

    build_info.write_text(
        (
            f'BUILD_CHANNEL = "{build_channel}"\n'
            f'BUILD_PROVIDER = "{build_provider}"\n'
            f'BUILD_REPOSITORY = "{build_repository}"\n'
        ),
        encoding="utf-8",
    )

    print(f"BuildInfo criado: {build_info}")