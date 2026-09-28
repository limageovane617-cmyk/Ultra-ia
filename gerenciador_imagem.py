# ============================================================
# 🖼️ ALEX IA ULTRA — GERENCIADOR DE IMAGENS
# PIXAZO + Z IMAGE TURBO + FALLBACK AUTOMÁTICO
# SEM REMOÇÃO AUTOMÁTICA DE FUNDO
# Criado por Geovani
# ============================================================

import os
from pathlib import Path

import requests
import streamlit as st


# ============================================================
# ⚙️ CONFIGURAÇÃO
# ============================================================

PIXAZO_URL = (
    "https://gateway.pixazo.ai/"
    "flux-1-schnell/v1/getData"
)

MODELO_PIXAZO = "Flux 1 Schnell"

MOTOR_PIXAZO = (
    "Pixazo / Flux 1 Schnell"
)


# ============================================================
# 🖼️ Z IMAGE TURBO
# ============================================================

ZIMAGE_SPACE = (
    "mrfakename/Z-Image-Turbo"
)

MOTOR_ZIMAGE = (
    "Z Image Turbo"
)


# ============================================================
# 🔐 API KEY PIXAZO
# ============================================================

def obter_api_key_pixazo():

    try:

        chave = st.secrets.get(
            "PIXAZO_API_KEY",
            ""
        )

    except Exception:

        chave = ""

    if not chave:

        chave = os.environ.get(
            "PIXAZO_API_KEY",
            ""
        )

    return str(chave).strip()


# ============================================================
# 📁 PASTA DAS IMAGENS
# ============================================================

def obter_pasta_imagens():

    pasta = Path(
        "/tmp/alex_ia_ultra_imagens"
    )

    pasta.mkdir(
        parents=True,
        exist_ok=True
    )

    return pasta


# ============================================================
# 💾 GUARDAR ÚLTIMA IMAGEM
# ============================================================

def guardar_ultima_imagem(
    imagem,
    prompt,
    caminho=None,
    motor=None,
):

    try:

        st.session_state.ultima_imagem = imagem

        st.session_state.ultima_imagem_caminho = (
            caminho
        )

        st.session_state.ultimo_prompt_imagem = (
            prompt
        )

        st.session_state.ultimo_motor_imagem = (
            motor
        )

        return True

    except Exception:

        return False


# ============================================================
# 🎨 PIXAZO
# ============================================================

def gerar_imagem_pixazo(prompt):

    api_key = obter_api_key_pixazo()

    if not api_key:

        raise RuntimeError(
            "PIXAZO_API_KEY não encontrada."
        )

    headers = {

        "Content-Type": "application/json",

        "Cache-Control": "no-cache",

        "Ocp-Apim-Subscription-Key": (
            api_key
        ),
    }

    dados = {

        "prompt": prompt.strip(),

        "num_steps": 4,

        "height": 1024,

        "width": 1024,
    }

    try:

        resposta = requests.post(

            PIXAZO_URL,

            headers=headers,

            json=dados,

            timeout=120,
        )

    except Exception as erro:

        raise RuntimeError(
            f"Erro de conexão com Pixazo: {erro}"
        )

    if resposta.status_code != 200:

        try:

            detalhes = resposta.json()

        except Exception:

            detalhes = resposta.text

        raise RuntimeError(

            f"Pixazo HTTP "
            f"{resposta.status_code}: "
            f"{detalhes}"
        )

    try:

        resultado = resposta.json()

    except Exception as erro:

        raise RuntimeError(
            f"Pixazo não retornou JSON: {erro}"
        )

    imagem_url = None

    if isinstance(resultado, dict):

        imagem_url = (

            resultado.get("output")

            or resultado.get("image")

            or resultado.get("image_url")

            or resultado.get("url")
        )

    elif isinstance(resultado, list):

        if resultado:

            primeiro = resultado[0]

            if isinstance(
                primeiro,
                str
            ):

                imagem_url = primeiro

            elif isinstance(
                primeiro,
                dict
            ):

                imagem_url = (

                    primeiro.get("output")

                    or primeiro.get("image")

                    or primeiro.get(
                        "image_url"
                    )

                    or primeiro.get("url")
                )

    if not imagem_url:

        raise RuntimeError(
            "Pixazo não retornou a URL "
            "da imagem."
        )

    try:

        imagem = requests.get(

            imagem_url,

            timeout=120,
        )

    except Exception as erro:

        raise RuntimeError(
            f"Erro ao baixar imagem Pixazo: "
            f"{erro}"
        )

    if imagem.status_code != 200:

        raise RuntimeError(
            "Erro ao baixar imagem Pixazo. "
            f"HTTP {imagem.status_code}"
        )

    caminho = (

        obter_pasta_imagens()

        / "ultima_imagem.png"
    )

    caminho.write_bytes(
        imagem.content
    )

    return str(caminho)


