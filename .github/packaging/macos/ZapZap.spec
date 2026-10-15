"""Repository-relative Mac bundle; native bridge is built by build-native.sh."""
import ast
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

source = Path(SPECPATH).resolve().parents[2]
module = ast.parse((source / "zapzap" / "__init__.py").read_text(encoding="utf-8"))
version = next(
    ast.literal_eval(node.value)
    for node in module.body
    if isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets)
)
bridge = source / "build" / "native" / "libZapZapNotifications.dylib"
if not bridge.is_file():
    raise SystemExit("Run .github/packaging/macos/build-native.sh before PyInstaller")

a = Analysis(
    [str(source / "zapzap" / "__main__.py")],
    pathex=[str(source)],
    binaries=[(str(bridge), "zapzap/features/notifications")],
    datas=[
        (str(source / "zapzap" / "po"), "zapzap/po"),
        (str(source / "zapzap" / "assets"), "zapzap/assets"),
        (str(source / "zapzap" / "features" / "browser" / "web" / "scripts"),
         "zapzap/features/browser/web/scripts"),
    ],
    hiddenimports=collect_submodules("zapzap.features.settings.pages")
        + ["zapzap.features.notifications.macos_native_notifications"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True,
    name="ZapZap", console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name="ZapZap")
app = BUNDLE(
    coll, name="ZapZap.app", bundle_identifier="ZapZap",
    info_plist={
        "CFBundleShortVersionString": version,
        "CFBundleVersion": version,
        "NSHighResolutionCapable": True,
        "NSUserActivityTypes": ["INSendMessageIntent"],
    },
)
