# ============================================================
# 🧠 ALEX IA ULTRA — BRAIN
# Cérebro central do Ultra Core
# ============================================================

from typing import Any, Dict, List, Optional
from uuid import uuid4

from .context import TaskContext
from .interpreter import TaskInterpreter, interpreter
from .planner import TaskPlanner, planner
from .router import ToolRouter, router
from .executor import TaskExecutor, executor
from .verifier import ResultVerifier, verifier
from .intelligence import UltraIntelligence, intelligence
from gemini_bridge import GeminiBridge


class UltraBrain:
    """
    Coordenador central da Alex IA Ultra.

    Fluxo principal:

        Pedido do usuário
              ↓
        Interpreter
              ↓
        Contexto
              ↓
        Planner
              ↓
        Router
              ↓
        Executor
              ↓
        Verifier
              ↓
        UltraIntelligence
              ↓
        GeminiBridge
              ↓
        Resposta final

    O Brain coordena os componentes.
    Ele não executa diretamente as ferramentas.
    """

    def __init__(
        self,
        task_interpreter: TaskInterpreter = interpreter,
        task_planner: TaskPlanner = planner,
        task_router: ToolRouter = router,
        task_executor: TaskExecutor = executor,
        result_verifier: ResultVerifier = verifier,
        task_intelligence: UltraIntelligence = intelligence,
        gemini_bridge: Optional[GeminiBridge] = None,
    ) -> None:

        self.interpreter = task_interpreter
        self.planner = task_planner
        self.router = task_router
        self.executor = task_executor
        self.verifier = result_verifier
        self.intelligence = task_intelligence
        self.gemini_bridge = gemini_bridge

    # ========================================================
    # 🧠 INTERPRETAÇÃO
    # ========================================================

    def interpret(
        self,
        user_request: str,
    ) -> Dict[str, Any]:
        """
        Interpreta o pedido do usuário.

        O Interpreter identifica:

        - intenção;
        - palavras-chave;
        - confiança;
        - prompt;
        - ferramentas sugeridas.
        """

        return self.interpreter.interpret(
            user_request
        )

    # ========================================================
    # 📝 CRIAÇÃO DE TAREFA
    # ========================================================

    def create_task(
        self,
        user_request: str,
    ) -> TaskContext:
        """
        Cria um novo contexto para uma solicitação.
        """

        if not user_request or not user_request.strip():
            raise ValueError(
                "A solicitação do usuário não pode estar vazia."
            )

        context = TaskContext(
            user_request=user_request.strip(),
            task_id=str(uuid4()),
        )

        context.update_status("created")

        return context

    # ========================================================
    # 🧠 PREPARAÇÃO DA TAREFA
    # ========================================================

    def prepare_task(
        self,
        context: TaskContext,
    ) -> Dict[str, Any]:
        """
        Interpreta o pedido e grava as informações
        importantes dentro do contexto.
        """

        interpretation = self.interpret(
            context.user_request
        )

        if not interpretation.get("success"):
            context.add_error(
                source="interpreter",
                message=interpretation.get(
                    "message",
                    "Não foi possível interpretar o pedido.",
                ),
            )

            context.update_status(
                "interpretation_failed"
            )

            return interpretation

        context.set_metadata(
            "intent",
            interpretation.get("intent"),
        )

        context.set_metadata(
            "keywords",
            interpretation.get("keywords", []),
        )

        context.set_metadata(
            "confidence",
            interpretation.get("confidence", 0.0),
        )

        context.set_metadata(
            "prompt",
            interpretation.get("prompt", ""),
        )

        context.set_metadata(
            "suggested_tools",
            interpretation.get(
                "suggested_tools",
                [],
            ),
        )

        context.set_metadata(
            "original_request",
            interpretation.get(
                "original_request",
                context.user_request,
            ),
        )

        context.update_status(
            "interpreted"
        )

        return interpretation

    # ========================================================
    # 📝 PLANEJAMENTO
    # ========================================================

    def plan_task(
        self,
        context: TaskContext,
        steps: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Cria o plano de execução da tarefa.
        """

        plan = self.planner.create_plan(
            context,
            steps,
        )

        # ----------------------------------------------------
        # O Planner original normaliza as etapas.
        # Aqui recuperamos as informações da interpretação
        # para que o Router também possa utilizá-las.
        # ----------------------------------------------------

        keywords = context.get_metadata(
            "keywords",
            [],
        )

        prompt = context.get_metadata(
            "prompt",
            "",
        )

        for step in plan:

            if "keywords" not in step:
                step["keywords"] = list(
                    keywords
                )

            arguments = step.setdefault(
                "arguments",
                {},
            )

            # Não sobrescreve argumentos fornecidos
            # manualmente pelo plano.
            if (
                prompt
                and "prompt" not in arguments
            ):
                arguments["prompt"] = prompt

        context.touch()

        return plan

    # ========================================================
    # 🤖 CRIAÇÃO AUTOMÁTICA DE PLANO
    # ========================================================

    def create_intelligent_plan(
        self,
        context: TaskContext,
    ) -> List[Dict[str, Any]]:
        """
        Cria uma etapa automaticamente a partir
        da interpretação do pedido.

        Esta é a primeira camada de planejamento
        inteligente da Ultra.
        """

        interpretation = self.prepare_task(
            context
        )

        if not interpretation.get("success"):
            return []

        intent = interpretation.get(
            "intent",
            "geral",
        )

        keywords = interpretation.get(
            "keywords",
            [],
        )

        suggested_tools = interpretation.get(
            "suggested_tools",
            [],
        )

        prompt = interpretation.get(
            "prompt",
            "",
        )

        # ----------------------------------------------------
        # Procura primeiro uma ferramenta sugerida
        # que realmente esteja registrada.
        # ----------------------------------------------------

        selected_tool = None

        for tool_name in suggested_tools:

            tool = self.router.registry.get(
                tool_name
            )

            if tool and tool.enabled:
                selected_tool = tool.name
                break

        step = {
            "name": f"Executar tarefa: {intent}",
            "description": (
                "Etapa criada automaticamente "
                "pelo cérebro da Ultra."
            ),
            "tool": selected_tool,
            "keywords": keywords,
            "arguments": {
                "prompt": prompt,
            },
        }

        return self.plan_task(
            context,
            [step],
        )

    # ========================================================
    # 🔧 FERRAMENTAS
    # ========================================================

    def available_tools(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Retorna as ferramentas disponíveis.
        """

        return self.router.available_tools()

    # ========================================================
    # 🧭 EXPLICAR ROTA
    # ========================================================

    def explain_route(
        self,
        context: TaskContext,
    ) -> Dict[str, Any]:
        """
        Explica qual ferramenta será utilizada.
        """

        if not context.plan:
            return {
                "success": False,
                "tool": None,
                "reason": (
                    "A tarefa ainda não possui "
                    "um plano."
                ),
            }

        return self.router.explain_route(
            context.plan[0]
        )

    # ========================================================
    # ⚙️ EXECUÇÃO
    # ========================================================

    def execute(
        self,
        context: TaskContext,
        *,
        stop_on_error: bool = True,
    ) -> Dict[str, Any]:
        """
        Executa o plano da tarefa.
        """

        if not context.plan:
            return {
                "success": False,
                "status": "no_plan",
                "message": (
                    "A tarefa ainda não possui "
                    "um plano de execução."
                ),
            }

        return self.executor.execute_all(
            context,
            stop_on_error=stop_on_error,
        )

    # ========================================================
    # 🔍 VERIFICAÇÃO
    # ========================================================

    def verify(
        self,
        context: TaskContext,
    ) -> Dict[str, Any]:
        """
        Verifica o resultado da tarefa.
        """

        return self.verifier.verify_context(
            context
        )

    # ========================================================
    # 🧠 RESPOSTA FINAL
    # ========================================================

    def generate_response(
        self,
        context: TaskContext,
    ) -> str:
        """
        Gera a resposta final usando a
        UltraIntelligence e o GeminiBridge.

        O Gemini é opcional.
        Se não estiver disponível, retorna
        uma resposta vazia sem interromper
        o funcionamento do Ultra Core.
        """

        if self.gemini_bridge is None:
            return ""

        return self.intelligence.generate_response(
            context=context,
            gemini_bridge=self.gemini_bridge,
        )

    # ========================================================
    # 🚀 CICLO COMPLETO
    # ========================================================

    def run(
        self,
        user_request: str,
        steps: Optional[List[Dict[str, Any]]] = None,
        *,
        stop_on_error: bool = True,
        history: str = "",
        file_context: str = "",
        file_name: str = "",
    ) -> Dict[str, Any]:
        """
        Executa o ciclo completo da Ultra.

        Se steps forem fornecidos:

            Pedido
              ↓
            Interpretação
              ↓
            Plano fornecido
              ↓
            Execução
              ↓
            Verificação
              ↓
            Resposta final

        Se steps não forem fornecidos:

            Pedido
              ↓
            Interpretação
              ↓
            Plano automático
              ↓
            Execução
              ↓
            Verificação
              ↓
            Resposta final
        """

        context = self.create_task(
            user_request
        )

        # Histórico e arquivo NÃO entram na interpretação:
        # ficam separados e só são usados no prompt final.
        context.set_metadata("history", history)
        context.set_metadata("file_context", file_context)
        context.set_metadata("file_name", file_name)

        # ----------------------------------------------------
        # INTERPRETAÇÃO
        # ----------------------------------------------------

        interpretation = self.prepare_task(
            context
        )

        if not interpretation.get("success"):
            return {
                "success": False,
                "status": context.status,
                "task_id": context.task_id,
                "interpretation": interpretation,
                "context": context.summary(),
            }

        # ----------------------------------------------------
        # PLANEJAMENTO
        # ----------------------------------------------------

        if steps:

            self.plan_task(
                context,
                steps,
            )

        else:

            self.create_intelligent_plan(
                context
            )

        # ----------------------------------------------------
        # EXECUÇÃO
        # ----------------------------------------------------

        usa_ferramenta = any(
            etapa.get("tool")
            for etapa in context.plan
        )

        if usa_ferramenta:
            execution = self.execute(
                context,
                stop_on_error=stop_on_error,
            )

            verification = self.verify(
                context
            )

        else:
            # Conversa simples: sem ferramenta, sem erro falso.
            execution = {"success": True, "skipped": True}
            verification = {"success": True, "skipped": True}

        # ----------------------------------------------------
        # RESULTADO FINAL
        # ----------------------------------------------------

        success = (
            execution.get(
                "success",
                False,
            )
            and verification.get(
                "success",
                False,
            )
        )

        if success:
            context.update_status(
                "completed"
            )

        # ----------------------------------------------------
        # RESPOSTA FINAL
        # ----------------------------------------------------

        final_response = self.generate_response(
            context
        )

        return {
            "success": success,
            "task_id": context.task_id,
            "status": context.status,
            "interpretation": interpretation,
            "plan": context.plan,
            "execution": execution,
            "verification": verification,
            "final_response": final_response,
            "context": context.summary(),
        }


# ============================================================
# 🧠 INSTÂNCIA PRINCIPAL
# ============================================================

brain = UltraBrain()


__all__ = [
    "UltraBrain",
    "brain",
]
