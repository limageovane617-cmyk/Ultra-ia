# ============================================================
# 🌐 ALEX IA ULTRA — INTERNET
# Pesquisa independente + Wikidata
#
# Google Search/Gemini permanece disponível como mecanismo
# adicional.
#
# Núcleo independente:
#   Wikidata → resolução de entidade → P36 → verificação
#   → seleção da resposta → cache
#
# Criada por Geovani
# ============================================================

from google.genai import types

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote

import json
import os
import time
import unicodedata
import re
import random


# ============================================================
# 🔵 GOOGLE SEARCH
# ============================================================

def configurar_pesquisa_google():
    """
    Configura a ferramenta de pesquisa do Google para o Gemini.

    Retorna:
        Configuração da ferramenta de busca.
    """

    return types.Tool(
        google_search=types.GoogleSearch()
    )


# ============================================================
# 🔵 PREPARAR PESQUISA
# ============================================================

def preparar_pesquisa(pergunta):
    """
    Prepara uma pergunta para ser pesquisada na internet.
    """

    if not pergunta or not pergunta.strip():
        return None

    return f"""
Pesquise na internet informações atuais para responder
à pergunta abaixo.

Pergunta do usuário:
{pergunta.strip()}

Regras:

- Use informações encontradas na pesquisa.
- Priorize informações atuais e confiáveis.
- Responda em português do Brasil.
- Seja clara e objetiva.
- Não invente informações.
- Se houver informações conflitantes, explique.
- Quando possível, considere as fontes encontradas.
"""


# ============================================================
# 🔵 EXTRAIR FONTES DO GEMINI
# ============================================================

def extrair_fontes(resposta):
    """
    Tenta extrair as fontes utilizadas pelo Gemini.
    """

    fontes = []

    try:

        candidatos = resposta.candidates

        if not candidatos:
            return fontes

        grounding_metadata = (
            candidatos[0].grounding_metadata
        )

        if not grounding_metadata:
            return fontes

        chunks = grounding_metadata.grounding_chunks

        if not chunks:
            return fontes

        for chunk in chunks:

            if hasattr(chunk, "web") and chunk.web:

                uri = getattr(
                    chunk.web,
                    "uri",
                    None
                )

                if uri and uri not in fontes:
                    fontes.append(uri)

    except Exception:
        pass

    return fontes


# ============================================================
# 🔵 DUCKDUCKGO LITE
# ============================================================

def pesquisar_web(pergunta, limite=5, timeout=15):
    """
    Pesquisa web usando DuckDuckGo Lite.

    Mantida por compatibilidade com versões anteriores.
    """

    if not pergunta or not pergunta.strip():

        return {
            "success": False,
            "provider": "duckduckgo_lite",
            "erro": "Pergunta vazia.",
            "resultados": [],
            "fontes": [],
            "quantidade": 0,
        }

    try:

        resposta = requests.get(
            "https://lite.duckduckgo.com/lite/",
            params={
                "q": pergunta.strip()
            },
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=timeout,
        )

        resposta.raise_for_status()

        soup = BeautifulSoup(
            resposta.text,
            "html.parser"
        )

        resultados = []
        fontes = []

        for link in soup.find_all("a"):

            href = link.get("href")

            titulo = link.get_text(
                " ",
                strip=True
            )

            if not href:
                continue

            if "uddg=" not in href:
                continue

            if not titulo:
                continue

            if href.startswith("//"):
                href = "https:" + href

            dados = parse_qs(
                urlparse(href).query
            )

            original = next(
                iter(
                    dados.get(
                        "uddg",
                        []
                    )
                ),
                None
            )

            if not original:
                continue

            url_original = unquote(original)

            if url_original in fontes:
                continue

            resultados.append({
                "titulo": titulo,
                "url": url_original,
            })

            fontes.append(url_original)

            if len(resultados) >= limite:
                break

        if not resultados:

            return {
                "success": False,
                "provider": "duckduckgo_lite",
                "pergunta": pergunta.strip(),
                "resultados": [],
                "fontes": [],
                "quantidade": 0,
                "erro": (
                    "Nenhum resultado encontrado "
                    "na pesquisa web."
                ),
            }

        return {
            "success": True,
            "provider": "duckduckgo_lite",
            "pergunta": pergunta.strip(),
            "resultados": resultados,
            "fontes": fontes,
            "quantidade": len(resultados),
            "erro": None,
        }

    except Exception as erro:

        return {
            "success": False,
            "provider": "duckduckgo_lite",
            "pergunta": pergunta.strip(),
            "resultados": [],
            "fontes": [],
            "quantidade": 0,
            "erro": str(erro),
        }


