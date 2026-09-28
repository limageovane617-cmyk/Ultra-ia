# ============================================================
# 🔐 ALEX IA ULTRA — SERVIÇOS E CONEXÕES
# ============================================================
# Criada por: Geovani
#
# Serviços:
# - Google Gemini
# - Hugging Face
# - Magic Hour
# ============================================================


# ============================================================
# 📦 IMPORTAÇÕES
# ============================================================

import streamlit as st

from google import genai

from huggingface_hub import InferenceClient


# ============================================================
# 🔑 GEMINI
# ============================================================

def obter_chave_gemini():
    """
    Obtém a chave do Gemini
    pelos Secrets do Streamlit.
    """

    try:

        chave = st.secrets.get(
            "GEMINI_API_KEY",
            ""
        )

        return str(
            chave
        ).strip()

    except Exception:

        return None


# ============================================================
# 🤗 HUGGING FACE
# ============================================================

def obter_token_huggingface():
    """
    Obtém o token do Hugging Face
    pelos Secrets do Streamlit.
    """

    try:

        token = st.secrets.get(
            "HF_TOKEN",
            ""
        )

        return str(
            token
        ).strip()

    except Exception:

        return None


# ============================================================
# 🎬 MAGIC HOUR
# ============================================================

def obter_chave_magic_hour():
    """
    Obtém a chave do Magic Hour
    pelos Secrets do Streamlit.
    """

    try:

        chave = st.secrets.get(
            "MAGIC_HOUR_API_KEY",
            ""
        )

        return str(
            chave
        ).strip()

    except Exception:

        return None


# ============================================================
# 🤖 CRIAR CLIENTE GEMINI
# ============================================================

def criar_cliente_gemini():
    """
    Cria o cliente da API Gemini.
    """

    chave = obter_chave_gemini()

    if not chave:

        return None

    try:

        return genai.Client(
            api_key=chave
        )

    except Exception:

        return None


# ============================================================
# 🤗 CRIAR CLIENTE HUGGING FACE
# ============================================================

def criar_cliente_huggingface():
    """
    Cria o cliente do Hugging Face.
    """

    token = obter_token_huggingface()

    if not token:

        return None

    try:

        return InferenceClient(
            provider="auto",
            api_key=token
        )

    except Exception:

        return None


# ============================================================
# 🔎 VERIFICAR SERVIÇOS
# ============================================================

def verificar_servicos():
    """
    Verifica quais serviços possuem
    credenciais configuradas.
    """

    resultado = {

        "gemini":
            bool(
                obter_chave_gemini()
            ),

        "huggingface":
            bool(
                obter_token_huggingface()
            ),

        "magic_hour":
            bool(
                obter_chave_magic_hour()
            ),

    }

    return resultado
