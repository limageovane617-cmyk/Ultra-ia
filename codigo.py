# ============================================================
# 💻 ALEX IA ULTRA — SISTEMA DE CÓDIGO
# Criada por Geovani
# ============================================================


LINGUAGENS_SUPORTADAS = [
    "Python",
    "JavaScript",
    "HTML",
    "CSS",
    "SQL",
    "JSON",
    "Bash"
]


def preparar_pedido_codigo(
    pedido,
    linguagem="Python"
):
    """
    Prepara uma solicitação de programação
    para a Alex IA.
    """

    if not pedido or not pedido.strip():
        return None

    if linguagem not in LINGUAGENS_SUPORTADAS:
        linguagem = "Python"

    prompt = f"""
Você é especialista em programação.

Linguagem principal:
{linguagem}

Pedido do usuário:
{pedido.strip()}

Regras:

- Analise o pedido antes de escrever o código.
- Gere código organizado e legível.
- Explique as partes importantes.
- Evite erros de sintaxe.
- Quando corrigir código existente, preserve o que já funciona.
- Se faltar alguma informação importante, deixe isso claro.
- Sempre responda em português do Brasil.
"""

    return prompt.strip()


def analisar_codigo(codigo, linguagem="Python"):
    """
    Prepara um código para análise.
    """

    if not codigo or not codigo.strip():
        return None

    if linguagem not in LINGUAGENS_SUPORTADAS:
        linguagem = "Python"

    prompt = f"""
Analise o código abaixo.

Linguagem:
{linguagem}

Código:

{codigo}

Verifique:

- erros de sintaxe
- possíveis erros de lógica
- problemas de organização
- possíveis melhorias
- segurança
- compatibilidade

Explique os problemas de forma clara
e apresente as correções quando necessário.
"""

    return prompt.strip()


def listar_linguagens():
    """Retorna as linguagens disponíveis."""

    return LINGUAGENS_SUPORTADAS.copy()
