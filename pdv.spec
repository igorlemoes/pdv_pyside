# -*- mode: python ; coding: utf-8 -*-
"""
Spec do PyInstaller para o PDV Minimercado.
Gera .app funcional no macOS e .exe no Windows.

Uso:
    pyinstaller pdv.spec
"""
import os
import PySide6
from PySide6.QtCore import QT_VERSION_STR

block_cipher = None

# Mapeia todos os plugins Qt como binários para garantir
# que o plugin de plataforma (cocoa no mac, windows no win) seja incluído
plugin_src = os.path.join(os.path.dirname(PySide6.__file__), "plugins")
plugin_binaries = []
for root, dirs, files in os.walk(plugin_src):
    for f in files:
        full = os.path.join(root, f)
        rel = os.path.relpath(root, plugin_src)
        dst = os.path.join("PySide6", "plugins", rel, f)
        plugin_binaries.append((dst, full, "BINARY"))

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=plugin_binaries,
    datas=[
        (plugin_src, "PySide6/plugins"),
    ],
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
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="PDV",
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
)

app = BUNDLE(
    exe,
    name="PDV.app",
    icon=None,
    bundle_identifier="com.pdv.minimercado",
    info_plist={
        "NSHighResolutionCapable": True,
        "NSSupportsAutomaticGraphicsSwitching": True,
        "QT_MAC_WANTS_LAYER": "1",
    },
)
