# ============================================================
# 🧠 ALEX IA ULTRA — SISTEMA DE MEMÓRIA
# Criada por Geovani
# ============================================================

import sqlite3


BANCO_DADOS = "alexia.db"


def conectar():
    """Abre a conexão com o banco de dados."""
    return sqlite3.connect(BANCO_DADOS)


def criar_tabela():
    """Cria a tabela de memória caso ela ainda não exista."""

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            informacao TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def salvar_memoria(informacao):
    """Salva uma nova informação na memória."""

    if not informacao:
        return

    informacao = informacao.strip()

    if not informacao:
        return

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM memoria WHERE informacao = ?",
        (informacao,)
    )

    existente = cursor.fetchone()

    if not existente:

        cursor.execute(
            "INSERT INTO memoria (informacao) VALUES (?)",
            (informacao,)
        )

        conn.commit()

    conn.close()


def carregar_memorias():
    """Carrega todas as memórias salvas."""

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT informacao FROM memoria ORDER BY id"
    )

    resultados = cursor.fetchall()

    conn.close()

    return [item[0] for item in resultados]


def apagar_memoria(informacao):
    """Apaga uma memória específica."""

    if not informacao:
        return

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM memoria WHERE informacao = ?",
        (informacao.strip(),)
    )

    conn.commit()
    conn.close()


def apagar_todas_memorias():
    """Apaga todas as memórias."""

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM memoria")

    conn.commit()
    conn.close()


# Cria a tabela automaticamente quando o módulo é carregado.
criar_tabela()
