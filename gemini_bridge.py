# ============================================================
# ALEX IA ULTRA — GEMINI BRIDGE
# Ponte entre o Ultra Core e o Google GenAI
# ============================================================

from typing import Optional

from google import genai


class GeminiBridge:
    """
    Ponte opcional entre o Ultra Core e o Gemini.

    O Ultra Core continua funcionando mesmo quando
    o Gemini não estiver disponível.
    """

    def __init__(self, api_key: str, model: str = "gemini-3.1-flash-lite"):
        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def gerar_resposta(self, prompt: str) -> str:
        """
        Envia um prompt para o Gemini e retorna o texto.
        """

        resposta = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return getattr(resposta, "text", "") or ""


def criar_gemini_bridge(
    api_key: Optional[str],
    model: str = "gemini-3.1-flash-lite",
):
    """
    Cria a ponte somente quando existe uma chave válida.
    """

    if not api_key:
        return None

    try:
        return GeminiBridge(
            api_key=api_key,
            model=model,
        )
    except Exception:
        return None
