# ============================================================
# PONTE ALEX - INTEGRACAO COM A PONTE ALEX v2
# ============================================================

import os
from pathlib import Path
from typing import Optional, Dict, Any

from cliente_ponte_alex import (
    ClientePonteAlex,
    ErroPonteAlex,
)


DEFAULT_PONTE_URL = "https://ponte-alex-v2.onrender.com"


def criar_cliente_ponte(
    base_url: Optional[str] = None,
) -> ClientePonteAlex:
    """
    Cria um cliente conectado a Ponte Alex v2.

    A chave PONTE_API_SECRET nunca fica escrita neste arquivo.
    Ela deve existir como variavel de ambiente.
    """

    url = (
        base_url
        or os.environ.get("PONTE_API_URL")
        or DEFAULT_PONTE_URL
    )

    return ClientePonteAlex(base_url=url)


def verificar_ponte(
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Verifica se a Ponte Alex v2 esta online.
    """

    cliente = criar_cliente_ponte(base_url)

    return cliente.ping()


def processar_arquivo_ponte(
    caminho_arquivo: str,
    instrucao: str,
    arquivo_saida: Optional[str] = None,
    destino_local: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Envia um arquivo Python para a Ponte Alex v2.

    A Ponte processa, valida, executa e devolve
    o arquivo resultante.
    """

    cliente = criar_cliente_ponte(base_url)

    return cliente.processar_arquivo(
        caminho_arquivo=caminho_arquivo,
        instrucao=instrucao,
        arquivo_saida=arquivo_saida,
        destino_local=destino_local,
    )


def processar_codigo_ponte(
    conteudo_codigo: str,
    instrucao: str,
    nome_arquivo: str = "script.py",
    nome_saida: Optional[str] = None,
    destino_local: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Envia codigo Python diretamente para a Ponte Alex v2.
    """

    cliente = criar_cliente_ponte(base_url)

    return cliente.processar_codigo(
        conteudo_codigo=conteudo_codigo,
        instrucao=instrucao,
        nome_arquivo=nome_arquivo,
        nome_saida=nome_saida,
        destino_local=destino_local,
    )


def ponte_disponivel(
    base_url: Optional[str] = None,
) -> bool:
    """
    Retorna True se a Ponte estiver online.
    """

    try:
        dados = verificar_ponte(base_url)

        return dados.get("status") == "online"

    except Exception:
        return False


def obter_status_ponte(
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retorna informacoes de status da Ponte sem expor
    a chave de autenticacao.
    """

    try:
        dados = verificar_ponte(base_url)

        return {
            "online": dados.get("status") == "online",
            "status": dados.get("status"),
            "ponte": dados.get("ponte"),
            "version": dados.get("version"),
            "pythonRuntime": dados.get("pythonRuntime"),
            "message": dados.get("message"),
        }

    except ErroPonteAlex as erro:

        return {
            "online": False,
            "status": "offline",
            "erro": str(erro),
        }

    except Exception as erro:

        return {
            "online": False,
            "status": "offline",
            "erro": str(erro),
        }


__all__ = [
    "DEFAULT_PONTE_URL",
    "ClientePonteAlex",
    "ErroPonteAlex",
    "criar_cliente_ponte",
    "verificar_ponte",
    "processar_arquivo_ponte",
    "processar_codigo_ponte",
    "ponte_disponivel",
    "obter_status_ponte",
]
