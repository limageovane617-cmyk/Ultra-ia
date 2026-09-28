# ============================================================
# 🧠 ALEX IA ULTRA — INTERPRETER
# Interpretador de linguagem natural do Ultra Core
# ============================================================

from typing import Any, Dict, List


class TaskInterpreter:
    """
    Interpretador central da Alex IA Ultra.

    Responsabilidades:

    - normalizar o pedido do usuário;
    - identificar a intenção;
    - extrair palavras-chave;
    - extrair o prompt principal;
    - sugerir ferramentas;
    - preparar informações para o Brain e Planner.

    O Interpreter não executa ferramentas.
    Ele apenas entende o pedido.
    """

    # ========================================================
    # NORMALIZAÇÃO
    # ========================================================

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normaliza o texto para facilitar a interpretação.
        """

        return " ".join(
            str(text or "")
            .lower()
            .strip()
            .split()
        )

    # ========================================================
    # DETECÇÃO DE INTENÇÃO
    # ========================================================

    def detect_intent(
        self,
        user_request: str,
    ) -> Dict[str, Any]:
        """
        Detecta a intenção principal do usuário.
        """

        texto = self.normalize_text(
            user_request
        )

        if not texto:
            return {
                "intent": "unknown",
                "keywords": [],
                "confidence": 0.0,
                "suggested_tools": [],
            }

        categorias = {
            "internet": [
                "pesquisar",
                "pesquise",
                "pesquisa",
                "buscar",
                "busque",
                "procure",
                "internet",
                "google",
                "notícia",
                "noticias",
                "notícia",
                "informação atual",
                "informacoes atuais",
                "informações atuais",
            ],

            "imagem": [
                "imagem",
                "imagens",
                "foto",
                "fotografia",
                "desenho",
                "ilustração",
                "ilustracao",
                "picture",
                "image",
                "gerar imagem",
                "criar imagem",
                "fazer imagem",
            ],

            "video": [
                "vídeo",
                "video",
                "vídeos",
                "videos",
                "filme",
                "animação",
                "animacao",
                "clipe",
                "clip",
                "gerar vídeo",
                "gerar video",
                "criar vídeo",
                "criar video",
                "animar",
            ],

            "texto": [
                "texto",
                "escrever",
                "escreva",
                "redigir",
                "resumo",
                "resumir",
                "explicar",
                "explicação",
                "explicacao",
                "traduzir",
                "tradução",
                "traducao",
            ],

            "codigo": [
                "código",
                "codigo",
                "programar",
                "programação",
                "programacao",
                "python",
                "javascript",
                "typescript",
                "função",
                "funcao",
                "arquivo",
                "script",
                "classe",
                "bug",
                "erro",
                "corrigir código",
                "corrigir codigo",
            ],
        }

        encontrados: Dict[str, int] = {}

        for categoria, palavras in categorias.items():

            quantidade = sum(
                1
                for palavra in palavras
                if palavra in texto
            )

            if quantidade > 0:
                encontrados[categoria] = quantidade

        if not encontrados:
            return {
                "intent": "geral",
                "keywords": self.extract_keywords(
                    texto
                ),
                "confidence": 0.40,
                "suggested_tools": [],
            }

        # ----------------------------------------------------
        # Escolhe a intenção com maior quantidade de sinais.
        # ----------------------------------------------------

        intent = max(
            encontrados,
            key=encontrados.get,
        )

        quantidade = encontrados[intent]

        confidence = min(
            0.55 + (
                quantidade * 0.10
            ),
            0.98,
        )

        suggested_tools = (
            self.suggest_tools(intent)
        )

        keywords = self.build_keywords(
            texto,
            intent,
        )

        return {
            "intent": intent,
            "keywords": keywords,
            "confidence": confidence,
            "suggested_tools": suggested_tools,
        }

    # ========================================================
    # PALAVRAS-CHAVE
    # ========================================================

    @staticmethod
    def extract_keywords(
        text: str,
        limit: int = 10,
    ) -> List[str]:
        """
        Extrai palavras relevantes do pedido.
        """

        palavras = []

        for palavra in text.split():

            palavra = (
                palavra
                .strip(
                    ".,!?;:()[]{}\"'"
                )
            )

            if len(palavra) < 4:
                continue

            if palavra not in palavras:
                palavras.append(
                    palavra
                )

            if len(palavras) >= limit:
                break

        return palavras

    # ========================================================
    # KEYWORDS POR INTENÇÃO
    # ========================================================

    def build_keywords(
        self,
        text: str,
        intent: str,
    ) -> List[str]:
        """
        Cria palavras-chave úteis para o Router.
        """

        keywords = []

        mapas = {
            "internet": [
                "internet",
                "pesquisa",
                "google",
                "buscar",
            ],

            "imagem": [
                "imagem",
                "image",
                "foto",
                "gerar",
            ],

            "video": [
                "video",
                "vídeo",
                "gerar",
                "animar",
            ],

            "texto": [
                "texto",
                "escrever",
                "gerar",
            ],

            "codigo": [
                "codigo",
                "código",
                "python",
                "programar",
            ],
        }

        keywords.extend(
            mapas.get(
                intent,
                [],
            )
        )

        # Adiciona palavras do pedido.
        keywords.extend(
            self.extract_keywords(
                text,
                limit=6,
            )
        )

        # Remove duplicadas.
        resultado = []

        for keyword in keywords:

            keyword = (
                str(keyword)
                .strip()
                .lower()
            )

            if (
                keyword
                and keyword not in resultado
            ):
                resultado.append(
                    keyword
                )

        return resultado[:12]

    # ========================================================
    # EXTRAÇÃO DO PROMPT
    # ========================================================

    def extract_prompt(
        self,
        user_request: str,
    ) -> str:
        """
        Extrai o conteúdo principal do pedido.

        Remove comandos comuns do começo,
        mas preserva o restante da solicitação.
        """

        texto = str(
            user_request or ""
        ).strip()

        if not texto:
            return ""

        prefixos = [
            # Imagem
            "gerar uma imagem de ",
            "gerar uma imagem ",
            "criar uma imagem de ",
            "criar uma imagem ",
            "fazer uma imagem de ",
            "fazer uma imagem ",
            "gere uma imagem de ",
            "gere uma imagem ",
            "crie uma imagem de ",
            "crie uma imagem ",

            # Vídeo
            "gerar um vídeo de ",
            "gerar um vídeo ",
            "gerar um video de ",
            "gerar um video ",
            "criar um vídeo de ",
            "criar um vídeo ",
            "criar um video de ",
            "criar um video ",
            "gere um vídeo de ",
            "gere um vídeo ",
            "gere um video de ",
            "gere um video ",
            "animar ",

            # Internet
            "pesquisar sobre ",
            "pesquisar ",
            "pesquise sobre ",
            "pesquise ",
            "buscar sobre ",
            "buscar ",
            "busque sobre ",
            "busque ",
            "procurar sobre ",
            "procurar ",
            "procure sobre ",
            "procure ",

            # Texto
            "escrever sobre ",
            "escreva sobre ",
            "criar um texto sobre ",
            "criar um texto ",
            "fazer um texto sobre ",
            "fazer um texto ",

            # Código
            "criar código para ",
            "criar codigo para ",
            "escrever código para ",
            "escrever codigo para ",
        ]

        texto_lower = texto.lower()

        for prefixo in prefixos:

            if texto_lower.startswith(
                prefixo
            ):

                return texto[
                    len(prefixo):
                ].strip()

        return texto

    # ========================================================
    # SUGESTÃO DE FERRAMENTAS
    # ========================================================

    @staticmethod
    def suggest_tools(
        intent: str,
    ) -> List[str]:
        """
        Sugere nomes de ferramentas para o Router.
        """

        ferramentas = {
            "internet": [
               "pesquisa_internet",
            ],

            "imagem": [
                "imagem.gerar",
                "gerar_imagem",
                "image.generate",
                "image_generator",
            ],

            "video": [
                "video.gerar",
                "video.texto",
                "video.imagem",
                "video.fallback",
                "gerar_video",
            ],

            "texto": [
                "texto.gerar",
                "text.gerar",
                "gerar_texto",
            ],

            "codigo": [
                "codigo.gerar",
                "codigo.executar",
                "python.executar",
                "code.execute",
            ],

            "geral": [],
        }

        return ferramentas.get(
            intent,
            [],
        )

    # ========================================================
    # INTERPRETAÇÃO COMPLETA
    # ========================================================

    def interpret(
        self,
        user_request: str,
    ) -> Dict[str, Any]:
        """
        Executa a interpretação completa.
        """

        if not user_request or not str(
            user_request
        ).strip():

            return {
                "success": False,
                "intent": "unknown",
                "keywords": [],
                "confidence": 0.0,
                "prompt": "",
                "suggested_tools": [],
                "message": (
                    "A solicitação do usuário "
                    "está vazia."
                ),
            }

        detected = self.detect_intent(
            user_request
        )

        prompt = self.extract_prompt(
            user_request
        )

        return {
            "success": True,
            "intent": detected["intent"],
            "keywords": detected["keywords"],
            "confidence": detected["confidence"],
            "prompt": prompt,
            "suggested_tools": detected[
                "suggested_tools"
            ],
            "original_request": str(
                user_request
            ).strip(),
        }


# ============================================================
# INSTÂNCIA PADRÃO
# ============================================================

interpreter = TaskInterpreter()


__all__ = [
    "TaskInterpreter",
    "interpreter",
]