# ============================================================
# 🟣 WIKIDATA — CONFIGURAÇÃO
# ============================================================

WIKIDATA_API = (
    "https://www.wikidata.org/w/api.php"
)

WIKIDATA_HEADERS = {
    "User-Agent": (
        "AlexIAUltra/1.0 "
        "(Internet Engine; "
        "research tool)"
    )
}


# ============================================================
# 💾 CACHE
# ============================================================

if os.path.isdir("/kaggle/working"):

    WIKIDATA_CACHE = (
        "/kaggle/working/wikidata_cache.json"
    )

else:

    WIKIDATA_CACHE = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "wikidata_cache.json"
    )


def _normalizar_texto(texto):
    """
    Normalização básica.
    """

    if not texto:
        return ""

    texto = str(texto)

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )

    texto = texto.lower()

    texto = re.sub(
        r"\s+",
        " ",
        texto
    ).strip()

    return texto


def _normalizar_texto_v2(texto):
    """
    Normalização robusta usada pelo Internet Engine V3.

    Remove:
    - acentos
    - pontuação
    - espaços duplicados

    Exemplo:

        "Qual é a capital do Canadá?"
        →
        "qual e a capital do canada"
    """

    if not texto:
        return ""

    texto = str(texto)

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )

    texto = texto.lower()

    texto = re.sub(
        r"[^\w\s]",
        " ",
        texto
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    ).strip()

    return texto


def _carregar_cache_wikidata():

    if not os.path.exists(
        WIKIDATA_CACHE
    ):
        return {}

    try:

        with open(
            WIKIDATA_CACHE,
            "r",
            encoding="utf-8"
        ) as arquivo:

            dados = json.load(
                arquivo
            )

            if isinstance(
                dados,
                dict
            ):
                return dados

    except Exception:
        pass

    return {}


def _salvar_cache_wikidata(cache):

    try:

        pasta = os.path.dirname(
            WIKIDATA_CACHE
        )

        if pasta:

            os.makedirs(
                pasta,
                exist_ok=True
            )

        with open(
            WIKIDATA_CACHE,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                cache,
                arquivo,
                ensure_ascii=False,
                indent=2
            )

        return True

    except Exception:
        return False


# ============================================================
# 🛡️ REQUISIÇÃO ROBUSTA WIKIDATA
# ============================================================