# ============================================================
# 🤖 Z IMAGE TURBO
# ============================================================

def gerar_imagem_zimage(prompt):

    try:

        from gradio_client import Client

    except Exception as erro:

        raise RuntimeError(
            "A biblioteca gradio_client "
            "não está instalada. "
            f"Detalhes: {erro}"
        )

    try:

        cliente = Client(
            ZIMAGE_SPACE
        )

        resultado = cliente.predict(

            prompt.strip(),

            1024,

            1024,

            9,

            42,

            True,

            api_name="/generate_image"
        )

    except Exception as erro:

        raise RuntimeError(
            f"Erro ao chamar Z Image Turbo: "
            f"{erro}"
        )

    # ========================================================
    # OBTER CAMINHO RETORNADO
    # ========================================================

    imagem = None

    if isinstance(
        resultado,
        tuple
    ):

        if len(resultado) > 0:

            imagem = resultado[0]

    elif isinstance(
        resultado,
        str
    ):

        imagem = resultado

    elif isinstance(
        resultado,
        list
    ):

        if resultado:

            imagem = resultado[0]

    if not imagem:

        raise RuntimeError(
            "Z Image Turbo não retornou "
            "uma imagem."
        )

    caminho_origem = str(
        imagem
    )

    pasta = obter_pasta_imagens()

    caminho_final = (
        pasta / "ultima_imagem.png"
    )

    # ========================================================
    # CASO SEJA URL
    # ========================================================

    if caminho_origem.startswith(
        "http://"
    ) or caminho_origem.startswith(
        "https://"
    ):

        try:

            resposta = requests.get(

                caminho_origem,

                timeout=120,
            )

        except Exception as erro:

            raise RuntimeError(
                f"Erro ao baixar imagem "
                f"Z Image Turbo: {erro}"
            )

        if resposta.status_code != 200:

            raise RuntimeError(
                "Erro ao baixar imagem "
                "Z Image Turbo. "
                f"HTTP {resposta.status_code}"
            )

        caminho_final.write_bytes(
            resposta.content
        )

        return str(
            caminho_final
        )

    # ========================================================
    # CASO SEJA ARQUIVO LOCAL
    # ========================================================

    origem = Path(
        caminho_origem
    )

    if origem.exists():

        try:

            caminho_final.write_bytes(
                origem.read_bytes()
            )

        except Exception as erro:

            raise RuntimeError(
                f"Erro ao copiar imagem "
                f"Z Image Turbo: {erro}"
            )

        return str(
            caminho_final
        )

    # ========================================================
    # RESULTADO NÃO IDENTIFICADO
    # ========================================================

    raise RuntimeError(
        "Z Image Turbo retornou um resultado "
        "que não conseguimos identificar:\n\n"
        f"{resultado}"
    )


# ============================================================
# 🧠 GERADOR PRINCIPAL
# ============================================================

