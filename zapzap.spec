# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['zapzap/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('zapzap', 'zapzap'),
    ],
    hiddenimports=[
        # Qt WebEngine (CRÍTICO)
        'PyQt6.QtWebEngineCore',
        'PyQt6.QtWebEngineWidgets',

        # Qt internos frequentemente omitidos
        'PyQt6.QtPrintSupport',
        'PyQt6.QtNetwork',
        'PyQt6.QtDBus',

        # DBus
        'dbus',
        'dbus.mainloop.pyqt6',

        # Gettext
        'gettext',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='zapzap',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='zapzap',
)