# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['image_gen_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['PySide6.QtSvg', 'PIL._tkinter_finder', 'skimage'],  # Add if needed
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyd = PYZ(a.pure)
exe = EXE(
    pyd,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ImageGen',
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
    icon='icon.ico'  # Optional
)
