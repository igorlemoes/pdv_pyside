"""
Setup para gerar executável com cx_Freeze.
Funciona no Windows e macOS.

Uso:
    # Windows
    uv run python setup.py build

    # macOS (.app)
    uv run python setup.py bdist_mac --icon=None
"""
import sys
import os
from cx_Freeze import setup, Executable

# Descobre onde o PySide6 está instalado
import PySide6
pyside_dir = os.path.dirname(PySide6.__file__)

# Inclui a pasta de plugins do Qt (plataforma, estilos, etc.)
# Essencial para o app funcionar em qualquer máquina sem Qt instalado
pyside_plugins = os.path.join(pyside_dir, "plugins")

# Mapeia os plugins para dentro da pasta PySide6/plugins no bundle
def coletar_plugins():
    recursos = []
    if not os.path.isdir(pyside_plugins):
        return recursos
    for root, dirs, files in os.walk(pyside_plugins):
        for f in files:
            src = os.path.join(root, f)
            rel = os.path.relpath(root, os.path.dirname(pyside_plugins))
            dst = os.path.join("PySide6", rel, f)
            recursos.append((src, dst))
    return recursos

build_exe_options = {
    "includes": [
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
    ],
    "include_files": coletar_plugins(),
    "packages": ["PySide6"],
    "excludes": [],
    "optimize": 2,
}

bdist_mac_options = {
    "bundle_name": "PDV",
    "iconfile": None,
    "custom_info_plist": {
        "NSHighResolutionCapable": True,
        "NSRequiresAquaSystemAppearance": False,
    },
    "codesign_identity": "-",
}

executavel = Executable(
    script="main.py",
    base="gui" if sys.platform == "win32" else None,
    target_name="PDV",
)

setup(
    name="PDV Minimercado",
    version="1.0.0",
    description="Sistema PDV para Minimercado",
    options={
        "build_exe": build_exe_options,
        "bdist_mac": bdist_mac_options,
    },
    executables=[executavel],
)
