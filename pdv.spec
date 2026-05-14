# -*- mode: python ; coding: utf-8 -*-
"""
Spec do PyInstaller para o PDV Minimercado.
Modo onedir — estrutura correta para .app no macOS.

Uso:
    pyinstaller pdv.spec
"""
import os
import PySide6

block_cipher = None

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
    target_arch="arm64",
    codesign_identity="-",
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
    name="PDV",
)

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