def _requisicao_wikidata(
    parametros,
    tentativas=5,
    timeout=20
):
    """
    Consulta Wikidata com retry/backoff.

    Trata:
    - 429
    - 500
    - 502
    - 503
    - 504
    - falhas temporárias de rede
    """

    parametros = dict(parametros)

    parametros.setdefault(
        "maxlag",
        "5"
    )

    for tentativa in range(
        1,
        tentativas + 1
    ):

        try:

            resposta = requests.get(
                WIKIDATA_API,
                params=parametros,
                headers=WIKIDATA_HEADERS,
                timeout=timeout
            )

            print(
                f"HTTP {resposta.status_code} "
                f"(tentativa {tentativa})"
            )

            # ------------------------------------------------
            # RATE LIMIT
            # ------------------------------------------------

            if resposta.status_code == 429:

                if tentativa >= tentativas:
                    return None

                retry_after = (
                    resposta.headers.get(
                        "Retry-After"
                    )
                )

                try:

                    if retry_after:

                        espera = float(
                            retry_after
                        )

                    else:

                        espera = (
                            4 * (2 ** (tentativa - 1))
                        )

                except Exception:

                    espera = (
                        4 * (2 ** (tentativa - 1))
                    )

                espera += random.uniform(
                    0.5,
                    1.5
                )

                print(
                    f"⏳ Wikidata limitou a consulta. "
                    f"Aguardando {espera:.1f}s..."
                )

                time.sleep(
                    espera
                )

                continue

            # ------------------------------------------------
            # ERROS TEMPORÁRIOS
            # ------------------------------------------------

            if resposta.status_code in (
                500,
                502,
                503,
                504
            ):

                if tentativa >= tentativas:
                    return None

                espera = (
                    4 * (2 ** (tentativa - 1))
                )

                espera += random.uniform(
                    0.5,
                    1.5
                )

                print(
                    f"⏳ Erro temporário. "
                    f"Nova tentativa em {espera:.1f}s..."
                )

                time.sleep(
                    espera
                )

                continue

            resposta.raise_for_status()

            return resposta.json()

        except Exception as erro:

            if tentativa >= tentativas:

                print(
                    "❌ Erro Wikidata:",
                    erro
                )

                return None

            espera = (
                4 * (2 ** (tentativa - 1))
            )

            espera += random.uniform(
                0.5,
                1.5
            )

            print(
                f"⏳ Falha temporária. "
                f"Nova tentativa em {espera:.1f}s..."
            )

            time.sleep(
                espera
            )

    return None


# ============================================================
# 🔎 BUSCAR ENTIDADES
# ============================================================

def _buscar_entidade_wikidata(
    nome,
    limite=10
):
    """
    Pesquisa entidades no Wikidata.

    Retorna resultados brutos da busca.
    """

    if not nome:
        return []

    dados = _requisicao_wikidata(
        {
            "action": "wbsearchentities",
            "search": nome,
            "language": "pt",
            "uselang": "pt",
            "format": "json",
            "limit": str(limite)
        }
    )

    if not dados:
        return []

    return dados.get(
        "search",
        []
    )


# ============================================================
# 🎯 EXTRAIR PAÍS DA PERGUNTA — V3
# ============================================================

def _extrair_pais_da_pergunta_v3(
    pergunta
):
    """
    Extrai o nome provável do país diretamente
    da estrutura da pergunta.

    Exemplos:

        Qual é a capital do Brasil?
        → brasil

        Me diga a capital da França.
        → franca

        Você sabe qual é a capital do Japão?
        → japao

        capital do Canadá
        → canada
    """

    texto = _normalizar_texto_v2(
        pergunta
    )

    if not texto:
        return None

    # --------------------------------------------------------
    # PADRÕES PRINCIPAIS
    # --------------------------------------------------------

    padroes = [
        r"capital\s+de\s+(.+)",
        r"capital\s+do\s+(.+)",
        r"capital\s+da\s+(.+)",
        r"capital\s+dos\s+(.+)",
        r"capital\s+das\s+(.+)",
    ]

    trecho = None

    for padrao in padroes:

        encontrado = re.search(
            padrao,
            texto
        )

        if encontrado:

            trecho = encontrado.group(
                1
            ).strip()

            break

    # --------------------------------------------------------
    # LIMPEZA
    # --------------------------------------------------------

    if trecho:

        trecho = re.sub(
            r"\b(hoje|atual|atualmente)\b",
            " ",
            trecho
        )

        trecho = re.sub(
            r"\b(para mim|por favor|me diga)\b",
            " ",
            trecho
        )

        trecho = re.sub(
            r"\s+",
            " ",
            trecho
        ).strip()

        if trecho:
            return trecho

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    palavras_remover = {
        "qual",
        "e",
        "a",
        "o",
        "uma",
        "um",
        "capital",
        "de",
        "do",
        "da",
        "dos",
        "das",
        "voce",
        "sabe",
        "me",
        "diga",
        "onde",
        "fica",
        "por",
        "favor",
        "qual",
        "é",
        "onde",
    }

    palavras = texto.split()

    restantes = [
        palavra
        for palavra in palavras
        if palavra not in palavras_remover
    ]

    if not restantes:
        return None

    return " ".join(
        restantes
    )


