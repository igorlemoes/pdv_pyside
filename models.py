"""
Modelos do banco de dados para o sistema PDV de minimercado.
Usa Peewee ORM com SQLite.
"""
from database import BaseModel
import peewee as pw


class Produto(BaseModel):
    codigo = pw.IntegerField(unique=True, verbose_name="Código")
    nome = pw.CharField(max_length=200, verbose_name="Nome")
    tipo = pw.CharField(
        max_length=20,
        choices=[
            ("Unidade", "Unidade"),
            ("Kg", "Kg"),
            ("Metros", "Metros"),
            ("M2", "M2"),
            ("Caixas", "Caixas"),
        ],
        default="Unidade",
        verbose_name="Tipo"
    )
    valor_custo = pw.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="Valor de Custo"
    )
    lucro_pct = pw.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name="Lucro (%)"
    )
    valor_sugerido = pw.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="Valor Sugerido"
    )
    valor_venda = pw.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="Valor de Venda"
    )
    estoque_total = pw.DecimalField(
        max_digits=10, decimal_places=3, default=0,
        verbose_name="Estoque Total"
    )
    estoque_minimo = pw.DecimalField(
        max_digits=10, decimal_places=3, default=0,
        verbose_name="Estoque Mínimo"
    )
    validade = pw.DateField(null=True, verbose_name="Validade")

    class Meta:
        table_name = "produtos"

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


if __name__ == "__main__":
    import subprocess, sys, os
    subprocess.run([
        sys.executable,
        os.path.join(os.path.dirname(__file__), "main.py")
    ])
