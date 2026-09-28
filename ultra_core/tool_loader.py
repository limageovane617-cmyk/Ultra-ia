# ============================================================
# 🧠 ALEX IA ULTRA — TOOL LOADER
# Carregador central das ferramentas reais do sistema
# ============================================================

from typing import Any, Dict

from .tools import tool_registry


def _registrar_pesquisa(
    ferramentas_carregadas: Dict[str, Any],
) -> None:
    """
    Carrega as ferramentas de pesquisa da Ultra.
    """

    try:
        from .tool_bindings import registrar_ferramentas

        registrar_ferramentas(
            tool_registry
        )

        if tool_registry.has(
            "pesquisa_internet"
        ):
            ferramentas_carregadas[
                "pesquisa_internet"
            ] = True
        else:
            ferramentas_carregadas[
                "pesquisa_internet"
            ] = {
                "erro": (
                    "A ferramenta de pesquisa "
                    "não foi registrada."
                )
            }

    except Exception as erro:
        ferramentas_carregadas[
            "pesquisa_internet"
        ] = {
            "erro": str(erro)
        }


def _registrar_imagem(
    ferramentas_carregadas: Dict[str, Any],
) -> None:
    """
    Carrega o gerador de imagens existente.
    """

    try:
        from gerenciador_imagem import (
            gerar_imagem_pixazo,
        )

        if not tool_registry.has(
            "imagem.gerar"
        ):
            tool_registry.register(
                name="imagem.gerar",
                description=(
                    "Gera uma imagem a partir de "
                    "uma descrição usando o sistema "
                    "de geração de imagens da Ultra."
                ),
                function=gerar_imagem_pixazo,
                metadata={
                    "categoria": "imagem",
                    "tipo": "geracao",
                },
            )

        ferramentas_carregadas[
            "imagem.gerar"
        ] = True

    except Exception as erro:
        ferramentas_carregadas[
            "imagem.gerar"
        ] = {
            "erro": str(erro)
        }


def _registrar_video(
    ferramentas_carregadas: Dict[str, Any],
) -> None:
    """
    Carrega os geradores de vídeo existentes.

    O vídeo continua sendo opcional. Se o módulo
    não estiver disponível, o restante da Ultra
    continua funcionando normalmente.
    """

    try:
        from gerenciador_video import (
            gerar_video,
            gerar_video_texto,
            gerar_video_imagem,
            gerar_video_fallback,
        )

        funcoes_video = {
            "video.gerar": (
                gerar_video,
                "Gerenciador principal de geração de vídeo.",
            ),
            "video.texto": (
                gerar_video_texto,
                "Gera vídeo a partir de texto.",
            ),
            "video.imagem": (
                gerar_video_imagem,
                "Gera vídeo a partir de uma imagem.",
            ),
            "video.fallback": (
                gerar_video_fallback,
                "Motor alternativo de geração de vídeo.",
            ),
        }

        for nome, (
            funcao,
            descricao,
        ) in funcoes_video.items():

            if not tool_registry.has(
                nome
            ):
                tool_registry.register(
                    name=nome,
                    description=descricao,
                    function=funcao,
                    metadata={
                        "categoria": "video",
                        "tipo": nome.split(
                            ".",
                            1,
                        )[1],
                    },
                )

            ferramentas_carregadas[
                nome
            ] = True

    except Exception as erro:
        ferramentas_carregadas[
            "video"
        ] = {
            "erro": str(erro)
        }


def carregar_ferramentas() -> Dict[str, Any]:
    """
    Carrega todas as ferramentas conhecidas
    pelo Ultra Core.

    A ordem de carregamento é:

    1. Pesquisa
    2. Imagem
    3. Vídeo

    Cada ferramenta possui isolamento de erro,
    portanto uma falha em uma ferramenta não
    impede as demais de serem carregadas.
    """

    ferramentas_carregadas: Dict[str, Any] = {}

    # ========================================================
    # 🌐 PESQUISA
    # ========================================================

    _registrar_pesquisa(
        ferramentas_carregadas
    )

    # ========================================================
    # 🎨 IMAGEM
    # ========================================================

    _registrar_imagem(
        ferramentas_carregadas
    )

    # ========================================================
    # 🎬 VÍDEO
    # ========================================================

    _registrar_video(
        ferramentas_carregadas
    )

    return ferramentas_carregadas


def ferramentas_disponiveis() -> list[Dict[str, Any]]:
    """
    Retorna todas as ferramentas atualmente
    registradas no Ultra Core.
    """

    return tool_registry.list_tools()


def status_ferramentas() -> Dict[str, Any]:
    """
    Retorna um resumo do estado das ferramentas.
    """

    ferramentas = (
        tool_registry.list_tools()
    )

    return {
        "total": len(ferramentas),
        "habilitadas": sum(
            1
            for ferramenta in ferramentas
            if ferramenta["enabled"]
        ),
        "ferramentas": ferramentas,
    }


__all__ = [
    "carregar_ferramentas",
    "ferramentas_disponiveis",
    "status_ferramentas",
]
