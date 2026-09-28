# ============================================================
# 🧭 ALEX IA ULTRA — ROUTER
# Direcionador de tarefas e ferramentas do Ultra Core
# ============================================================

from typing import Any, Dict, List, Optional

from .tools import Tool, ToolRegistry, tool_registry


class ToolRouter:
    """
    Decide qual ferramenta deve atender uma determinada tarefa.

    O Router utiliza explicitamente o tool_registry global
    do Ultra Core quando nenhuma instância personalizada
    é fornecida.

    Isso garante que Brain, Router e ToolRegistry utilizem
    a mesma fonte de ferramentas.
    """

    def __init__(
        self,
        registry: Optional[ToolRegistry] = None,
    ) -> None:

        # ----------------------------------------------------
        # Usa SEMPRE o registry global quando nenhum registry
        # personalizado for informado.
        #
        # Isso evita que o Router fique ligado a uma instância
        # diferente do ToolRegistry usado pelo Tool Loader.
        # ----------------------------------------------------

        self.registry = (
            registry
            if registry is not None
            else tool_registry
        )

    # ========================================================
    # 🔎 LOCALIZAR FERRAMENTA
    # ========================================================

    def find_tool(
        self,
        requested_tool: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ) -> Optional[Tool]:
        """
        Procura uma ferramenta disponível.

        Ordem de busca:

        1. Nome exato da ferramenta.
        2. Palavras-chave.
        """

        # ----------------------------------------------------
        # Busca direta pelo nome.
        # ----------------------------------------------------

        if requested_tool:

            tool = self.registry.get(
                requested_tool
            )

            if tool and tool.enabled:
                return tool

        # ----------------------------------------------------
        # Sem palavras-chave não há segunda tentativa.
        # ----------------------------------------------------

        if not keywords:
            return None

        normalized_keywords = [
            str(keyword)
            .lower()
            .strip()
            for keyword in keywords
            if keyword
        ]

        # ----------------------------------------------------
        # Busca por nome + descrição.
        # ----------------------------------------------------

        for tool_info in self.registry.list_tools():

            if not tool_info["enabled"]:
                continue

            searchable_text = (
                f"{tool_info['name']} "
                f"{tool_info['description']}"
            ).lower()

            if any(
                keyword in searchable_text
                for keyword in normalized_keywords
            ):

                return self.registry.get(
                    tool_info["name"]
                )

        return None

    # ========================================================
    # 🧭 ROTEAR ETAPA
    # ========================================================

    def route(
        self,
        step: Dict[str, Any],
    ) -> Optional[Tool]:
        """
        Escolhe a ferramenta para uma etapa do plano.
        """

        requested_tool = step.get(
            "tool"
        )

        keywords = step.get(
            "keywords",
            [],
        )

        return self.find_tool(
            requested_tool=requested_tool,
            keywords=keywords,
        )

    # ========================================================
    # 📝 EXPLICAR ROTA
    # ========================================================

    def explain_route(
        self,
        step: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Explica qual ferramenta foi escolhida.
        """

        tool = self.route(
            step
        )

        if tool is None:

            return {
                "success": False,
                "tool": None,
                "reason": (
                    "Nenhuma ferramenta compatível "
                    "foi encontrada."
                ),
            }

        return {
            "success": True,
            "tool": tool.name,
            "description": tool.description,
            "reason": (
                "Ferramenta encontrada no registro "
                "da Ultra."
            ),
        }

    # ========================================================
    # 🛠️ FERRAMENTAS DISPONÍVEIS
    # ========================================================

    def available_tools(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Retorna as ferramentas atualmente disponíveis.
        """

        return self.registry.list_tools()


# ============================================================
# 🧠 INSTÂNCIA PRINCIPAL
# ============================================================

# Importante:
# Não criar outro ToolRegistry aqui.
#
# O Router deve compartilhar exatamente o mesmo
# tool_registry utilizado pelo restante do Ultra Core.

router = ToolRouter(
    registry=tool_registry
)


# ============================================================
# 📦 EXPORTAÇÕES
# ============================================================

__all__ = [
    "ToolRouter",
    "router",
]