# ============================================================
# 🌎 IDENTIFICAR PAÍS
# ============================================================

def _identificar_pais(
    pergunta
):
    """
    Resolve o país da pergunta usando Wikidata.

    Utiliza pontuação para evitar confundir:

        França
        Franca
        Cidade
        pessoa
        evento
        empresa

    com o país verdadeiro.
    """

    nome_pais = (
        _extrair_pais_da_pergunta_v3(
            pergunta
        )
    )

    if not nome_pais:
        return None

    print(
        f"🎯 Possível país extraído: "
        f"'{nome_pais}'"
    )

    candidatos = _buscar_entidade_wikidata(
        nome_pais,
        limite=10
    )

    if not candidatos:
        return None

    candidatos_avaliados = []

    indicadores_pais = {
        "pais",
        "country",
        "estado soberano",
        "sovereign state",
        "republica",
        "república"
    }

    indicadores_nao_pais = {
        "cidade",
        "city",
        "comuna",
        "municipio",
        "município",
        "empresa",
        "filme",
        "musica",
        "música",
        "pessoa",
        "jogador",
        "jogadora",
        "livro",
        "evento",
        "clube",
        "universidade",
        "provincia",
        "província",
        "estado",
        "regiao",
        "região"
    }

    nome_normalizado = (
        _normalizar_texto_v2(
            nome_pais
        )
    )

    for candidato in candidatos:

        label = candidato.get(
            "label",
            ""
        )

        descricao = candidato.get(
            "description",
            ""
        )

        label_normalizado = (
            _normalizar_texto_v2(
                label
            )
        )

        descricao_normalizada = (
            _normalizar_texto_v2(
                descricao
            )
        )

        score = 0

        # ----------------------------------------------------
        # LABEL EXATO
        # ----------------------------------------------------

        if (
            label_normalizado
            == nome_normalizado
        ):
            score += 50

        # ----------------------------------------------------
        # DESCRIÇÃO INDICA PAÍS
        # ----------------------------------------------------

        for indicador in indicadores_pais:

            if indicador in descricao_normalizada:
                score += 30
                break

        # ----------------------------------------------------
        # EVITAR ENTIDADES NÃO-PAÍS
        # ----------------------------------------------------

        for indicador in indicadores_nao_pais:

            if indicador in descricao_normalizada:
                score -= 50
                break

        candidatos_avaliados.append(
            {
                "id": candidato.get("id"),
                "label": label,
                "description": descricao,
                "score": score
            }
        )

    candidatos_avaliados.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    for candidato in candidatos_avaliados:

        print(
            f"   {candidato['id']:<10} "
            f"{candidato['label']:<35} "
            f"score={candidato['score']}"
        )

    # --------------------------------------------------------
    # EXIGIR CONFIANÇA MÍNIMA
    # --------------------------------------------------------

    melhor = (
        candidatos_avaliados[0]
        if candidatos_avaliados
        else None
    )

    if not melhor:
        return None

    if melhor["score"] < 50:
        return None

    return melhor


# ============================================================
# 📦 OBTER DESCRIÇÕES DE VÁRIAS ENTIDADES
# ============================================================