def gerar_imagem(prompt):

    if not prompt or not prompt.strip():

        return (
            None,
            "❌ O prompt da imagem está vazio."
        )

    # ========================================================
    # 🥇 MOTOR 1 — PIXAZO
    # ========================================================

    try:

        caminho = gerar_imagem_pixazo(
            prompt
        )

        # ----------------------------------------------------
        # IMPORTANTE:
        # NÃO REMOVER O FUNDO.
        # A imagem original será usada diretamente.
        # ----------------------------------------------------

        guardar_ultima_imagem(

            imagem=caminho,

            prompt=prompt,

            caminho=caminho,

            motor=MOTOR_PIXAZO,
        )

        return (

            caminho,

            "🖼️ Imagem gerada com sucesso."
        )

    except Exception as erro_pixazo:

        print(
            "⚠️ Pixazo falhou:",
            erro_pixazo
        )

    # ========================================================
    # 🥈 MOTOR 2 — Z IMAGE TURBO
    # ========================================================

    try:

        caminho = gerar_imagem_zimage(
            prompt
        )

        # ----------------------------------------------------
        # IMPORTANTE:
        # NÃO REMOVER O FUNDO.
        # A imagem original será usada diretamente.
        # ----------------------------------------------------

        guardar_ultima_imagem(

            imagem=caminho,

            prompt=prompt,

            caminho=caminho,

            motor=MOTOR_ZIMAGE,
        )

        return (

            caminho,

            "🖼️ Imagem gerada com sucesso."
        )

    except Exception as erro_zimage:

        print(
            "⚠️ Z Image Turbo falhou:",
            erro_zimage
        )

    # ========================================================
    # ❌ OS DOIS FALHARAM
    # ========================================================

    return (

        None,

        "❌ Não foi possível gerar a imagem "
        "neste momento."
    )


# ============================================================
# 🖼️ MOSTRAR IMAGEM
# ============================================================

def mostrar_imagem(prompt):

    with st.spinner(
        "🎨 Alex IA está criando sua imagem..."
    ):

        imagem, mensagem = gerar_imagem(
            prompt
        )

    if imagem is None:

        st.error(
            mensagem
        )

        return False

    st.image(

        imagem,

        caption=(
            "🖼️ Imagem gerada pela "
            "Alex IA Ultra"
        ),

        use_container_width=True,
    )

    motor = st.session_state.get(

        "ultimo_motor_imagem",

        "",
    )

    if motor:

        st.caption(
            f"🎨 Motor utilizado: {motor}"
        )

    return True


# ============================================================
# 🔎 ACESSO À ÚLTIMA IMAGEM
# ============================================================

def obter_ultima_imagem():

    return st.session_state.get(
        "ultima_imagem"
    )


def obter_caminho_ultima_imagem():

    return st.session_state.get(
        "ultima_imagem_caminho"
    )


def obter_prompt_ultima_imagem():

    return st.session_state.get(
        "ultimo_prompt_imagem",
        "",
    )


def obter_motor_ultima_imagem():

    return st.session_state.get(
        "ultimo_motor_imagem",
        "",
    )


# ============================================================
# 🧹 LIMPAR ÚLTIMA IMAGEM
# ============================================================

def limpar_ultima_imagem():

    for chave in [

        "ultima_imagem",

        "ultima_imagem_caminho",

        "ultimo_prompt_imagem",

        "ultimo_motor_imagem",

    ]:

        st.session_state.pop(
            chave,
            None
        )


# ============================================================
# 🧪 TESTE DIRETO
# ============================================================

def executar_teste():

    st.title(
        "🖼️ Teste de Geração de Imagem"
    )

    st.write(
        "Alex IA Ultra utiliza dois "
        "motores com fallback automático."
    )

    st.info(
        "🥇 Pixazo → "
        "🥈 Z Image Turbo"
    )

    prompt = st.text_input(

        "Digite o que deseja gerar:",

        value=(

            "Um beija-flor voando "
            "com asas abertas"
        ),
    )

    if st.button(

        "🎨 Gerar imagem",

        use_container_width=True,

    ):

        if not prompt.strip():

            st.warning(
                "Digite um prompt para "
                "gerar a imagem."
            )

            return

        mostrar_imagem(
            prompt
        )


# ============================================================
# 🚀 EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    executar_teste()
