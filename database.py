"""
Configuração do banco de dados com Peewee (SQLite).
Gerencia a conexão e criação das tabelas do sistema PDV.
"""
import os
import sys
import peewee as pw


def _db_path():
    if getattr(sys, 'frozen', False):
        # Rodando como bundle (PyInstaller) — salva em ~/Library/Application Support
        app_support = os.path.join(
            os.path.expanduser("~"), "Library", "Application Support", "PDVMinimercado"
        )
        os.makedirs(app_support, exist_ok=True)
        return os.path.join(app_support, "pdv.db")
    # Rodando direto do fonte — usa o diretório do arquivo
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdv.db")


db = pw.SqliteDatabase(_db_path())


class BaseModel(pw.Model):
    class Meta:
        database = db


def conectar():
    db.connect()
    from models import Produto
    db.create_tables([Produto])
    return db


if __name__ == "__main__":
    import subprocess, sys, os
    subprocess.run([
        sys.executable,
        os.path.join(os.path.dirname(__file__), "main.py")
    ])