def _obter_descricoes(
    ids
):
    """
    Obtém labels e descrições de várias entidades
    em uma única chamada.
    """

    if not ids:
        return {}

    ids = list(
        dict.fromkeys(
            ids
        )
    )

    dados = _requisicao_wikidata(
        {
            "action": "wbgetentities",
            "ids": "|".join(ids),
            "props": "labels|descriptions",
            "languages": "pt|en",
            "format": "json"
        }
    )

    if not dados:
        return {}

    entidades = dados.get(
        "entities",
        {}
    )

    resultado = {}

    for qid, entidade in entidades.items():

        labels = entidade.get(
            "labels",
            {}
        )

        descriptions = entidade.get(
            "descriptions",
            {}
        )

        nome = (
            labels.get(
                "pt",
                {}
            ).get("value")
            or labels.get(
                "en",
                {}
            ).get("value")
            or qid
        )

        descricao = (
            descriptions.get(
                "pt",
                {}
            ).get("value")
            or descriptions.get(
                "en",
                {}
            ).get("value")
            or ""
        )

        resultado[qid] = {
            "label": nome,
            "description": descricao
        }

    return resultado


# ============================================================
# 🛡️ SELECIONAR CAPITAL
# ============================================================

def _selecionar_capital(
    candidatos,
    pais
):
    """
    Seleciona a capital atual entre os candidatos P36.

    Pontuação:

    +60  capital nacional/federal do país
    -70  capital estadual/regional/subnacional
    -25  indicação histórica
    """

    if not candidatos:
        return None

    pais_normalizado = (
        _normalizar_texto_v2(
            pais
        )
    )

    avaliados = []

    padroes_nacionais = [
        "capital do " + pais_normalizado,
        "capital da " + pais_normalizado,
        "capital de " + pais_normalizado,
        "capital dos " + pais_normalizado,
        "capital das " + pais_normalizado,
        "capital e maior cidade do " + pais_normalizado,
        "capital e maior cidade da " + pais_normalizado,
        "capital nacional",
        "capital federal",
        "national capital",
        "federal capital",
    ]

    padroes_subnacionais = [
        "capital do estado",
        "capital estadual",
        "capital da regiao",
        "capital regional",
        "state capital",
        "regional capital",
        "capital provincial",
        "provincial capital",
    ]

    padroes_historicos = [
        "antiga capital",
        "antiga capital do",
        "antiga capital da",
        "former capital",
        "historical capital",
        "capital historica",
        "capital histórica",
        "periodo",
        "período",
        "shogunato",
        "shogunate",
    ]

    for candidato in candidatos:

        qid = candidato.get(
            "id"
        )

        nome = candidato.get(
            "label",
            qid
        )

        descricao = candidato.get(
            "description",
            ""
        )

        texto = _normalizar_texto_v2(
            descricao
        )

        score = 0

        # ----------------------------------------------------
        # CAPITAL NACIONAL
        # ----------------------------------------------------

        for padrao in padroes_nacionais:

            if padrao in texto:

                score += 60
                break

        # ----------------------------------------------------
        # CAPITAL SUBNACIONAL
        # ----------------------------------------------------

        for padrao in padroes_subnacionais:

            if padrao in texto:

                score -= 70
                break

        # ----------------------------------------------------
        # CAPITAL HISTÓRICA
        # ----------------------------------------------------

        for padrao in padroes_historicos:

            if padrao in texto:

                score -= 25

        # ----------------------------------------------------
        # VERIFICAÇÃO GENÉRICA
        # ----------------------------------------------------

        if "capital" not in texto:

            score = min(
                score,
                0
            )

        # ----------------------------------------------------
        # PAÍS NA DESCRIÇÃO
        # ----------------------------------------------------

        if (
            pais_normalizado
            and re.search(
                rf"\b{re.escape(pais_normalizado)}\b",
                texto
            )
        ):

            score += 10

        avaliados.append(
            {
                "id": qid,
                "label": nome,
                "description": descricao,
                "score": score
            }
        )

    avaliados.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    for candidato in avaliados:

        print(
            f"   {candidato['id']:<10} "
            f"{candidato['label']:<25} "
            f"score={candidato['score']}"
        )

    # --------------------------------------------------------
    # CAPITAL COM SCORE POSITIVO
    # --------------------------------------------------------

    for candidato in avaliados:

        if candidato["score"] >= 60:

            return candidato

    # --------------------------------------------------------
    # FALLBACK SE HOUVER APENAS UM CANDIDATO
    # --------------------------------------------------------

    if len(avaliados) == 1:

        candidato = avaliados[0]

        texto = _normalizar_texto_v2(
            candidato["description"]
        )

        if "capital" in texto:

            return candidato

    return None


