"""
Configuração do banco de dados com Peewee (SQLite).
Gerencia a conexão e criação das tabelas do sistema PDV.
"""
import os
import sys
import peewee as pw


def _db_path():
    if getattr(sys, 'frozen', False):
        if sys.platform == "win32":
            # %APPDATA%\PDVMinimercado\pdv.db
            base = os.environ.get("APPDATA", os.path.expanduser("~"))
        elif sys.platform == "darwin":
            # ~/Library/Application Support/PDVMinimercado/pdv.db
            base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
        else:
            # ~/.local/share/PDVMinimercado/pdv.db  (padrão XDG no Linux)
            base = os.environ.get("XDG_DATA_HOME", os.path.join(os.path.expanduser("~"), ".local", "share"))
        app_dir = os.path.join(base, "PDVMinimercado")
        os.makedirs(app_dir, exist_ok=True)
        return os.path.join(app_dir, "pdv.db")
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
