"""
Tela de gerenciamento de estoque do PDV.
Exibe todos os produtos cadastrados e permite:
- Cadastrar novo produto
- Editar produto existente
- Excluir produto
"""
from datetime import datetime
from decimal import Decimal, InvalidOperation

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QTableView, QHeaderView, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QAbstractTableModel, Signal, QModelIndex
from PySide6.QtGui import QColor, QBrush, QFont, QShortcut, QKeySequence

from models import Produto
from utils import fmt_br, parse_br, remover_acentos
from widgets.botao import Botao


class ProdutoTableModel(QAbstractTableModel):
    colunas = ["Código", "Nome", "Tipo", "Custo", "Venda", "Estoque", "Mínimo"]

    def __init__(self):
        super().__init__()
        self.produtos = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.produtos)

    def columnCount(self, parent=QModelIndex()):
        return len(self.colunas)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        p = self.produtos[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0:
                return str(p.codigo)
            elif col == 1:
                return p.nome
            elif col == 2:
                return p.tipo
            elif col == 3:
                return fmt_br(p.valor_custo)
            elif col == 4:
                return fmt_br(p.valor_venda)
            elif col == 5:
                return f"{float(p.estoque_total):.3f}".replace(".", ",")
            elif col == 6:
                return f"{float(p.estoque_minimo):.3f}".replace(".", ",")
        if role == Qt.ForegroundRole:
            if p.estoque_total <= p.estoque_minimo:
                return QBrush(QColor("#FF6B6B"))
        if role == Qt.TextAlignmentRole:
            if col >= 3:
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.colunas[section]
        return None

    def carregar(self, termo=""):
        self.beginResetModel()
        termo_clean = remover_acentos(termo.lower().strip()) if termo else ""
        if not termo_clean:
            self.produtos = list(Produto.select().order_by(Produto.codigo))
        else:
            try:
                cod = int(termo)
                self.produtos = [
                    p for p in Produto.select().order_by(Produto.codigo)
                    if p.codigo == cod or termo_clean in remover_acentos(p.nome.lower())
                ]
            except ValueError:
                self.produtos = [
                    p for p in Produto.select().order_by(Produto.codigo)
                    if termo_clean in remover_acentos(p.nome.lower())
                ]
        self.endResetModel()

    def produto_at(self, row):
        if 0 <= row < len(self.produtos):
            return self.produtos[row]
        return None


class TelaEstoque(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._produto_editando = None
        self._layout_principal = QVBoxLayout(self)
        self._layout_principal.setContentsMargins(0, 0, 0, 0)

        # Container interno com padding
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(15, 15, 15, 15)

        header = QHBoxLayout()
        titulo = QLabel("Estoque")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        header.addWidget(titulo)
        header.addStretch()

        self.btn_novo = Botao("Novo", "F2", self)
        self.btn_novo.clicked.connect(self.abrir_form_novo)
        header.addWidget(self.btn_novo)

        self.btn_editar = Botao("Editar", "F3", self)
        self.btn_editar.clicked.connect(self.editar_selecionado)
        header.addWidget(self.btn_editar)

        self.btn_excluir = Botao("Excluir", "F4", self)
        self.btn_excluir.clicked.connect(self.excluir_selecionado)
        header.addWidget(self.btn_excluir)

        self.btn_atualizar = Botao("Atualizar", "F5", self)
        self.btn_atualizar.clicked.connect(self.carregar_produtos)
        header.addWidget(self.btn_atualizar)

        container_layout.addLayout(header)

        self.pesquisa = QLineEdit()
        self.pesquisa.setPlaceholderText("Pesquisar por código ou nome...")
        self.pesquisa.textChanged.connect(self.carregar_produtos)
        container_layout.addWidget(self.pesquisa)

        self.model = ProdutoTableModel()
        self.tabela = QTableView()
        self.tabela.setModel(self.model)
        self.tabela.setSelectionBehavior(QTableView.SelectRows)
        self.tabela.setSelectionMode(QTableView.SingleSelection)
        self.tabela.verticalHeader().hide()
        self.tabela.setAlternatingRowColors(True)
        header_view = self.tabela.horizontalHeader()
        header_view.setStretchLastSection(True)
        header_view.setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.setStyleSheet("""
            QTableView { background-color: #2B2B2B; color: white; gridline-color: #444; border: none; }
            QTableView::item:selected { background-color: #2B5F8A; color: white; }
            QTableView::item:alternate { background-color: #3B3B3B; }
            QHeaderView::section { background-color: #1E3A5F; color: white; font-weight: bold; padding: 4px; border: none; }
        """)

        container_layout.addWidget(self.tabela)
        self._layout_principal.addWidget(container)

        self.form_widget = QWidget()
        self.form_layout = QVBoxLayout(self.form_widget)
        self.form_widget.hide()
        self._criar_formulario()
        self._layout_principal.addWidget(self.form_widget)

        self.carregar_produtos()

    def _criar_formulario(self):
        titulo = QLabel("Produto")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        self.form_layout.addWidget(titulo)

        grid = QGridLayout()
        campos = [
            ("Código:", "codigo", 0, 0),
            ("Nome:", "nome", 0, 1),
            ("Tipo:", "tipo", 0, 2),
            ("Valor Custo (R$):", "valor_custo", 1, 0),
            ("Lucro (%):", "lucro_pct", 1, 1),
            ("Valor Sugerido:", "valor_sugerido", 1, 2),
            ("Valor Venda (R$):", "valor_venda", 2, 0),
            ("Estoque Total:", "estoque_total", 2, 1),
            ("Estoque Mínimo:", "estoque_minimo", 2, 2),
            ("Validade (AAAA-MM-DD):", "validade", 3, 0),
        ]

        self._form_widgets = {}
        for label, attr, row, col in campos:
            f = QWidget()
            f_layout = QVBoxLayout(f)
            f_layout.setContentsMargins(5, 4, 5, 4)
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #ccc; font-size: 12px;")
            f_layout.addWidget(lbl)

            if attr == "tipo":
                widget = QComboBox()
                widget.addItems(["Unidade", "Kg", "Metros", "M2", "Caixas"])
            elif attr == "valor_sugerido":
                widget = QLineEdit()
                widget.setReadOnly(True)
                widget.setStyleSheet("background-color: #444; color: #aaa;")
            else:
                widget = QLineEdit()

            widget.setStyleSheet(widget.styleSheet() + " padding: 4px;")
            f_layout.addWidget(widget)
            grid.addWidget(f, row, col)
            self._form_widgets[attr] = widget

        self.form_layout.addLayout(grid)

        botoes = QHBoxLayout()
        self.btn_salvar = Botao("Salvar", "F1", self)
        self.btn_salvar.clicked.connect(self.salvar_produto)
        botoes.addWidget(self.btn_salvar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.fechar_form)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self.fechar_form)
        botoes.addWidget(btn_cancelar)
        self.form_layout.addLayout(botoes)

        if "valor_custo" in self._form_widgets:
            self._form_widgets["valor_custo"].textChanged.connect(self._calcular_sugerido)
        if "lucro_pct" in self._form_widgets:
            self._form_widgets["lucro_pct"].textChanged.connect(self._calcular_sugerido)

    def _calcular_sugerido(self):
        try:
            custo_text = self._form_widgets["valor_custo"].text().strip()
            lucro_text = self._form_widgets["lucro_pct"].text().strip()
            if custo_text and lucro_text:
                custo = parse_br(custo_text)
                lucro = parse_br(lucro_text)
                sugerido = custo * (1 + lucro / 100)
                texto_br = f"{float(sugerido):.2f}".replace(".", ",")
                self._form_widgets["valor_sugerido"].setText(texto_br)
        except (InvalidOperation, ValueError):
            pass

    def abrir_form_novo(self):
        self._produto_editando = None
        self._limpar_form()
        self._mostrar_form()

    def editar_selecionado(self):
        idx = self.tabela.currentIndex()
        produto = self.model.produto_at(idx.row())
        if not produto:
            return
        self._produto_editando = produto
        self._preencher_form(produto)
        self._mostrar_form()

    def _mostrar_form(self):
        self.pesquisa.parent().hide() if self.pesquisa.parent() else None
        self.tabela.parent().hide()
        self.form_widget.show()

    def fechar_form(self):
        self.form_widget.hide()
        self.tabela.parent().show()
        self._produto_editando = None

    def _limpar_form(self):
        for attr, widget in self._form_widgets.items():
            if attr == "tipo":
                widget.setCurrentIndex(0)
            elif attr == "valor_sugerido":
                widget.setText("")
            else:
                widget.setText("")

    def _preencher_form(self, produto):
        for attr, widget in self._form_widgets.items():
            valor = getattr(produto, attr, "")
            if attr == "tipo":
                idx = widget.findText(valor)
                if idx >= 0:
                    widget.setCurrentIndex(idx)
            elif attr == "valor_sugerido":
                widget.setText(f"{float(valor):.2f}".replace(".", ","))
            elif attr == "validade":
                if valor:
                    widget.setText(valor.strftime("%Y-%m-%d"))
            elif attr in ("estoque_total", "estoque_minimo"):
                widget.setText(f"{float(valor):.3f}".replace(".", ","))
            else:
                widget.setText(str(valor).replace(".", ","))

    def salvar_produto(self):
        try:
            dados = {}
            for attr, widget in self._form_widgets.items():
                if attr == "tipo":
                    dados[attr] = widget.currentText()
                elif attr == "valor_sugerido":
                    continue
                elif attr == "validade":
                    texto = widget.text().strip()
                    dados[attr] = (
                        datetime.strptime(texto, "%Y-%m-%d").date()
                        if texto else None
                    )
                elif attr == "nome":
                    texto = widget.text().strip()
                    if not texto:
                        raise ValueError("Nome não pode ficar vazio")
                    dados[attr] = texto
                else:
                    texto = widget.text().strip()
                    if not texto:
                        raise ValueError(f"Campo {attr} está vazio")
                    if attr == "codigo":
                        dados[attr] = int(texto)
                    else:
                        dados[attr] = parse_br(texto)

            texto_sugerido = self._form_widgets["valor_sugerido"].text().strip()
            dados["valor_sugerido"] = parse_br(texto_sugerido) if texto_sugerido else Decimal("0")

            if self._produto_editando:
                for chave, valor in dados.items():
                    setattr(self._produto_editando, chave, valor)
                self._produto_editando.save()
            else:
                Produto.create(**dados)

            self.fechar_form()
            self.carregar_produtos()

        except (InvalidOperation, ValueError):
            pass
        except Exception:
            pass

    def excluir_selecionado(self):
        idx = self.tabela.currentIndex()
        produto = self.model.produto_at(idx.row())
        if not produto:
            return

        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Excluir {produto.nome} (cód. {produto.codigo})?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            produto.delete_instance()
            self.carregar_produtos()

    def carregar_produtos(self):
        termo = self.pesquisa.text()
        self.model.carregar(termo)
        self.tabela.resizeColumnsToContents()


if __name__ == "__main__":
    import subprocess, sys, os
    subprocess.run([
        sys.executable,
        os.path.join(os.path.dirname(__file__), "..", "main.py")
    ])
