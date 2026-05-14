"""
Utilitários para formatação de valores no padrão brasileiro (R$).
Lida com conversão entre formato de exibição (1.234,56) e interno (1234.56).
"""
import unicodedata
from decimal import Decimal, InvalidOperation


def fmt_br(valor):
    s = f"{float(valor):.2f}"
    inteiro, dec = s.split(".")
    partes = []
    while inteiro:
        partes.insert(0, inteiro[-3:])
        inteiro = inteiro[:-3]
    inteiro = ".".join(partes) if partes else "0"
    return f"R$ {inteiro},{dec}"


def parse_br(texto):
    texto = texto.strip().replace("R$", "").replace("r$", "").strip()
    if not texto or texto in (".", ","):
        return Decimal("0")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return Decimal(texto)
    except InvalidOperation:
        return Decimal("0")


def remover_acentos(texto):
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


if __name__ == "__main__":
    import subprocess, sys, os
    subprocess.run([
        sys.executable,
        os.path.join(os.path.dirname(__file__), "main.py")
    ])
