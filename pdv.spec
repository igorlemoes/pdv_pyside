# -*- mode: python ; coding: utf-8 -*-
"""
Spec do PyInstaller para o PDV Minimercado.
Modo onedir — funciona no macOS e Windows.

macOS: use build_mac.sh (faz re-assinatura necessária)
Windows: pyinstaller pdv.spec
"""
import sys

block_cipher = None
IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtSvg",
        "PySide6.QtNetwork",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PDV",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity="-" if IS_MAC else None,
    entitlements_file=None,
    # Ícone: icon="icon.ico" no Windows, icon="icon.icns" no macOS
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PDV",
)

if IS_MAC:
    app = BUNDLE(
        coll,
        name="PDV.app",
        icon=None,
        bundle_identifier="com.pdv.minimercado",
        info_plist={
            "CFBundleIdentifier": "com.pdv.minimercado",
            "CFBundleName": "PDV Minimercado",
            "CFBundleShortVersionString": "1.0.0",
            "NSHighResolutionCapable": True,
            "NSSupportsAutomaticGraphicsSwitching": True,
            "NSPrincipalClass": "NSApplication",
            "NSRequiresAquaSystemAppearance": False,
        },
    )
