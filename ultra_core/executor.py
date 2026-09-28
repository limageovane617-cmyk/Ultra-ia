# ============================================================
# ⚙️ ALEX IA ULTRA — EXECUTOR
# Executor controlado do Ultra Core
# ============================================================

from typing import Any, Dict

from .context import TaskContext
from .planner import TaskPlanner, planner
from .router import ToolRouter, router


class TaskExecutor:
    """
    Executa as etapas planejadas pela Alex IA Ultra.
    """

    def __init__(
        self,
        task_router: ToolRouter = router,
        task_planner: TaskPlanner = planner,
    ) -> None:
        self.router = task_router
        self.planner = task_planner

    def execute_step(
        self,
        context: TaskContext,
        step_id: int,
    ) -> Dict[str, Any]:
        """
        Executa uma única etapa do plano.
        """

        step = self._get_step(context, step_id)

        self.planner.start_step(
            context,
            step_id,
        )

        tool = self.router.route(step)

        if tool is None:
            error_message = (
                f"Nenhuma ferramenta disponível para "
                f"a etapa {step_id}."
            )

            self.planner.fail_step(
                context,
                step_id,
                error_message,
            )

            context.add_error(
                source="executor",
                message=error_message,
            )

            return {
                "success": False,
                "step_id": step_id,
                "error": error_message,
            }

        try:
            arguments = step.get(
                "arguments",
                {},
            )

            result = tool.execute(
                **arguments,
            )

            self.planner.complete_step(
                context,
                step_id,
                result,
            )

            context.add_tool_result(
                tool=tool.name,
                success=True,
                result=result,
            )

            return {
                "success": True,
                "step_id": step_id,
                "tool": tool.name,
                "result": result,
            }

        except Exception as exc:
            error_message = str(exc)

            self.planner.fail_step(
                context,
                step_id,
                error_message,
            )

            context.add_error(
                source=f"tool:{tool.name}",
                message=error_message,
            )

            context.add_tool_result(
                tool=tool.name,
                success=False,
                result=None,
            )

            return {
                "success": False,
                "step_id": step_id,
                "tool": tool.name,
                "error": error_message,
            }

    def execute_next(
        self,
        context: TaskContext,
    ) -> Dict[str, Any]:
        """
        Executa a próxima etapa pendente.
        """

        pending = self.planner.pending_steps(
            context,
        )

        if not pending:
            return {
                "success": False,
                "message": (
                    "Não existem etapas pendentes."
                ),
            }

        next_step = pending[0]

        return self.execute_step(
            context,
            next_step["id"],
        )

    def execute_all(
        self,
        context: TaskContext,
        stop_on_error: bool = True,
    ) -> Dict[str, Any]:
        """
        Executa todas as etapas pendentes.

        Por padrão, interrompe quando encontra um erro.
        """

        results = []

        while not self.planner.is_complete(context):

            pending = self.planner.pending_steps(
                context,
            )

            if not pending:
                break

            step_id = pending[0]["id"]

            result = self.execute_step(
                context,
                step_id,
            )

            results.append(result)

            if not result.get("success") and stop_on_error:
                break

        if self.planner.is_complete(context):
            context.update_status("completed")

            return {
                "success": True,
                "status": "completed",
                "results": results,
            }

        if context.has_errors():
            context.update_status("failed")

            return {
                "success": False,
                "status": "failed",
                "results": results,
                "errors": context.errors,
            }

        return {
            "success": False,
            "status": context.status,
            "results": results,
        }

    @staticmethod
    def _get_step(
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
            f"Etapa {step_id} não encontrada."
        )


# ============================================================
# INSTÂNCIA PADRÃO
# ============================================================

executor = TaskExecutor()


__all__ = [
    "TaskExecutor",
    "executor",
]