# ============================================================
# 🏛️ OBTER P36 DO PAÍS
# ============================================================

def _obter_capitais_wikidata(
    qid
):
    """
    Obtém os valores P36 de uma entidade.
    """

    dados = _requisicao_wikidata(
        {
            "action": "wbgetentities",
            "ids": qid,
            "props": "claims",
            "format": "json"
        }
    )

    if not dados:
        return []

    entidades = dados.get(
        "entities",
        {}
    )

    entidade = entidades.get(
        qid,
        {}
    )

    claims = entidade.get(
        "claims",
        {}
    )

    valores = claims.get(
        "P36",
        []
    )

    ids_capitais = []

    for claim in valores:

        try:

            valor = (
                claim
                .get("mainsnak", {})
                .get("datavalue", {})
                .get("value", {})
            )

            capital_id = valor.get(
                "id"
            )

            if (
                capital_id
                and capital_id not in ids_capitais
            ):

                ids_capitais.append(
                    capital_id
                )

        except Exception:
            continue

    return ids_capitais


# ============================================================
# 🌐 INTERNET ENGINE V3
# ============================================================

def internet_engine_v3(
    pergunta
):
    """
    Núcleo independente de pesquisa do Alex IA Ultra.

    Fluxo:

        pergunta
            ↓
        extração do país
            ↓
        Wikidata
            ↓
        identificação da entidade
            ↓
        P36
            ↓
        descrições
            ↓
        seleção/verificação
            ↓
        resultado
            ↓
        cache
    """

    print(
        "\n"
        + "=" * 70
    )

    print(
        "🌐 INTERNET ENGINE V3"
    )

    print(
        "=" * 70
    )

    print(
        f"🔎 Pergunta: {pergunta}"
    )

    if not pergunta or not str(
        pergunta
    ).strip():

        return {
            "sucesso": False,
            "success": False,
            "pergunta": pergunta,
            "resultado": None,
            "pais": None,
            "qid": None,
            "descricao": None,
            "fonte": "Wikidata",
            "erro": "Pergunta vazia."
        }

    pergunta = str(
        pergunta
    ).strip()

    # ========================================================
    # 💾 CACHE POR PERGUNTA
    # ========================================================

    cache = _carregar_cache_wikidata()

    chave_pergunta = (
        "pergunta::"
        + _normalizar_texto_v2(
            pergunta
        )
    )

    cache_resultado = cache.get(
        chave_pergunta
    )

    if (
        isinstance(
            cache_resultado,
            dict
        )
        and cache_resultado.get(
            "sucesso"
        )
        and cache_resultado.get(
            "resultado"
        )
    ):

        print(
            "💾 Resultado da pergunta "
            "encontrado no cache."
        )

        return cache_resultado

    # ========================================================
    # 🎯 IDENTIFICAR PAÍS
    # ========================================================

    entidade_pais = _identificar_pais(
        pergunta
    )

    if not entidade_pais:

        resultado = {
            "sucesso": False,
            "success": False,
            "pergunta": pergunta,
            "resultado": None,
            "pais": None,
            "qid": None,
            "descricao": None,
            "fonte": "Wikidata",
            "erro": (
                "Não foi possível identificar "
                "o país da pergunta."
            )
        }

        return resultado

    qid_pais = entidade_pais.get(
        "id"
    )

    nome_pais = entidade_pais.get(
        "label"
    )

    descricao_pais = entidade_pais.get(
        "description",
        ""
    )

    print(
        f"🌎 País identificado: "
        f"{nome_pais} ({qid_pais})"
    )

    # ========================================================
    # 📚 P36
    # ========================================================

    ids_capitais = _obter_capitais_wikidata(
        qid_pais
    )

    print(
        f"📚 Candidatos P36: "
        f"{len(ids_capitais)}"
    )

    if not ids_capitais:

        return {
            "sucesso": False,
            "success": False,
            "pergunta": pergunta,
            "resultado": None,
            "pais": nome_pais,
            "qid": qid_pais,
            "descricao": descricao_pais,
            "fonte": "Wikidata",
            "erro": (
                "Nenhuma capital encontrada "
                "no Wikidata."
            )
        }

    # ========================================================
    # 🔍 DESCRIÇÕES
    # ========================================================

    descricoes = _obter_descricoes(
        ids_capitais
    )

    candidatos = []

    for capital_id in ids_capitais:

        dados = descricoes.get(
            capital_id,
            {}
        )

        candidatos.append(
            {
                "id": capital_id,
                "label": dados.get(
                    "label",
                    capital_id
                ),
                "description": dados.get(
                    "description",
                    ""
                )
            }
        )

    # ========================================================
    # 🧮 SELECIONAR CAPITAL
    # ========================================================

    print(
        "🔍 Avaliando candidatos:"
    )

    capital = _selecionar_capital(
        candidatos,
        nome_pais
    )

    if not capital:

        print(
            "⚠️ Nenhum candidato foi "
            "confirmado como capital atual."
        )

        return {
            "sucesso": False,
            "success": False,
            "pergunta": pergunta,
            "resultado": None,
            "pais": nome_pais,
            "qid": qid_pais,
            "descricao": descricao_pais,
            "fonte": "Wikidata",
            "erro": (
                "Nenhum candidato foi "
                "confirmado como capital atual."
            )
        }

    # ========================================================
    # ✅ RESULTADO
    # ========================================================

    nome_capital = capital.get(
        "label"
    )

    qid_capital = capital.get(
        "id"
    )

    descricao_capital = capital.get(
        "description",
        ""
    )

    resultado = {
        "sucesso": True,
        "success": True,
        "pergunta": pergunta,
        "pais": nome_pais,
        "resultado": nome_capital,
        "qid": qid_capital,
        "descricao": descricao_capital,
        "fonte": "Wikidata",
        "verified": True,
        "erro": None
    }

    print(
        "\n"
        "✅ RESULTADO FINAL"
    )

    print(
        f"   País: {nome_pais}"
    )

    print(
        f"   Capital: {nome_capital}"
    )

    print(
        f"   QID: {qid_capital}"
    )

    # ========================================================
    # 💾 SALVAR SOMENTE RESULTADO VALIDADO
    # ========================================================

    cache[
        chave_pergunta
    ] = resultado

    # Também mantém cache por país,
    # facilitando consultas futuras.

    chave_pais = (
        _normalizar_texto_v2(
            nome_pais
        )
    )

    cache[
        chave_pais
    ] = {
        "success": True,
        "answer": nome_capital,
        "source": "Wikidata",
        "verified": True,
        "qid_pais": qid_pais,
        "qid_capital": qid_capital,
        "descricao": descricao_capital,
        "error": None
    }

    _salvar_cache_wikidata(
        cache
    )

    print(
        "💾 Resultado válido salvo no cache."
    )

    return resultado


