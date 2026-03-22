import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "professor.db")
ARQUIVOS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "arquivos")


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar():
    os.makedirs(ARQUIVOS_PATH, exist_ok=True)
    with conectar() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS areas (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nome        TEXT NOT NULL UNIQUE,
                descricao   TEXT,
                criado_em   TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS arquivos (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                area_id         INTEGER NOT NULL REFERENCES areas(id),
                nome_original   TEXT NOT NULL,
                tipo            TEXT NOT NULL,
                caminho         TEXT NOT NULL,
                tamanho_mb      REAL NOT NULL,
                enviado_por     TEXT,
                criado_em       TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS conteudo_gerado (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                arquivo_id  INTEGER NOT NULL REFERENCES arquivos(id),
                tipo        TEXT NOT NULL,
                conteudo    TEXT NOT NULL,
                custo_brl   REAL,
                criado_em   TEXT NOT NULL
            )
        """)

        # manter compatibilidade com rotas antigas
        conn.execute("""
            CREATE TABLE IF NOT EXISTS resumos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                resumo      TEXT NOT NULL,
                nivel       TEXT NOT NULL,
                criado_em   TEXT NOT NULL
            )
        """)

        conn.commit()


# ─── Áreas ───────────────────────────────────────────────────────────────────

def criar_area(nome: str, descricao: str = "") -> int:
    with conectar() as conn:
        cur = conn.execute(
            "INSERT INTO areas (nome, descricao, criado_em) VALUES (?, ?, ?)",
            (nome, descricao, datetime.now().isoformat())
        )
        conn.commit()
        return cur.lastrowid


def listar_areas() -> list[dict]:
    with conectar() as conn:
        rows = conn.execute("SELECT * FROM areas ORDER BY nome").fetchall()
        return [dict(r) for r in rows]


def buscar_area(area_id: int) -> dict | None:
    with conectar() as conn:
        row = conn.execute("SELECT * FROM areas WHERE id = ?", (area_id,)).fetchone()
        return dict(row) if row else None


# ─── Arquivos ─────────────────────────────────────────────────────────────────

def salvar_arquivo(
    area_id: int,
    nome_original: str,
    tipo: str,
    conteudo_bytes: bytes,
    enviado_por: str = "",
) -> int:
    agora = datetime.now().isoformat()
    tamanho_mb = round(len(conteudo_bytes) / (1024 * 1024), 3)

    # pasta da área dentro de data/arquivos/
    area = buscar_area(area_id)
    pasta_area = os.path.join(ARQUIVOS_PATH, str(area_id))
    os.makedirs(pasta_area, exist_ok=True)

    # nome único para evitar colisão
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_salvo = f"{timestamp}_{nome_original}"
    caminho = os.path.join(pasta_area, nome_salvo)

    with open(caminho, "wb") as f:
        f.write(conteudo_bytes)

    with conectar() as conn:
        cur = conn.execute(
            """INSERT INTO arquivos
               (area_id, nome_original, tipo, caminho, tamanho_mb, enviado_por, criado_em)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (area_id, nome_original, tipo, caminho, tamanho_mb, enviado_por, agora)
        )
        conn.commit()
        return cur.lastrowid


def listar_arquivos(area_id: int) -> list[dict]:
    with conectar() as conn:
        rows = conn.execute(
            "SELECT * FROM arquivos WHERE area_id = ? ORDER BY criado_em DESC",
            (area_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def buscar_arquivo(arquivo_id: int) -> dict | None:
    with conectar() as conn:
        row = conn.execute("SELECT * FROM arquivos WHERE id = ?", (arquivo_id,)).fetchone()
        return dict(row) if row else None


# ─── Conteúdo gerado ──────────────────────────────────────────────────────────

def salvar_conteudo(arquivo_id: int, tipo: str, conteudo: str, custo_brl: float = 0.0) -> int:
    with conectar() as conn:
        cur = conn.execute(
            """INSERT INTO conteudo_gerado
               (arquivo_id, tipo, conteudo, custo_brl, criado_em)
               VALUES (?, ?, ?, ?, ?)""",
            (arquivo_id, tipo, conteudo, custo_brl, datetime.now().isoformat())
        )
        conn.commit()
        return cur.lastrowid


def listar_conteudo(arquivo_id: int) -> list[dict]:
    with conectar() as conn:
        rows = conn.execute(
            "SELECT * FROM conteudo_gerado WHERE arquivo_id = ? ORDER BY criado_em DESC",
            (arquivo_id,)
        ).fetchall()
        return [dict(r) for r in rows]


# ─── Compatibilidade com rotas antigas ────────────────────────────────────────

def salvar_resumo(resumo: str, nivel: str) -> int:
    with conectar() as conn:
        cur = conn.execute(
            "INSERT INTO resumos (resumo, nivel, criado_em) VALUES (?, ?, ?)",
            (resumo, nivel, datetime.now().isoformat())
        )
        conn.commit()
        return cur.lastrowid


def buscar_resumo(resumo_id: int) -> dict | None:
    with conectar() as conn:
        row = conn.execute("SELECT * FROM resumos WHERE id = ?", (resumo_id,)).fetchone()
        return dict(row) if row else None
