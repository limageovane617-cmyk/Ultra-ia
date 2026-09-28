# ============================================================
# 🧠 ALEX IA ULTRA — CONTEXT ENGINE
# Gerenciador de contexto do Ultra Core
# ============================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class TaskContext:
    """
    Contexto completo de uma tarefa executada pela Ultra.
    """

    user_request: str

    task_id: Optional[str] = None

    status: str = "created"

    plan: List[Dict[str, Any]] = field(default_factory=list)

    tool_results: List[Dict[str, Any]] = field(default_factory=list)

    errors: List[Dict[str, Any]] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    updated_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    def update_status(self, status: str) -> None:
        """Atualiza o estado atual da tarefa."""

        self.status = status
        self.touch()

    def add_plan_step(self, step: Dict[str, Any]) -> None:
        """Adiciona uma etapa ao planejamento."""

        self.plan.append(step)
        self.touch()

    def add_tool_result(
        self,
        tool: str,
        success: bool,
        result: Any = None,
    ) -> None:
        """Registra o resultado de uma ferramenta."""

        self.tool_results.append(
            {
                "tool": tool,
                "success": success,
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        self.touch()

    def add_error(
        self,
        source: str,
        message: str,
        details: Any = None,
    ) -> None:
        """Registra um erro ocorrido durante a tarefa."""

        self.errors.append(
            {
                "source": source,
                "message": message,
                "details": details,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        self.touch()

    def set_metadata(self, key: str, value: Any) -> None:
        """Armazena uma informação adicional no contexto."""

        self.metadata[key] = value
        self.touch()

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Recupera uma informação do contexto."""

        return self.metadata.get(key, default)

    def touch(self) -> None:
        """Atualiza o horário da última alteração."""

        self.updated_at = datetime.utcnow().isoformat()

    def has_errors(self) -> bool:
        """Indica se a tarefa possui erros registrados."""

        return len(self.errors) > 0

    def is_successful(self) -> bool:
        """Indica se a tarefa terminou com sucesso."""

        return self.status == "completed" and not self.has_errors()

    def summary(self) -> Dict[str, Any]:
        """Retorna um resumo seguro do estado da tarefa."""

        return {
            "task_id": self.task_id,
            "request": self.user_request,
            "status": self.status,
            "plan_steps": len(self.plan),
            "tool_results": len(self.tool_results),
            "errors": len(self.errors),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