# ============================================================
# 🟣 PESQUISAR CAPITAL — INTERFACE COMPATÍVEL
# ============================================================

def pesquisar_capital(
    pais
):
    """
    Interface compatível com a versão anterior.

    Recebe diretamente o nome de um país e utiliza
    o Internet Engine V3.

    Exemplo:

        pesquisar_capital("Brasil")
    """

    if not pais or not str(
        pais
    ).strip():

        return {
            "success": False,
            "answer": None,
            "source": "Wikidata",
            "verified": False,
            "error": "País vazio."
        }

    pais = str(
        pais
    ).strip()

    # Cria uma pergunta padronizada para
    # reutilizar o núcleo V3.

    resultado = internet_engine_v3(
        f"Qual é a capital do {pais}?"
    )

    if not resultado.get(
        "sucesso"
    ):

        return {
            "success": False,
            "answer": None,
            "source": "Wikidata",
            "verified": False,
            "error": resultado.get(
                "erro"
            )
        }

    return {
        "success": True,
        "answer": resultado.get(
            "resultado"
        ),
        "source": resultado.get(
            "fonte",
            "Wikidata"
        ),
        "verified": True,
        "qid_pais": resultado.get(
            "qid"
        ),
        "descricao": resultado.get(
            "descricao"
        ),
        "error": None
    }


