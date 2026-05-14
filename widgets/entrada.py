"""
Campo de entrada personalizado com suporte a atalho de teclado para foco.
Herda de QLineEdit e permite focar via tecla de atalho.
"""
from PySide6.QtWidgets import QLineEdit
from PySide6.QtGui import QShortcut, QKeySequence


class Entrada(QLineEdit):
    def __init__(self, atalho=None, parent=None):
        super().__init__(parent)
        self._atalho = atalho
        if atalho and parent:
            self._shortcut = QShortcut(QKeySequence(atalho), parent)
            self._shortcut.activated.connect(self._focar)

    def _focar(self):
        self.setFocus()

    def atalho_key(self):
        return self._atalho


if __name__ == "__main__":
    import subprocess, sys, os
    subprocess.run([
        sys.executable,
        os.path.join(os.path.dirname(__file__), "..", "main.py")
    ])
