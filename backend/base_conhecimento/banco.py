import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "professor.db")


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar():
    with conectar() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS resumos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resumo TEXT NOT NULL,
                nivel TEXT NOT NULL,
                criado_em TEXT NOT NULL
            )
        """)
        conn.commit()


def salvar_resumo(resumo: str, nivel: str) -> int:
    with conectar() as conn:
        cursor = conn.execute(
            "INSERT INTO resumos (resumo, nivel, criado_em) VALUES (?, ?, ?)",
            (resumo, nivel, datetime.now().isoformat())
        )
        conn.commit()
        return cursor.lastrowid


def buscar_resumo(resumo_id: int) -> dict | None:
    with conectar() as conn:
        row = conn.execute("SELECT * FROM resumos WHERE id = ?", (resumo_id,)).fetchone()
        return dict(row) if row else None