# ============================================================
# 🔵 PESQUISA INTERNET — INTERFACE PRINCIPAL
# ============================================================

def pesquisa_internet(
    pergunta,
    limite=5
):
    """
    Interface principal para o Ultra Core.

    O mecanismo independente é tentado primeiro
    para perguntas estruturadas que o Wikidata
    consegue verificar.

    Para perguntas que não forem resolvidas
    pelo mecanismo estruturado, o DuckDuckGo
    permanece disponível como fallback.

    Retorno padronizado.
    """

    if not pergunta or not str(
        pergunta
    ).strip():

        return {
            "success": False,
            "sucesso": False,
            "provider": "internet_engine",
            "pergunta": pergunta,
            "resultados": [],
            "fontes": [],
            "quantidade": 0,
            "erro": "Pergunta vazia."
        }

    pergunta = str(
        pergunta
    ).strip()

    # ========================================================
    # 🌐 INTERNET ENGINE V3
    # ========================================================

    resultado_wikidata = (
        internet_engine_v3(
            pergunta
        )
    )

    if resultado_wikidata.get(
        "sucesso"
    ):

        capital = resultado_wikidata.get(
            "resultado"
        )

        return {
            "success": True,
            "sucesso": True,
            "provider": "wikidata",
            "pergunta": pergunta,
            "resultado": capital,
            "pais": resultado_wikidata.get(
                "pais"
            ),
            "qid": resultado_wikidata.get(
                "qid"
            ),
            "descricao": resultado_wikidata.get(
                "descricao"
            ),
            "resultados": [
                {
                    "titulo": capital,
                    "url": (
                        "https://www.wikidata.org/wiki/"
                        + str(
                            resultado_wikidata.get(
                                "qid"
                            )
                        )
                    )
                }
            ],
            "fontes": [
                (
                    "https://www.wikidata.org/wiki/"
                    + str(
                        resultado_wikidata.get(
                            "qid"
                        )
                    )
                )
            ],
            "quantidade": 1,
            "verified": True,
            "erro": None
        }

    # ========================================================
    # 🔵 FALLBACK DUCKDUCKGO
    # ========================================================
    #
    # Mantido por compatibilidade.
    # Se estiver bloqueado/indisponível no ambiente,
    # o resultado simplesmente informa a falha.
    #

    resultado_web = pesquisar_web(
        pergunta,
        limite=limite
    )

    if resultado_web.get(
        "success"
    ):

        return resultado_web

    # ========================================================
    # ❌ NENHUM MECANISMO RESOLVEU
    # ========================================================

    return {
        "success": False,
        "sucesso": False,
        "provider": "internet_engine",
        "pergunta": pergunta,
        "resultados": [],
        "fontes": [],
        "quantidade": 0,
        "verified": False,
        "erro": (
            resultado_wikidata.get(
                "erro"
            )
            or resultado_web.get(
                "erro"
            )
            or "Nenhum mecanismo encontrou resultado."
        )
    }


# ============================================================
# 🔵 DISPONIBILIDADE
# ============================================================

def pesquisa_disponivel():
    """
    Informa se o módulo de pesquisa está disponível.

    Mecanismos disponíveis:

    1. Internet Engine / Wikidata
    2. DuckDuckGo Lite
    3. Google Search/Gemini como mecanismo adicional
    """

    return True


# ============================================================
# 🧪 FIM DO MÓDULO
# ============================================================
