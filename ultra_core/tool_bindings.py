# ============================================================
# 🔌 ALEX IA ULTRA — TOOL BINDINGS
# Conecta as ferramentas reais ao Ultra Core
# ============================================================

from typing import Any, Dict

from .tools import ToolRegistry, tool_registry

# Internet.py está na raiz do projeto ULTRA-IA-PRO.
from Internet import (
    preparar_pesquisa,
    pesquisar_web,
    pesquisar_capital,
)


# ============================================================
# 🌐 FERRAMENTA DE PESQUISA
# ============================================================

def pesquisar_internet(
    pergunta: str = "",
    prompt: str = "",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Executa uma pesquisa real na internet.

    Aceita tanto 'pergunta' quanto 'prompt' para manter
    compatibilidade com o Ultra Core.

    Para perguntas estruturadas sobre a capital de um país,
    utiliza Wikidata através do Internet Engine.

    Para outras perguntas, mantém o mecanismo DuckDuckGo.
    """

    consulta_usuario = (
        str(pergunta or "").strip()
        or str(prompt or "").strip()
    )

    if not consulta_usuario:
        raise ValueError(
            "A pergunta para pesquisa não pode estar vazia."
        )

    pesquisa = preparar_pesquisa(
        consulta_usuario
    )

    if pesquisa is None:
        raise ValueError(
            "Não foi possível preparar a pesquisa."
        )

    # ========================================================
    # 🟣 DETECÇÃO DE PERGUNTA SOBRE CAPITAL
    # ========================================================

    consulta_normalizada = (
        consulta_usuario.lower()
    )

    termos_capital = (
        "capital do ",
        "capital da ",
        "capital de ",
        "capital dos ",
        "capital das ",
    )

    eh_pergunta_capital = any(
        termo in consulta_normalizada
        for termo in termos_capital
    )

    if eh_pergunta_capital:

        # ----------------------------------------------------
        # Tenta identificar o país depois de "capital de..."
        # ----------------------------------------------------

        pais = ""

        marcadores = (
            "capital do ",
            "capital da ",
            "capital de ",
            "capital dos ",
            "capital das ",
        )

        for marcador in marcadores:

            posicao = consulta_normalizada.find(
                marcador
            )

            if posicao == -1:
                continue

            pais = consulta_usuario[
                posicao + len(marcador):
            ].strip()

            break

        # Remove pontuação simples no final.
        pais = pais.rstrip(
            "?.!,;:"
        ).strip()

        if pais:

            resultado_capital = pesquisar_capital(
                pais
            )

            if resultado_capital.get(
                "success"
            ):

                return {
                    "success": True,
                    "tool": "pesquisa_internet",
                    "pergunta": consulta_usuario,
                    "consulta": pesquisa,
                    "provider": resultado_capital.get(
                        "source",
                        "wikidata"
                    ),
                    "answer": resultado_capital.get(
                        "answer"
                    ),
                    "verified": resultado_capital.get(
                        "verified",
                        False
                    ),
                    "resultados": [
                        {
                            "titulo": (
                                f"Capital de {pais}"
                            ),
                            "resposta": (
                                resultado_capital.get(
                                    "answer"
                                )
                            ),
                        }
                    ],
                    "fontes": [
                        "https://www.wikidata.org/"
                    ],
                    "quantidade": 1,
                    "erro": None,
                }

    # ========================================================
    # 🔵 MECANISMO LEGADO — DUCKDUCKGO
    # ========================================================

    resultado_web = pesquisar_web(
        consulta_usuario
    )

    return {
        "success": resultado_web.get(
            "success",
            False
        ),
        "tool": "pesquisa_internet",
        "pergunta": consulta_usuario,
        "consulta": pesquisa,
        "provider": resultado_web.get(
            "provider",
            "duckduckgo_lite"
        ),
        "resultados": resultado_web.get(
            "resultados",
            []
        ),
        "fontes": resultado_web.get(
            "fontes",
            []
        ),
        "quantidade": resultado_web.get(
            "quantidade",
            0
        ),
        "erro": resultado_web.get(
            "erro"
        ),
    }


# ============================================================
# 🛠️ REGISTRO DAS FERRAMENTAS
# ============================================================

def registrar_ferramentas(
    registry: ToolRegistry = tool_registry,
) -> ToolRegistry:
    """
    Registra as ferramentas disponíveis no Ultra Core.
    """

    if not registry.has(
        "pesquisa_internet"
    ):
        registry.register(
            name="pesquisa_internet",
            description=(
                "Pesquisa informações atuais na internet "
                "usando Internet Engine, Wikidata e "
                "DuckDuckGo Lite."
            ),
            function=pesquisar_internet,
            metadata={
                "categoria": "internet",
                "provider": "internet_engine",
                "providers": [
                    "wikidata",
                    "duckduckgo_lite",
                ],
                "language": "pt-BR",
            },
        )

    return registry


# ============================================================
# 🚀 INICIALIZAÇÃO PADRÃO
# ============================================================

registrar_ferramentas()


# ============================================================
# 📦 EXPORTAÇÕES
# ============================================================

__all__ = [
    "pesquisar_internet",
    "registrar_ferramentas",
]
