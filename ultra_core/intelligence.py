# ============================================================
# 🧠 ULTRA IA — INTELLIGENCE BRIDGE
# Ponte entre o Ultra Core e o modelo de linguagem
# ============================================================

import json
import logging
from typing import Any, Optional

from .context import TaskContext

log = logging.getLogger("ultra_ia")

LIMITE_RESULTADO = 6000


def _texto(valor: Any, limite: int = LIMITE_RESULTADO) -> str:
    """Converte um resultado de ferramenta em texto limpo e curto."""

    if isinstance(valor, str):
        texto = valor
    else:
        try:
            texto = json.dumps(valor, ensure_ascii=False, indent=1, default=str)
        except Exception:
            texto = str(valor)

    texto = texto.strip()

    if len(texto) > limite:
        texto = texto[:limite] + "\n[...resultado cortado por tamanho...]"

    return texto


class UltraIntelligence:
    """
    Monta o prompt final do modelo de linguagem.

    Regras desta versão:
    - histórico e arquivo entram em seções próprias;
    - só resultados de ferramentas que funcionaram entram no prompt;
    - erros técnicos ficam apenas no registro interno (log).
    """

    def build_context(self, context: TaskContext) -> dict:
        return {
            "user_request": context.user_request,
            "status": context.status,
            "plan": context.plan,
            "tool_results": context.tool_results,
            "errors": context.errors,
            "metadata": context.metadata,
        }

    CAMPOS_INTERNOS = ("consulta", "pergunta", "tool", "provider", "quantidade")

    def _resultado_valido(self, resultado: Any) -> bool:
        """Falha interna da ferramenta (success False / erro) não é resultado."""

        if not resultado:
            return False

        if isinstance(resultado, dict):
            if resultado.get("success") is False:
                return False

            if resultado.get("erro") or resultado.get("error"):
                if not (resultado.get("resultados") or resultado.get("fontes")):
                    return False

        return True

    def _limpar_resultado(self, resultado: Any) -> Any:
        if isinstance(resultado, dict):
            return {
                k: v
                for k, v in resultado.items()
                if k not in self.CAMPOS_INTERNOS
                and k not in ("erro", "error", "success")
            }

        return resultado

    def _resultados_validos(self, context: TaskContext) -> list:
        validos = []

        for item in context.tool_results:
            if item.get("success") and self._resultado_valido(item.get("result")):
                validos.append(item)

        return validos

    def build_prompt(self, context: TaskContext) -> str:
        historico = context.get_metadata("history", "") or ""
        arquivo = context.get_metadata("file_context", "") or ""
        nome_arquivo = context.get_metadata("file_name", "") or ""

        resultados = self._resultados_validos(context)

        # Erros técnicos vão só para o log, nunca para o modelo.
        for erro in context.errors:
            log.warning("ultra_core erro: %s", erro)

        partes = [
            "Você é a Ultra IA, uma assistente inteligente, "
            "simpática e objetiva.\n"
            "Responda sempre em português do Brasil.\n"
            "Nunca mencione ferramentas, planos, tarefas internas, "
            "erros técnicos ou caminhos de arquivos do sistema, "
            "a menos que o usuário pergunte sobre isso.\n"
            "Se for apenas uma saudação ou conversa simples, "
            "responda de forma curta e natural.\n"
        ]

        if historico:
            partes.append(
                "CONVERSA ANTERIOR (apenas contexto, não responda a ela):\n"
                f"{historico}\n"
            )

        if arquivo:
            titulo = "ARQUIVO ENVIADO"

            if nome_arquivo:
                titulo += f" ({nome_arquivo})"

            partes.append(f"{titulo}:\n{_texto(arquivo, 12000)}\n")

        if resultados:
            blocos = []

            for item in resultados:
                blocos.append(
                    f"[{item.get('tool', 'ferramenta')}]\n"
                    f"{_texto(self._limpar_resultado(item.get('result')))}"
                )

            partes.append(
                "RESULTADOS OBTIDOS (use como base da resposta):\n"
                + "\n\n".join(blocos)
                + "\n\n"
                "Regras para estes resultados:\n"
                "- Não invente fatos, fontes, títulos ou URLs.\n"
                "- Preserve as URLs exatamente como fornecidas.\n"
                "- Se a resposta depender de pesquisa na internet, "
                "termine com uma seção curta 'Fontes utilizadas' "
                "com as fontes realmente fornecidas.\n"
                "- Se houver divergência entre fontes, avise.\n"
            )

        if context.tool_results and not resultados:
            partes.append(
                "AVISO: não foi possível obter dados externos agora "
                "(por exemplo, uma pesquisa). Responda com o que você "
                "sabe e diga de forma breve e simples que não conseguiu "
                "buscar informações atualizadas, sem detalhes técnicos.\n"
            )

        partes.append(
            "PERGUNTA ATUAL DO USUÁRIO (responda somente a esta):\n"
            f"{context.user_request}\n"
        )

        return "\n".join(partes)

    def generate_response(
        self,
        context: TaskContext,
        gemini_bridge: Optional[Any] = None,
    ) -> str:
        prompt = self.build_prompt(context)

        if gemini_bridge is None:
            return ""

        try:
            resposta = gemini_bridge.gerar_resposta(prompt)
            return resposta or ""

        except Exception as exc:
            context.add_error(
                source="gemini_bridge",
                message="Erro ao gerar resposta com Gemini",
                details=str(exc),
            )
            return ""


intelligence = UltraIntelligence()
