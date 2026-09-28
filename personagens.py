# ============================================================
# 🎭 ALEX IA ULTRA — SISTEMA DE PERSONAGENS
# Criada por Geovani
# ============================================================

import sqlite3


BANCO_DADOS = "alexia.db"


def conectar():
    """Abre a conexão com o banco de dados."""
    return sqlite3.connect(BANCO_DADOS)


def criar_tabela():
    """Cria a tabela de personagens."""

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            idade TEXT,
            aparencia TEXT,
            roupa TEXT,
            personalidade TEXT
        )
    """)

    conn.commit()
    conn.close()


def salvar_personagem(
    nome,
    idade="",
    aparencia="",
    roupa="",
    personalidade=""
):
    """Cria ou atualiza um personagem."""

    if not nome or not nome.strip():
        return False

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO personagens
        (nome, idade, aparencia, roupa, personalidade)
        VALUES (?, ?, ?, ?, ?)
    """, (
        nome.strip(),
        idade.strip(),
        aparencia.strip(),
        roupa.strip(),
        personalidade.strip()
    ))

    conn.commit()
    conn.close()

    return True


def carregar_personagem(nome):
    """Carrega um personagem pelo nome."""

    if not nome:
        return None

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nome, idade, aparencia, roupa, personalidade
        FROM personagens
        WHERE nome = ?
    """, (nome,))

    resultado = cursor.fetchone()

    conn.close()

    if not resultado:
        return None

    return {
        "nome": resultado[0],
        "idade": resultado[1],
        "aparencia": resultado[2],
        "roupa": resultado[3],
        "personalidade": resultado[4]
    }


def listar_personagens():
    """Retorna todos os personagens salvos."""

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nome
        FROM personagens
        ORDER BY nome
    """)

    resultados = cursor.fetchall()

    conn.close()

    return [item[0] for item in resultados]


def apagar_personagem(nome):
    """Apaga um personagem."""

    if not nome:
        return False

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM personagens WHERE nome = ?",
        (nome,)
    )

    apagou = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return apagou


# Cria a tabela automaticamente.
criar_tabela()
