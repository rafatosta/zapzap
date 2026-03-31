# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['zapzap\\__main__.py'],
    pathex=[],
    binaries=[],
    datas=[('zapzap/po', 'zapzap/po'), ('zapzap/ui', 'zapzap/ui'), ('zapzap/resources', 'zapzap/resources'), ('zapzap/webengine/webrtc_shield.js', 'zapzap/webengine')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ZapZap',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ZapZap',
)
