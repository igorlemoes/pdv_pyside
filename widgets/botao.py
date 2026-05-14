"""
Botão personalizado com suporte a atalho de teclado.
Herda de QPushButton e exibe o atalho no texto.
"""
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QShortcut, QKeySequence


class Botao(QPushButton):
    def __init__(self, texto, atalho=None, parent=None):
        self._atalho = atalho
        texto_exibicao = f"<{atalho}>  -  {texto}" if atalho else texto
        super().__init__(texto_exibicao, parent)
        if atalho:
            self.setShortcut(QKeySequence(atalho))

    def atalho_key(self):
        return self._atalho


if __name__ == "__main__":
    import subprocess, sys, os
    subprocess.run([
        sys.executable,
        os.path.join(os.path.dirname(__file__), "..", "main.py")
    ])
