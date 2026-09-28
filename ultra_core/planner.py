# ============================================================
# 🧠 ALEX IA ULTRA — PLANNER
# Planejador de tarefas do Ultra Core
# ============================================================

from typing import Any, Dict, List

from .context import TaskContext


class TaskPlanner:
    """
    Cria e gerencia o plano de execução de uma tarefa.
    """

    def create_plan(
        self,
        context: TaskContext,
        steps: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Cria um plano a partir de etapas previamente definidas.

        O Planner não executa as etapas.
        Ele apenas organiza o trabalho.
        """

        context.plan.clear()

        for index, step in enumerate(steps, start=1):
            normalized_step = {
                "id": index,
                "name": step.get("name", f"Etapa {index}"),
                "description": step.get("description", ""),
                "tool": step.get("tool"),
                "arguments": step.get("arguments", {}),
                "status": "pending",
            }

            context.add_plan_step(normalized_step)

        context.update_status("planned")

        return context.plan

    def add_step(
        self,
        context: TaskContext,
        name: str,
        description: str = "",
        tool: str | None = None,
        arguments: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Adiciona uma nova etapa ao plano.
        """

        step = {
            "id": len(context.plan) + 1,
            "name": name,
            "description": description,
            "tool": tool,
            "arguments": arguments or {},
            "status": "pending",
        }

        context.add_plan_step(step)

        return step

    def start_step(
        self,
        context: TaskContext,
        step_id: int,
    ) -> Dict[str, Any]:
        """
        Marca uma etapa como em execução.
        """

        step = self._get_step(context, step_id)

        step["status"] = "running"
        context.update_status("executing")

        return step

    def complete_step(
        self,
        context: TaskContext,
        step_id: int,
        result: Any = None,
    ) -> Dict[str, Any]:
        """
        Marca uma etapa como concluída.
        """

        step = self._get_step(context, step_id)

        step["status"] = "completed"
        step["result"] = result

        context.touch()

        return step

    def fail_step(
        self,
        context: TaskContext,
        step_id: int,
        error: str,
    ) -> Dict[str, Any]:
        """
        Marca uma etapa como falha.
        """

        step = self._get_step(context, step_id)

        step["status"] = "failed"
        step["error"] = error

        context.update_status("failed")

        return step

    def pending_steps(
        self,
        context: TaskContext,
    ) -> List[Dict[str, Any]]:
        """
        Retorna as etapas que ainda não foram concluídas.
        """

        return [
            step
            for step in context.plan
            if step.get("status") != "completed"
        ]

    def is_complete(
        self,
        context: TaskContext,
    ) -> bool:
        """
        Verifica se todas as etapas foram concluídas.
        """

        if not context.plan:
            return False

        return all(
            step.get("status") == "completed"
            for step in context.plan
        )

    def _get_step(
        self,
        context: TaskContext,
        step_id: int,
    ) -> Dict[str, Any]:
        """
        Localiza uma etapa pelo ID.
        """

        for step in context.plan:
            if step.get("id") == step_id:
                return step

        raise KeyError(
            f"Etapa {step_id} não encontrada no plano."
        )


# ============================================================
# INSTÂNCIA PADRÃO
# ============================================================

planner = TaskPlanner()


__all__ = [
    "TaskPlanner",
    "planner",
]
