# ============================================================
# 🛠️ ALEX IA ULTRA — TOOL REGISTRY
# Registro central de ferramentas do Ultra Core
# ============================================================

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional


@dataclass
class Tool:
    """
    Representa uma ferramenta que pode ser utilizada pela Ultra.
    """

    name: str
    description: str
    function: Callable[..., Any]

    enabled: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)

    def execute(self, **kwargs: Any) -> Any:
        """
        Executa a ferramenta com os argumentos fornecidos.
        """

        if not self.enabled:
            raise RuntimeError(
                f"A ferramenta '{self.name}' está desativada."
            )

        return self.function(**kwargs)


class ToolRegistry:
    """
    Registro central de ferramentas da Alex IA Ultra.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(
        self,
        name: str,
        description: str,
        function: Callable[..., Any],
        *,
        enabled: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tool:
        """
        Registra uma nova ferramenta.
        """

        if not name:
            raise ValueError("O nome da ferramenta não pode estar vazio.")

        if not callable(function):
            raise TypeError(
                f"A ferramenta '{name}' precisa receber uma função executável."
            )

        if name in self._tools:
            raise ValueError(
                f"A ferramenta '{name}' já está registrada."
            )

        tool = Tool(
            name=name,
            description=description,
            function=function,
            enabled=enabled,
            metadata=metadata or {},
        )

        self._tools[name] = tool

        return tool

    def unregister(self, name: str) -> bool:
        """
        Remove uma ferramenta do registro.
        """

        if name not in self._tools:
            return False

        del self._tools[name]

        return True

    def get(self, name: str) -> Optional[Tool]:
        """
        Recupera uma ferramenta pelo nome.
        """

        return self._tools.get(name)

    def require(self, name: str) -> Tool:
        """
        Recupera uma ferramenta ou gera erro caso ela não exista.
        """

        tool = self.get(name)

        if tool is None:
            raise KeyError(
                f"A ferramenta '{name}' não está registrada."
            )

        return tool

    def enable(self, name: str) -> None:
        """
        Ativa uma ferramenta.
        """

        tool = self.require(name)

        tool.enabled = True

    def disable(self, name: str) -> None:
        """
        Desativa uma ferramenta.
        """

        tool = self.require(name)

        tool.enabled = False

    def list_tools(self) -> list[Dict[str, Any]]:
        """
        Lista as ferramentas disponíveis.
        """

        return [
            {
                "name": tool.name,
                "description": tool.description,
                "enabled": tool.enabled,
                "metadata": tool.metadata,
            }
            for tool in self._tools.values()
        ]

    def has(self, name: str) -> bool:
        """
        Verifica se uma ferramenta está registrada.
        """

        return name in self._tools

    def count(self) -> int:
        """
        Retorna a quantidade de ferramentas registradas.
        """

        return len(self._tools)


# ============================================================
# REGISTRO GLOBAL DO ULTRA CORE
# ============================================================

tool_registry = ToolRegistry()


__all__ = [
    "Tool",
    "ToolRegistry",
    "tool_registry",
]
