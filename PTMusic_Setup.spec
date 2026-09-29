# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['PTMusic_Installer.py'],
    pathex=[],
    binaries=[],
    datas=[('dist\\26.9.x\\26.9.3\\PTMusic.exe', '.'), ('PTMusic.png', '.'), ('PTMusic.ico', '.'), ('I:\\pt apps\\Python\\PTMusic\\examplemusic', 'examplemusic')],
    hiddenimports=['PIL'],
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
    a.binaries,
    a.datas,
    [],
    name='PTMusic_Setup',
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
    icon=['PTMusic.ico'],
)
