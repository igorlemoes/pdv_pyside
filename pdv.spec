# -*- mode: python ; coding: utf-8 -*-
"""
Spec do PyInstaller para o PDV Minimercado.
Gera .app funcional no macOS e .exe no Windows.

Uso:
    pyinstaller pdv.spec
"""
import os
import PySide6

block_cipher = None

# Localiza a pasta de plugins do Qt
# No macOS pode estar em PySide6/plugins ou PySide6/Qt/plugins
pyside_dir = os.path.dirname(PySide6.__file__)
possiveis_plugins = [
    os.path.join(pyside_dir, "plugins"),
    os.path.join(pyside_dir, "Qt", "plugins"),
    os.path.join(pyside_dir, "Qt", "lib"),
]
plugin_src = None
for p in possiveis_plugins:
    if os.path.isdir(p):
        plugin_src = p
        break

plugin_binaries = []
if plugin_src:
    for root, dirs, files in os.walk(plugin_src):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(root, plugin_src)
            dst = os.path.join("PySide6", "plugins", rel)
            plugin_binaries.append((full, dst))

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=plugin_binaries,
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
    target_arch="universal2",
    bundle_identifier="com.pdv.minimercado",
    info_plist={
        "CFBundleIdentifier": "com.pdv.minimercado",
        "CFBundleName": "PDV Minimercado",
        "CFBundleShortVersionString": "1.0.0",
        "NSHighResolutionCapable": True,
        "NSSupportsAutomaticGraphicsSwitching": True,
        "NSPrincipalClass": "NSApplication",
        "NSRequiresAquaSystemAppearance": False,
        "QT_MAC_WANTS_LAYER": "1",
    },
)
