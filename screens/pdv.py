"""
Tela principal do PDV (Ponto de Venda) do minimercado.
Gerencia a busca de produtos, carrinho de compras e finalização da venda.
"""
import re
from decimal import Decimal

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QFrame, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QShortcut, QKeySequence, QColor

from models import Produto
from utils import fmt_br, remover_acentos
from widgets.botao import Botao


class ItemCarrinho:
    def __init__(self, produto, quantidade, preco_unitario):
        self.produto = produto
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario


class TelaPDV(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.carrinho = []
        self._ultimo_item = None
        self._item_selecionado_idx = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        header = QHBoxLayout()
        titulo = QLabel("PDV")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        header.addWidget(titulo)
        header.addStretch()
        dica = QLabel("Dica: digite 3*arroz para adicionar 3 unidades")
        dica.setStyleSheet("font-size: 11px; color: gray;")
        header.addWidget(dica)
        layout.addLayout(header)

        busca_widget = QWidget()
        busca_layout = QVBoxLayout(busca_widget)
        busca_layout.setContentsMargins(0, 0, 0, 0)
        self.busca = QLineEdit()
        self.busca.setPlaceholderText("Digite o código ou nome do produto...")
        font_busca = QFont()
        font_busca.setPointSize(16)
        self.busca.setFont(font_busca)
        self.busca.setStyleSheet("padding: 8px;")
        self.busca.textChanged.connect(self._ao_digitar)
        self.busca.returnPressed.connect(self._ao_enter)
        busca_layout.addWidget(self.busca)

        self.dropdown = QListWidget()
        self.dropdown.setStyleSheet("""
            QListWidget {
                background-color: #3B3B3B; color: white; border: 1px solid #555;
                font-size: 13px;
            }
            QListWidget::item:selected { background-color: #2B5F8A; }
        """)
        self.dropdown.setMaximumHeight(200)
        self.dropdown.hide()
        self.dropdown.itemClicked.connect(self._dropdown_clicado)
        busca_layout.addWidget(self.dropdown)
        layout.addWidget(busca_widget)
        
        QShortcut(QKeySequence("F5"), self).activated.connect(self.busca.setFocus)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self._esconder_dropdown)

        area = QHBoxLayout()

        frame_carrinho = QWidget()
        carrinho_layout = QVBoxLayout(frame_carrinho)
        carrinho_layout.setContentsMargins(0, 0, 0, 0)
        lbl_carrinho = QLabel("Carrinho")
        lbl_carrinho.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        carrinho_layout.addWidget(lbl_carrinho)

        cabecalho_carrinho = QWidget()
        cabecalho_carrinho.setStyleSheet("background-color: #1E3A5F; padding: 4px;")
        cabecalho_carrinho.setFixedHeight(28)
        cab_h = QHBoxLayout(cabecalho_carrinho)
        cab_h.setContentsMargins(8, 2, 8, 2)
        for texto, larg in [("Qtd", 60), ("Item", 200), ("Total", 100)]:
            lbl = QLabel(texto)
            lbl.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")
            lbl.setFixedWidth(larg)
            cab_h.addWidget(lbl)
        cab_h.addStretch()
        carrinho_layout.addWidget(cabecalho_carrinho)

        self.scroll_itens = QScrollArea()
        self.scroll_itens.setWidgetResizable(True)
        self.scroll_itens.setStyleSheet("QScrollArea { border: none; }")
        self.itens_container = QWidget()
        self.itens_container.setStyleSheet("background-color: #2B2B2B;")
        self.itens_layout = QVBoxLayout(self.itens_container)
        self.itens_layout.setContentsMargins(0, 0, 0, 0)
        self.itens_layout.setSpacing(1)
        self.itens_layout.addStretch()
        self.scroll_itens.setWidget(self.itens_container)
        carrinho_layout.addWidget(self.scroll_itens)

        self.total_label = QLabel("Total: R$ 0,00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white; padding: 8px;")
        self.total_label.setAlignment(Qt.AlignRight)
        carrinho_layout.addWidget(self.total_label)

        area.addWidget(frame_carrinho, stretch=3)

        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("background-color: #333; padding: 10px;")
        side_layout = QVBoxLayout(self.sidebar)

        side_titulo = QLabel("Último Item")
        side_titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        side_layout.addWidget(side_titulo)

        self.side_qtd = QLabel("Quantidade: —")
        self.side_qtd.setStyleSheet("color: #ccc;")
        side_layout.addWidget(self.side_qtd)
        self.side_preco = QLabel("Preço Unitário: —")
        self.side_preco.setStyleSheet("color: #ccc;")
        side_layout.addWidget(self.side_preco)
        self.side_sub = QLabel("Subtotal: —")
        self.side_sub.setStyleSheet("color: #ccc;")
        side_layout.addWidget(self.side_sub)

        side_layout.addSpacing(15)
        btn_remover = QPushButton("Remover Selecionado")
        btn_remover.clicked.connect(self.remover_selecionado)
        side_layout.addWidget(btn_remover)
        side_layout.addStretch()

        area.addWidget(self.sidebar)
        layout.addLayout(area)

        self.btn_finalizar = Botao("Finalizar Venda", "F8", self)
        self.btn_finalizar.setStyleSheet("""
            QPushButton {
                background-color: #2B7A2B; color: white; font-weight: bold;
                font-size: 15px; padding: 10px; border: none;
            }
            QPushButton:hover { background-color: #1F5C1F; }
        """)
        self.btn_finalizar.clicked.connect(self.finalizar_venda)
        layout.addWidget(self.btn_finalizar)

    def _ao_digitar(self):
        texto = self.busca.text()
        if not texto:
            self._esconder_dropdown()
            return

        qtd, termo = self._parse_quantidade(texto)
        produtos = self._buscar_produtos(termo)

        if not produtos:
            self._esconder_dropdown()
            return

        if len(produtos) == 1:
            self._adicionar_ao_carrinho(produtos[0], qtd)
            return

        self.dropdown.clear()
        for p in produtos:
            item_texto = f"{p.codigo}  {p.nome}  ({p.tipo})  {fmt_br(p.valor_venda)}"
            li = QListWidgetItem(item_texto)
            li.setData(Qt.UserRole, p.id)
            self.dropdown.addItem(li)
        self.dropdown.show()

    def _dropdown_clicado(self, item):
        produto_id = item.data(Qt.UserRole)
        try:
            produto = Produto.get_by_id(produto_id)
        except Produto.DoesNotExist:
            return
        texto = self.busca.text()
        qtd, _ = self._parse_quantidade(texto)
        self._adicionar_ao_carrinho(produto, qtd)

    def _ao_enter(self):
        texto = self.busca.text().strip()
        if not texto:
            self._esconder_dropdown()
            return

        if self.dropdown.isVisible() and self.dropdown.count() > 0:
            item = self.dropdown.currentItem()
            if item:
                self._dropdown_clicado(item)
                return

        qtd, termo = self._parse_quantidade(texto)
        produtos = self._buscar_produtos(termo)
        if produtos:
            self._adicionar_ao_carrinho(produtos[0], qtd)
        else:
            self._esconder_dropdown()

    def _parse_quantidade(self, texto):
        texto = texto.strip()
        m = re.match(r"^(\d+(?:[.,]\d+)?)\s*\*\s*(.*)", texto)
        if m:
            qtd_str = m.group(1).replace(",", ".")
            return Decimal(qtd_str), m.group(2).strip()
        return Decimal(1), texto

    def _buscar_produtos(self, termo):
        if not termo:
            return []
        termo_clean = remover_acentos(termo.lower())
        resultados = []
        try:
            cod = int(termo)
            for p in Produto.select().order_by(Produto.nome):
                if p.codigo == cod or termo_clean in remover_acentos(p.nome.lower()):
                    resultados.append(p)
        except ValueError:
            for p in Produto.select().order_by(Produto.nome):
                if termo_clean in remover_acentos(p.nome.lower()):
                    resultados.append(p)
        return resultados

    def _esconder_dropdown(self):
        self.dropdown.clear()
        self.dropdown.hide()

    def _adicionar_ao_carrinho(self, produto, quantidade=Decimal(1)):
        qtd = quantidade
        preco = Decimal(str(produto.valor_venda))

        for item in self.carrinho:
            if item.produto.id == produto.id:
                item.quantidade += qtd
                self._ultimo_item = item
                self._atualizar_carrinho()
                self._limpar_busca()
                return

        item = ItemCarrinho(produto, qtd, preco)
        self.carrinho.append(item)
        self._ultimo_item = item
        self._atualizar_carrinho()
        self._limpar_busca()

    def _limpar_busca(self):
        self.busca.clear()
        self._esconder_dropdown()

    def _atualizar_carrinho(self):
        for i in reversed(range(self.itens_layout.count())):
            w = self.itens_layout.itemAt(i).widget()
            if w and w is not self.itens_layout.itemAt(self.itens_layout.count() - 1).widget():
                w.deleteLater()
        # Remove o stretch e reconstrói
        self.itens_layout.takeAt(self.itens_layout.count() - 1)

        total_geral = Decimal("0")
        for i, item in enumerate(self.carrinho):
            cor = "#3B3B3B" if i % 2 == 0 else "#484848"
            if self._item_selecionado_idx == i:
                cor = "#2B5F8A"

            linha = QWidget()
            linha.setStyleSheet(f"background-color: {cor};")
            linha.setFixedHeight(30)
            linha_layout = QHBoxLayout(linha)
            linha_layout.setContentsMargins(8, 2, 8, 2)
            linha_layout.setSpacing(0)

            qtd_str = f"{item.quantidade:.3f}".rstrip("0").rstrip(".").replace(".", ",")
            total_str = fmt_br(item.subtotal)

            for texto, larg in [(qtd_str, 60), (item.produto.nome, 200), (total_str, 100)]:
                lbl = QLabel(texto)
                lbl.setStyleSheet(f"color: white; font-size: 13px; background: transparent;")
                lbl.setFixedWidth(larg)
                linha_layout.addWidget(lbl)
            linha_layout.addStretch()

            linha.mousePressEvent = lambda e, idx=i: self._selecionar_item(idx)
            self.itens_layout.addWidget(linha)
            total_geral += item.subtotal

        self.itens_layout.addStretch()
        self.total_label.setText(f"Total: {fmt_br(total_geral)}")

        sel_idx = self._item_selecionado_idx
        if sel_idx is not None and sel_idx < len(self.carrinho):
            self._atualizar_sidebar(sel_idx)
        elif self._ultimo_item and self._ultimo_item in self.carrinho:
            idx = self.carrinho.index(self._ultimo_item)
            self._item_selecionado_idx = idx
            self._atualizar_sidebar(idx)

    def _atualizar_sidebar(self, idx):
        if idx is None or idx < 0 or idx >= len(self.carrinho):
            return
        item = self.carrinho[idx]
        self.side_qtd.setText(
            f"Quantidade: {item.quantidade:.3f}".rstrip("0").rstrip(".").replace(".", ",")
        )
        self.side_preco.setText(f"Preço Unitário: {fmt_br(item.preco_unitario)}")
        self.side_sub.setText(f"Subtotal: {fmt_br(item.subtotal)}")

    def _selecionar_item(self, idx):
        if idx < 0 or idx >= len(self.carrinho):
            return
        self._item_selecionado_idx = idx
        self._atualizar_sidebar(idx)
        self._atualizar_carrinho()

    def remover_selecionado(self):
        if self._item_selecionado_idx is None:
            return
        idx = self._item_selecionado_idx
        if 0 <= idx < len(self.carrinho):
            removido = self.carrinho.pop(idx)
            if self._ultimo_item == removido:
                self._ultimo_item = self.carrinho[-1] if self.carrinho else None
            self._item_selecionado_idx = None
            self._atualizar_carrinho()

    def finalizar_venda(self):
        if not self.carrinho:
            return

        total = sum(item.subtotal for item in self.carrinho)
        reply = QMessageBox.question(
            self, "Finalizar Venda",
            f"Total: {fmt_br(total)}\n\nConfirmar finalização da venda?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for item in self.carrinho:
                produto = item.produto
                produto.estoque_total = Decimal(str(produto.estoque_total)) - item.quantidade
                produto.save()

            self.carrinho.clear()
            self._ultimo_item = None
            self._item_selecionado_idx = None
            self._atualizar_carrinho()
            self._limpar_busca()
            self.side_qtd.setText("Quantidade: —")
            self.side_preco.setText("Preço Unitário: —")
            self.side_sub.setText("Subtotal: —")


if __name__ == "__main__":
    import subprocess, sys, os
    subprocess.run([
        sys.executable,
        os.path.join(os.path.dirname(__file__), "..", "main.py")
    ])
