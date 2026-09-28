# ============================================================
# 🔍 ALEX IA ULTRA — VERIFIER
# Sistema inteligente de verificação do Ultra Core
# ============================================================

from typing import Any, Dict, List, Optional

from .context import TaskContext


class VerificationResult:
    """
    Resultado de uma verificação.
    """

    def __init__(
        self,
        success: bool,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:

        self.success = bool(success)

        self.message = str(
            message
        )

        self.details = (
            details
            if isinstance(details, dict)
            else {}
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o resultado para dicionário.
        """

        return {
            "success": self.success,
            "message": self.message,
            "details": self.details,
        }


class ResultVerifier:
    """
    Verificador inteligente de resultados produzidos
    pelas ferramentas da Alex IA Ultra.

    O Verifier não executa ferramentas.

    Ele analisa os resultados produzidos pelo Executor
    e tenta determinar se a tarefa realmente funcionou.
    """

    # ========================================================
    # VERIFICAÇÃO BÁSICA
    # ========================================================

    def verify_result(
        self,
        result: Any,
    ) -> VerificationResult:
        """
        Faz uma análise inteligente de um resultado.

        Diferentemente da versão básica, esta função
        reconhece indicadores explícitos de sucesso
        e falha.
        """

        # ----------------------------------------------------
        # RESULTADO INEXISTENTE
        # ----------------------------------------------------

        if result is None:

            return VerificationResult(
                success=False,
                message=(
                    "A ferramenta não retornou "
                    "nenhum resultado."
                ),
                details={
                    "result_type": "NoneType",
                    "empty": True,
                },
            )

        # ----------------------------------------------------
        # BOOLEANO
        # ----------------------------------------------------

        if isinstance(
            result,
            bool,
        ):

            return VerificationResult(
                success=result,
                message=(
                    "Resultado booleano recebido."
                    if result
                    else
                    "A ferramenta retornou False."
                ),
                details={
                    "result_type": "bool",
                    "value": result,
                },
            )

        # ----------------------------------------------------
        # DICIONÁRIO
        # ----------------------------------------------------

        if isinstance(
            result,
            dict,
        ):

            return self._verify_dict(
                result
            )

        # ----------------------------------------------------
        # LISTA / TUPLA
        # ----------------------------------------------------

        if isinstance(
            result,
            (list, tuple),
        ):

            if not result:

                return VerificationResult(
                    success=False,
                    message=(
                        "A ferramenta retornou "
                        "uma coleção vazia."
                    ),
                    details={
                        "result_type":
                            type(result).__name__,
                        "empty": True,
                    },
                )

            return VerificationResult(
                success=True,
                message=(
                    "A ferramenta retornou "
                    "uma coleção com dados."
                ),
                details={
                    "result_type":
                        type(result).__name__,
                    "items":
                        len(result),
                    "empty": False,
                },
            )

        # ----------------------------------------------------
        # STRING
        # ----------------------------------------------------

        if isinstance(
            result,
            str,
        ):

            texto = result.strip()

            if not texto:

                return VerificationResult(
                    success=False,
                    message=(
                        "A ferramenta retornou "
                        "um texto vazio."
                    ),
                    details={
                        "result_type": "str",
                        "empty": True,
                    },
                )

            if self._text_indicates_failure(
                texto
            ):

                return VerificationResult(
                    success=False,
                    message=(
                        "O resultado contém "
                        "indícios de erro."
                    ),
                    details={
                        "result_type": "str",
                        "value": texto,
                    },
                )

            return VerificationResult(
                success=True,
                message=(
                    "Resultado textual recebido."
                ),
                details={
                    "result_type": "str",
                    "length": len(texto),
                    "empty": False,
                },
            )

        # ----------------------------------------------------
        # OUTROS TIPOS
        # ----------------------------------------------------

        return VerificationResult(
            success=True,
            message=(
                "Resultado recebido "
                "e não apresenta falha explícita."
            ),
            details={
                "result_type":
                    type(result).__name__,
            },
        )

    # ========================================================
    # VERIFICAÇÃO DE DICIONÁRIO
    # ========================================================

    def _verify_dict(
        self,
        result: Dict[str, Any],
    ) -> VerificationResult:
        """
        Analisa dicionários retornados pelas ferramentas.
        """

        if not result:

            return VerificationResult(
                success=False,
                message=(
                    "A ferramenta retornou "
                    "um dicionário vazio."
                ),
                details={
                    "result_type": "dict",
                    "empty": True,
                },
            )

        # ----------------------------------------------------
        # INDICADORES EXPLÍCITOS DE SUCESSO
        # ----------------------------------------------------

        success_values = []

        for chave in (
            "success",
            "sucesso",
        ):

            if chave in result:

                success_values.append(
                    bool(
                        result[chave]
                    )
                )

        # ----------------------------------------------------
        # INDICADORES EXPLÍCITOS DE FALHA
        # ----------------------------------------------------

        failure_detected = False

        for chave in (
            "error",
            "erro",
            "exception",
        ):

            if chave not in result:
                continue

            valor = result.get(
                chave
            )

            if valor not in (
                None,
                "",
                False,
            ):

                failure_detected = True

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status = str(
            result.get(
                "status",
                ""
            )
        ).strip().lower()

        status_failure = status in {
            "failed",
            "failure",
            "error",
            "erro",
            "falhou",
            "failed_task",
            "cancelled",
            "canceled",
        }

        status_success = status in {
            "success",
            "successful",
            "completed",
            "complete",
            "successfully",
            "concluido",
            "concluído",
        }

        # ----------------------------------------------------
        # FALHA EXPLÍCITA TEM PRIORIDADE
        # ----------------------------------------------------

        if failure_detected or status_failure:

            return VerificationResult(
                success=False,
                message=(
                    "A ferramenta retornou "
                    "um resultado com indicação de falha."
                ),
                details={
                    "result_type": "dict",
                    "status": status,
                    "explicit_success":
                        success_values,
                    "failure_detected":
                        failure_detected,
                },
            )

        # ----------------------------------------------------
        # SUCCESS / SUCESSO
        # ----------------------------------------------------

        if success_values:

            sucesso = all(
                success_values
            )

            return VerificationResult(
                success=sucesso,
                message=(
                    "A ferramenta confirmou "
                    "o sucesso da operação."
                    if sucesso
                    else
                    "A ferramenta indicou "
                    "que a operação não teve sucesso."
                ),
                details={
                    "result_type": "dict",
                    "status": status,
                    "explicit_success":
                        success_values,
                },
            )

        # ----------------------------------------------------
        # STATUS DE SUCESSO
        # ----------------------------------------------------

        if status_success:

            return VerificationResult(
                success=True,
                message=(
                    "O status da ferramenta "
                    "indica conclusão."
                ),
                details={
                    "result_type": "dict",
                    "status": status,
                },
            )

        # ----------------------------------------------------
        # RESULTADO COM DADOS
        # ----------------------------------------------------

        return VerificationResult(
            success=True,
            message=(
                "Resultado recebido "
                "com dados válidos."
            ),
            details={
                "result_type": "dict",
                "keys":
                    list(result.keys()),
                "status":
                    status or None,
            },
        )

    # ========================================================
    # TEXTO DE ERRO
    # ========================================================

    @staticmethod
    def _text_indicates_failure(
        text: str,
    ) -> bool:
        """
        Detecta mensagens textuais que indicam falha.
        """

        texto = str(
            text
        ).lower()

        palavras = (
            "erro:",
            "error:",
            "exception:",
            "failed",
            "failure",
            "falhou",
            "não foi possível",
            "nao foi possivel",
            "não foi possível gerar",
            "nao foi possivel gerar",
            "traceback",
        )

        return any(
            palavra in texto
            for palavra in palavras
        )

    # ========================================================
    # VERIFICAÇÃO DE ETAPA
    # ========================================================

    def verify_step(
        self,
        context: TaskContext,
        step_id: int,
    ) -> VerificationResult:
        """
        Verifica o resultado de uma etapa específica.
        """

        step = self._get_step(
            context,
            step_id,
        )

        status = step.get(
            "status"
        )

        # ----------------------------------------------------
        # ETAPA NÃO CONCLUÍDA
        # ----------------------------------------------------

        if status != "completed":

            return VerificationResult(
                success=False,
                message=(
                    f"A etapa {step_id} não está "
                    "marcada como concluída."
                ),
                details={
                    "step_id": step_id,
                    "status": status,
                },
            )

        # ----------------------------------------------------
        # VERIFICAR RESULTADO
        # ----------------------------------------------------

        result = step.get(
            "result"
        )

        verification = self.verify_result(
            result
        )

        verification.details.setdefault(
            "step_id",
            step_id,
        )

        return verification

    # ========================================================
    # VERIFICAÇÃO DO CONTEXTO
    # ========================================================

    def verify_context(
        self,
        context: TaskContext,
    ) -> Dict[str, Any]:
        """
        Verifica o estado geral da tarefa.
        """

        checks: List[Dict[str, Any]] = []

        # ----------------------------------------------------
        # PLANO VAZIO
        # ----------------------------------------------------

        if not context.plan:

            return {
                "success": False,
                "status": "verification_failed",
                "checks": [],
                "errors": context.errors,
                "message": (
                    "A tarefa não possui etapas "
                    "para verificar."
                ),
            }

        # ----------------------------------------------------
        # VERIFICAR CADA ETAPA
        # ----------------------------------------------------

        for step in context.plan:

            step_id = step.get(
                "id"
            )

            try:

                verification = self.verify_step(
                    context,
                    step_id,
                )

                checks.append(
                    {
                        "step_id": step_id,
                        **verification.to_dict(),
                    }
                )

            except Exception as exc:

                checks.append(
                    {
                        "step_id": step_id,
                        "success": False,
                        "message": (
                            "Erro ao verificar etapa."
                        ),
                        "details": {
                            "error":
                                str(exc),
                        },
                    }
                )

        # ----------------------------------------------------
        # RESULTADO FINAL
        # ----------------------------------------------------

        todos_sucesso = bool(
            checks
        ) and all(
            check.get(
                "success",
                False,
            )
            for check in checks
        )

        sem_erros = not context.has_errors()

        success = (
            todos_sucesso
            and sem_erros
        )

        return {
            "success": success,

            "status": (
                "verified"
                if success
                else
                "verification_failed"
            ),

            "checks": checks,

            "errors": context.errors,

            "summary": {
                "total_steps":
                    len(context.plan),

                "verified_steps":
                    sum(
                        1
                        for check in checks
                        if check.get(
                            "success",
                            False,
                        )
                    ),

                "failed_steps":
                    sum(
                        1
                        for check in checks
                        if not check.get(
                            "success",
                            False,
                        )
                    ),

                "context_errors":
                    len(context.errors),
            },
        }

    # ========================================================
    # LOCALIZAR ETAPA
    # ========================================================

    @staticmethod
    def _get_step(
        context: TaskContext,
        step_id: int,
    ) -> Dict[str, Any]:
        """
        Localiza uma etapa pelo ID.
        """

        for step in context.plan:

            if step.get(
                "id"
            ) == step_id:

                return step

        raise KeyError(
            f"Etapa {step_id} não encontrada."
        )


# ============================================================
# INSTÂNCIA PADRÃO
# ============================================================

verifier = ResultVerifier()


__all__ = [
    "VerificationResult",
    "ResultVerifier",
    "verifier",
]
