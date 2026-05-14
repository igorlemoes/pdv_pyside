"""
Configuração do banco de dados com Peewee (SQLite).
Gerencia a conexão e criação das tabelas do sistema PDV.
"""
import peewee as pw

db = pw.SqliteDatabase("pdv.db")


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
