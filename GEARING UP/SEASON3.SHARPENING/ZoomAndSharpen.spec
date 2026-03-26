# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for ZoomAndSharpen (SEASON3.SHARPENING)
# Build:  pyinstaller --clean ZoomAndSharpen.spec
# Output: dist/ZoomAndSharpen/ZoomAndSharpen.exe

import os
import cv2 as _cv2

_cv2_dir = os.path.dirname(_cv2.__file__)
_cv2_data = os.path.join(_cv2_dir, 'data')

block_cipher = None

a = Analysis(
    ['3.zoom_and_sharpen.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # OpenCV cascade / data files (e.g. haarcascades — included for completeness)
        (_cv2_data, 'cv2/data'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'PIL._tkinter_finder',
        'cv2',
        'numpy',
        'logging',
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

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ZoomAndSharpen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # No black console window — pure GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ZoomAndSharpen',
)
