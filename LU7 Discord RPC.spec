# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['lu7discordrpc.py'],
    pathex=[],
    binaries=[],
    datas=[('logo.icns', '.')],
    hiddenimports=['PyQt5'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='LU7 Discord RPC',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.icns'],
)
app = BUNDLE(
    exe,
    name='LU7 Discord RPC.app',
    icon='logo.icns',
    bundle_identifier=None,
)
