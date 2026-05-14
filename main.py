"""
Sistema PDV para Minimercado — Ponto de Venda e Controle de Estoque.
Arquivo principal de inicialização.
"""
import sys
import os

# Força o empacotamento dos plugins Qt no PyInstaller (necessário para macOS .app)
import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtWidgets

# Garante que os plugins Qt sejam encontrados dentro do bundle do PyInstaller
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    plugin_path = os.path.join(sys._MEIPASS, 'PySide6', 'plugins')
    if os.path.isdir(plugin_path):
        os.environ['QT_QPA_PLUGIN_PATH'] = plugin_path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout,
    QPushButton, QStackedWidget, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence

from database import conectar
from screens.pdv import TelaPDV
from screens.estoque import TelaEstoque


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDV Minimercado")
        self.resize(1200, 750)

        conectar()

        central = QWidget()
        self.setCentralWidget(central)
        layout_principal = QVBoxLayout(central)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        nav = QWidget()
        nav.setStyleSheet("background-color: #1a1a2e;")
        nav.setFixedHeight(50)
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(10, 5, 10, 5)

        logo = QLabel("PDV Minimercado")
        logo.setStyleSheet("color: white; font-weight: bold; font-size: 16px; padding: 0 15px;")
        nav_layout.addWidget(logo)

        self.nav_pdv = QPushButton("PDV")
        self.nav_pdv.setStyleSheet(self._estilo_nav_ativa())
        self.nav_pdv.clicked.connect(lambda: self.mostrar_tela("pdv"))
        nav_layout.addWidget(self.nav_pdv)

        self.nav_estoque = QPushButton("Estoque")
        self.nav_estoque.setStyleSheet(self._estilo_nav_inativa())
        self.nav_estoque.clicked.connect(lambda: self.mostrar_tela("estoque"))
        nav_layout.addWidget(self.nav_estoque)

        nav_layout.addStretch()
        layout_principal.addWidget(nav)

        self.stack = QStackedWidget()
        self.tela_pdv = TelaPDV()
        self.tela_estoque = TelaEstoque()
        self.stack.addWidget(self.tela_pdv)
        self.stack.addWidget(self.tela_estoque)
        layout_principal.addWidget(self.stack)

        QShortcut(QKeySequence("F6"), self).activated.connect(lambda: self.mostrar_tela("pdv"))

        self.mostrar_tela("pdv")

    def _estilo_nav_ativa(self):
        return """
            QPushButton {
                background-color: #2B5F8A; color: white; border: none;
                padding: 6px 20px; font-weight: bold; font-size: 13px;
            }
        """

    def _estilo_nav_inativa(self):
        return """
            QPushButton {
                background-color: transparent; color: white; border: none;
                padding: 6px 20px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #2B5F8A; }
        """

    def mostrar_tela(self, nome):
        if nome == "pdv":
            self.stack.setCurrentWidget(self.tela_pdv)
            self.nav_pdv.setStyleSheet(self._estilo_nav_ativa())
            self.nav_estoque.setStyleSheet(self._estilo_nav_inativa())
        else:
            self.stack.setCurrentWidget(self.tela_estoque)
            self.nav_pdv.setStyleSheet(self._estilo_nav_inativa())
            self.nav_estoque.setStyleSheet(self._estilo_nav_ativa())


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet("""
        QWidget {
            background-color: #2B2B2B;
            color: white;
            font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica Neue, Arial, sans-serif;
        }
        QLineEdit {
            background-color: #3B3B3B;
            color: white;
            border: 1px solid #555;
            padding: 6px;
            border-radius: 4px;
        }
        QLineEdit:focus {
            border: 2px solid #2B5F8A;
        }
        QPushButton {
            background-color: #2B5F8A;
            color: white;
            border: none;
            padding: 6px 16px;
            border-radius: 4px;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #1A3F5C;
        }
        QComboBox {
            background-color: #3B3B3B;
            color: white;
            border: 1px solid #555;
            padding: 4px;
            border-radius: 4px;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox QAbstractItemView {
            background-color: #3B3B3B;
            color: white;
            selection-background-color: #2B5F8A;
        }
        QScrollBar:vertical {
            background: #2B2B2B;
            width: 10px;
            border: none;
        }
        QScrollBar::handle:vertical {
            background: #555;
            border-radius: 5px;
            min-height: 20px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            background: #2B2B2B;
            height: 10px;
            border: none;
        }
        QScrollBar::handle:horizontal {
            background: #555;
            border-radius: 5px;
            min-width: 20px;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QTableView {
            background-color: #2B2B2B;
            color: white;
            gridline-color: #444;
            border: none;
            selection-background-color: #2B5F8A;
            selection-color: white;
            alternate-background-color: #3B3B3B;
        }
        QTableView::item:selected {
            background-color: #2B5F8A;
            color: white;
        }
        QHeaderView::section {
            background-color: #1E3A5F;
            color: white;
            font-weight: bold;
            padding: 6px;
            border: none;
        }
        QMessageBox {
            background-color: #2B2B2B;
            color: white;
        }
        QMessageBox QPushButton {
            min-width: 80px;
        }
    """)
    window = App()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
