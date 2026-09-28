# ============================================================
# 🤖 ALEX IA ULTRA
# APP PRINCIPAL
# ============================================================
# Criado por: Geovani
# ============================================================
# teste do codex

import base64
import os
import sys
import importlib
import requests
from pathlib import Path

import streamlit as st

from ponte_alex import (
    verificar_ponte,
    ponte_disponivel,
    obter_status_ponte,
    ClientePonteAlex,
    ErroPonteAlex,
)


# ============================================================
# ⚙️ CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Alex IA Ultra",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# 📦 IMPORTAÇÕES DO PROJETO
# ============================================================

if "gerenciador_imagem" in sys.modules:
    importlib.reload(sys.modules["gerenciador_imagem"])
else:
    import gerenciador_imagem

from gerenciador_imagem import mostrar_imagem

from config_ultra import (
    SYSTEM_PROMPT,
    GEMINI_MODEL,
    AI_NAME,
    CREATOR_NAME
)

from servicos import (
    criar_cliente_gemini,
    verificar_servicos
)

from memoria import (
    salvar_memoria,
    carregar_memorias,
    apagar_memoria,
    apagar_todas_memorias
)

from personagens import (
    salvar_personagem,
    carregar_personagem,
    listar_personagens,
    apagar_personagem
)

from voz import (
    mostrar_audio,
    gerar_audio
)

import video

gerar_video = video.gerar_video
mostrar_configuracao_video = video.mostrar_configuracao_video
verificar_magic_hour = video.verificar_magic_hour

from arquivos import ler_arquivo

from codigo import (
    preparar_pedido_codigo,
    listar_linguagens
)


# ============================================================
# 🧠 ULTRA CORE
# ============================================================

from kaggle_secrets import UserSecretsClient

from ultra_core.tool_loader import carregar_ferramentas
from ultra_core.brain import UltraBrain
from ultra_core.intelligence import intelligence
from gemini_bridge import criar_gemini_bridge


# ------------------------------------------------------------
# 🔧 CARREGAR FERRAMENTAS
# ------------------------------------------------------------

status_ultra = carregar_ferramentas()


# ------------------------------------------------------------
# 🔐 GEMINI BRIDGE
# ------------------------------------------------------------

try:

    secrets = UserSecretsClient()

    gemini_api_key = secrets.get_secret(
        "GEMINI_API_KEY"
    )

except Exception:

    gemini_api_key = None


gemini_bridge = criar_gemini_bridge(
    api_key=gemini_api_key,
    model="gemini-3.1-flash-lite"
)


# ------------------------------------------------------------
# 🧠 ULTRA BRAIN
# ------------------------------------------------------------

ultra_brain = UltraBrain(
    task_intelligence=intelligence,
    gemini_bridge=gemini_bridge
)


# ============================================================
# 🧠 SESSION STATE
# ============================================================

DEFAULTS = {
    "mensagens": [],
    "personagem_atual": None,
    "arquivo_contexto": "",
    "arquivo_nome": "",
    "imagem_contexto": None,
    "imagem_nome": "",
    "imagem_mime": "",
    "ferramenta_ativa": None,
    "usar_voz": False,
    "ultima_imagem_caminho": None,
}

for chave, valor in DEFAULTS.items():

    if chave not in st.session_state:
        st.session_state[chave] = valor


# ============================================================
# 🔐 SERVIÇOS
# ============================================================

servicos = verificar_servicos()

if not servicos.get("gemini"):

    st.error(
        "🔐 A chave GEMINI_API_KEY não está configurada "
        "nos Secrets do Streamlit."
    )

    st.stop()


cliente = criar_cliente_gemini()

if cliente is None:

    st.error(
        "❌ Não foi possível criar a conexão com o Gemini."
    )

    st.stop()


# ============================================================
# 🖼️ FUNDO DA ALEX IA ULTRA
# ============================================================

FUNDO_URL = (
    "https://i.supaimg.com/"
    "c4e94ec5-263e-44e5-b119-dca8baa8acad/"
    "9865081d-da93-4f67-a58d-f304f9feb1cb.jpg"
)


# ============================================================
# 🎨 CSS
# ============================================================

CSS = f"""
<style>

.stApp {{
    background-image: url("{FUNDO_URL}") !important;
    background-size: 100% 100% !important;
    background-position: center center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
    min-height: 100vh !important;
}}

.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    background: rgba(2,8,16,.35);
    z-index: 0;
    pointer-events: none;
}}

.main .block-container {{
    max-width: 980px;
    padding-top: 1.2rem;
    padding-bottom: 8rem;
}}


/* ========================================================
   📱 MODO APP — OCULTAR INTERFACE DO STREAMLIT
   ======================================================== */

header[data-testid="stHeader"] {{
    display: none !important;
}}

footer {{
    display: none !important;
}}

#MainMenu {{
    display: none !important;
}}


/* ========================================================
   📱 REMOVER BARRA INFERIOR DO STREAMLIT
   ======================================================== */

[data-testid="stBottomBlockContainer"] {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}

[data-testid="stBottom"] {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}


/* ========================================================
   📱 OCULTAR ELEMENTOS INFERIORES DO STREAMLIT
   ======================================================== */

div[data-testid="stStatusWidget"] {{
    display: none !important;
}}

div[data-testid="stDecoration"] {{
    display: none !important;
}}


/* ========================================================
   ➕ BOTÃO DE FERRAMENTAS
   ======================================================== */

div[data-testid="stElementContainer"]:has(
    div[data-testid="stPopover"]
),
div[data-testid="stPopover"] {{

    position: fixed !important;

    bottom: 14px !important;

    left: 1px !important;

    width: auto !important;

    z-index: 99999 !important;
}}


div[data-testid="stPopover"] > button {{

    padding: 0 !important;

    min-width: 1px !important;

    width: 1px !important;

    height: 1px !important;

    border-radius: 100% !important;

    border: 1px solid
        rgba(255, 0, 0, 0.3) !important;

    background-color:
        rgba(15, 23, 42, 0.85) !important;

    color: #ffffff !important;

    display: flex !important;

    align-items: center !important;

    justify-content: center !important;
}}


/* ========================================================
   🧰 PAINEL DE FERRAMENTAS
   ======================================================== */

.tool-panel {{

    margin: 0 auto .60rem;

    padding: .75rem;

    border-radius: 100px;

    background: rgba(8,17,29,.92);

    border: 1px solid
        rgba(130,210,255,.16);
}}


/* ========================================================
   💬 ESPAÇO PARA O +
   ======================================================== */

div[data-testid="stChatInput"] {{
    padding-left: 55px !important;
}}


/* ========================================================
   💬 CHAT
   ======================================================== */

div[data-testid="stChatMessage"] {{
    background: transparent !important;
}}

div[data-testid="stChatMessage"] > div {{
    background: transparent !important;
}}


/* ========================================================
   👤 MENSAGEM DO USUÁRIO
   ======================================================== */

.user-message {{
    background: rgba(40,110,180,0.90);
    color: white;
    padding: 11px 15px;
    border-radius: 20px 20px 5px 20px;
    font-size: 16px;
    line-height: 1.45;
    word-break: break-word;
    width: fit-content;
    max-width: 75%;
    margin-left: auto;
}}


/* ========================================================
   ✨ MENSAGEM DA ALEX
   ======================================================== */

.assistant-message {{
    background: rgba(0,0,0,0.50);
    color: white;
    padding: 12px 16px;
    border-radius: 20px 20px 20px 5px;
    font-size: 16px;
    line-height: 1.45;
    word-wrap: break-word;
    width: fit-content;
    max-width: 78%;
}}

.alex-name {{
    font-weight: bold;
    margin-bottom: 6px;
    color: #8fd8ff;
}}


/* ========================================================
   🔊 BOTÃO DE ÁUDIO
   ======================================================== */

button[kind="secondary"] {{
    border-radius: 18px !important;
}}

</style>
"""

st.markdown(
    CSS,
    unsafe_allow_html=True
)


# ============================================================
# 🤖 CABEÇALHO
# ============================================================

st.markdown(
    f"## 🤖 {AI_NAME}"
)

st.caption(
    f"Criada por {CREATOR_NAME} • inteligência artificial pessoal"
)


# ============================================================
# 💬 HISTÓRICO
# ============================================================

for indice, mensagem in enumerate(
    st.session_state.mensagens
):

    role = mensagem.get(
        "role",
        "assistant"
    )

    tipo = mensagem.get(
        "tipo",
        "texto"
    )

    texto = mensagem.get(
        "content",
        ""
    )


    # ========================================================
    # 👤 USUÁRIO
    # ========================================================

    if role == "user":

        with st.chat_message(
            "user",
            avatar="👤"
        ):

            st.markdown(
                f"""
                <div class="user-message">
                    {texto}
                </div>
                """,
                unsafe_allow_html=True
            )

        continue


    # ========================================================
    # ✨ ALEX
    # ========================================================

    with st.chat_message(
        "assistant",
        avatar="✨"
    ):

        st.markdown(
            """
            <div class="alex-name">
                ✨ Alex IA
            </div>
            """,
            unsafe_allow_html=True
        )


        # ====================================================
        # 🖼️ IMAGEM
        # ====================================================

        if (
            tipo == "imagem"
            and mensagem.get("arquivo")
            and os.path.exists(
                mensagem["arquivo"]
            )
        ):

            st.image(
                mensagem["arquivo"],
                use_container_width=True
            )


        # ====================================================
        # 🎬 VÍDEO
        # ====================================================

        elif (
            tipo == "video"
            and mensagem.get("arquivo")
            and os.path.exists(
                mensagem["arquivo"]
            )
        ):

            st.video(
                mensagem["arquivo"]
            )


        # ====================================================
        # 💬 TEXTO
        # ====================================================

        if texto:

            st.markdown(
                texto,
                unsafe_allow_html=False
            )


        # ====================================================
        # 🔊 BOTÃO OUVIR
        # ====================================================

        if texto:

            audio_key = (
                "historico_audio_"
                + str(indice)
            )

            if st.button(
                "🔊",
                key=audio_key
            ):

                with st.spinner(
                    "🔊 Preparando a voz..."
                ):

                    audio, erro, formato = (
                        gerar_audio(texto)
                    )

                if audio:

                    st.audio(
                        audio,
                        format=formato
                    )

                else:

                    st.error(
                        "❌ Não foi possível gerar "
                        f"a voz: {erro}"
                    )


# ============================================================
# 🧰 MENU DE FERRAMENTAS
# ============================================================

with st.popover("＋"):

    st.markdown(
        "### ☢️ Ferramentas"
    )

    ferramentas = [

        ("imagem", "🖼️ Imagem"),

        ("video", "🎬 Vídeo"),

        ("voz", "🔊 Voz"),

        ("codigo", "💻 Código"),

        ("arquivo", "📎 Arquivo"),

        ("personagem", "🎭 Personagem"),

        ("memoria", "🧠 Memória"),

    ]

    for nome, rotulo in ferramentas:

        if st.button(
            rotulo,
            use_container_width=True,
            key=f"ferramenta_{nome}"
        ):

            st.session_state.ferramenta_ativa = nome

            st.rerun()


    st.divider()


    if st.button(
        "🗑️ Limpar chat",
        use_container_width=True,
        key="limpar_chat"
    ):

        st.session_state.mensagens = []

        st.rerun()


# ============================================================
# 🧰 FERRAMENTA ATIVA
# ============================================================

ferramenta = (
    st.session_state.ferramenta_ativa
)


if ferramenta:

    st.markdown(
        '<div class="tool-panel">',
        unsafe_allow_html=True
    )


    # ========================================================
    # ❌ FECHAR
    # ========================================================

    if st.button(
        "✕ Fechar ferramenta",
        key="fechar_ferramenta"
    ):

        st.session_state.ferramenta_ativa = None

        st.rerun()


    # ========================================================
    # 🖼️ IMAGEM
    # ========================================================

    if ferramenta == "imagem":

        prompt_imagem = st.text_area(
            "📝 Prompt da imagem",
            key="tool_prompt_imagem",
            height=100
        )

        if st.button(
            "🖼️ Gerar imagem",
            type="primary",
            key="gerar_imagem_ferramenta"
        ):

            if not prompt_imagem.strip():

                st.warning(
                    "Digite o que você quer na imagem."
                )

            else:

                with st.spinner(
                    "🖼️ Criando imagem..."
                ):

                    sucesso = mostrar_imagem(
                        prompt_imagem.strip()
                    )


                if sucesso:

                    caminho = (
                        st.session_state.get(
                            "ultima_imagem_caminho"
                        )
                    )


                    st.session_state.mensagens.append({

                        "role":
                            "assistant",

                        "content":
                            "🖼️ Imagem criada.",

                        "tipo":
                            "imagem",

                        "arquivo":
                            caminho,
                    })


                    st.session_state.ferramenta_ativa = None

                    st.rerun()


    # ========================================================
    # 🎬 VÍDEO
    # ========================================================

    elif ferramenta == "video":

        st.markdown(
            "### 🎬 Gerador de vídeo"
        )


        camera, proporcao, duracao = (
            mostrar_configuracao_video()
        )


        st.divider()


        imagem = st.file_uploader(
            "📤 Imagem de referência (opcional)",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ],
            key="video_imagem_upload"
        )


        if imagem:

            st.image(
                imagem,
                caption="Imagem de referência",
                use_container_width=True
            )


        descricao = st.text_area(
            "📝 Descrição do vídeo",
            key="tool_prompt_video",
            height=130,
            placeholder=(
                "Exemplo: um personagem "
                "caminhando lentamente em uma "
                "rua cinematográfica..."
            )
        )


        if st.button(
            "🎬 Gerar vídeo",
            type="primary",
            use_container_width=True,
            key="gerar_video_ferramenta"
        ):

            if not descricao.strip():

                st.warning(
                    "⚠️ Digite a descrição do vídeo."
                )

                st.stop()


            if imagem:

                imagem_bytes = imagem.getvalue()

                nome_imagem = imagem.name

            else:

                imagem_bytes = None

                nome_imagem = "imagem.png"


            try:

                with st.spinner(
                    "🎬 Gerando vídeo... aguarde o processamento."
                ):

                    resultado = gerar_video(
                        descricao=descricao.strip(),
                        imagem_bytes=imagem_bytes,
                        nome_imagem=nome_imagem,
                        duracao=duracao,
                        width=512,
                        height=512,
                        camera=camera,
                        proporcao=proporcao,
                    )


                if resultado is None:

                    st.error(
                        "❌ O gerenciador de vídeo "
                        "não retornou nenhuma resposta."
                    )

                    st.stop()


                if not isinstance(
                    resultado,
                    dict
                ):

                    st.error(
                        "❌ O gerenciador de vídeo "
                        "retornou uma resposta inválida."
                    )

                    st.code(
                        str(resultado)
                    )

                    st.stop()


                caminho = resultado.get(
                    "video"
                )

                motor = resultado.get(
                    "motor",
                    "desconhecido"
                )

                sucesso = resultado.get(
                    "sucesso",
                    False
                )

                erro = resultado.get(
                    "erro"
                )


                if sucesso and caminho:

                    caminho = str(caminho)


                    if not os.path.exists(
                        caminho
                    ):

                        st.error(
                            "❌ O motor informou que "
                            "criou o vídeo, mas o "
                            "arquivo não existe."
                        )

                        st.code(
                            caminho
                        )

                        st.stop()


                    st.success(
                        "🎉 Vídeo gerado com sucesso!\n\n"
                        f"🎬 Motor: {motor}"
                    )


                    st.video(
                        caminho
                    )


                    st.session_state.mensagens.append({

                        "role":
                            "assistant",

                        "content": (
                            "🎬 Vídeo criado com "
                            f"sucesso usando {motor}."
                        ),

                        "tipo":
                            "video",

                        "arquivo":
                            caminho,
                    })


                    st.session_state.ferramenta_ativa = None

                    st.rerun()


                else:

                    st.error(
                        "❌ Nenhum vídeo foi gerado."
                    )


                    if erro:

                        st.warning(
                            "Detalhes do erro:"
                        )

                        st.code(
                            str(erro)
                        )


                    st.markdown(
                        "### 🔎 Resposta do gerenciador"
                    )

                    st.json(
                        resultado
                    )


            except Exception as erro_video:

                st.error(
                    "❌ O gerador de vídeo "
                    "encontrou um erro."
                )

                st.code(
                    str(erro_video)
                )


    # ========================================================
    # 🔊 VOZ
    # ========================================================

    elif ferramenta == "voz":

        st.session_state.usar_voz = st.checkbox(
            "🔊 Ler respostas da Alex em voz",
            value=st.session_state.usar_voz,
            key="ativar_voz_alex"
        )


        if st.session_state.usar_voz:

            st.success(
                "🔊 Voz automática ativada."
            )

            st.info(
                "A Alex tentará usar o Gemini TTS "
                "e utilizará o gTTS como backup."
            )

        else:

            st.info(
                "A voz automática está desativada."
            )


    # ========================================================
    # 💻 CÓDIGO
    # ========================================================

    elif ferramenta == "codigo":

        st.markdown(
            "### 💻 Código"
        )


        linguagem = st.selectbox(
            "Linguagem",
            listar_linguagens(),
            key="tool_linguagem_codigo"
        )


        codigo_entrada = st.text_area(
            "📝 Digite ou cole o código",
            height=300,
            key="ponte_codigo_entrada",
            placeholder=(
                "Cole aqui o código que você quer processar..."
            )
        )


        instrucao_ponte = st.text_area(
            "🔧 O que a Ponte deve fazer?",
            height=100,
            key="ponte_instrucao_codigo",
            placeholder=(
                "Exemplo: criar um arquivo, corrigir o código, "
                "melhorar uma função..."
            )
        )


        st.caption(
            "🌉 O código será enviado para a Ponte Alex v2 "
            "somente quando você clicar no botão abaixo."
        )


        # ====================================================
        # 🌉 PROCESSAR CÓDIGO
        # ====================================================

        if st.button(
            "🌉 Processar com a Ponte Alex",
            type="primary",
            use_container_width=True,
            key="processar_codigo_ponte"
        ):

            if not codigo_entrada.strip():

                st.warning(
                    "⚠️ Digite ou cole algum código primeiro."
                )

                st.stop()


            if not instrucao_ponte.strip():

                st.warning(
                    "⚠️ Informe o que você quer que a Ponte faça."
                )

                st.stop()


            if linguagem.lower() not in (
                "python",
                "python 3",
                "py"
            ):

                st.info(
                    "🌉 A integração inicial da Ponte "
                    "está preparada para código Python."
                )

                st.stop()


            try:

                # ============================================
                # 🔎 VERIFICAR PONTE
                # ============================================

                with st.spinner(
                    "🌉 Verificando a Ponte Alex v2..."
                ):

                    ponte_online = verificar_ponte()


                if not ponte_online:

                    st.error(
                        "❌ A Ponte Alex v2 não está disponível."
                    )

                    st.stop()


                # ============================================
                # ⚙️ PROCESSAR CÓDIGO
                # ============================================

                with st.spinner(
                    "⚙️ A Ponte está processando o código..."
                ):

                    cliente_ponte = ClientePonteAlex()

                    resultado = cliente_ponte.processar_codigo(
                        conteudo_codigo=codigo_entrada,
                        instrucao=instrucao_ponte,
                        nome_arquivo="codigo_alex.py"
                    )


                # ============================================================
                # 📄 LER CONTEÚDO RETORNADO PELA PONTE
                # ============================================================

                conteudo_resultado = ""

                resposta_completa = resultado.get(
                    "resposta_completa",
                    {}
                )


                if isinstance(
                    resposta_completa,
                    dict
                ):

                    processed_file = (
                        resposta_completa.get(
                            "processedFile",
                            {}
                        )
                    )

                else:

                    processed_file = {}


                if isinstance(
                    processed_file,
                    dict
                ):

                    conteudo_resultado = (
                        processed_file.get(
                            "content",
                            ""
                        )
                    )


                # ============================================================
                # 📄 COMPATIBILIDADE COM ARQUIVO SALVO
                # ============================================================

                if not conteudo_resultado:

                    caminho_resultado = (
                        resultado.get(
                            "arquivo_salvo"
                        )
                    )


                    if caminho_resultado:

                        if os.path.exists(
                            caminho_resultado
                        ):

                            try:

                                conteudo_resultado = Path(
                                    caminho_resultado
                                ).read_text(
                                    encoding="utf-8",
                                    errors="replace"
                                )

                            except Exception as erro_leitura:

                                st.error(
                                    "❌ Não foi possível ler "
                                    "o arquivo gerado."
                                )

                                st.code(
                                    str(erro_leitura)
                                )


                # ============================================================
                # 💾 SALVAR TUDO PARA SOBREVIVER AO RERUN
                # ============================================================

                st.session_state["ponte_resultado"] = (
                    resultado
                )

                st.session_state["ponte_conteudo"] = (
                    conteudo_resultado
                )

                st.session_state["ponte_processado"] = True


                # ============================================================
                # 📄 NOME REAL DO ARQUIVO PROCESSADO
                # ============================================================

                nome_processado = ""


                if isinstance(
                    processed_file,
                    dict
                ):

                    nome_processado = (
                        processed_file.get(
                            "filename",
                            ""
                        )
                    )


                st.session_state["ponte_nome_download"] = (
                    nome_processado
                    or "codigo_alex.py"
                )


                st.success(
                    "🌉 Código processado pela Ponte Alex v2!"
                )


            except ErroPonteAlex as erro:

                st.error(
                    "❌ Erro na Ponte Alex v2."
                )

                st.code(
                    str(erro)
                )


            except Exception as erro:

                st.error(
                    "❌ Erro ao processar o código."
                )

                st.code(
                    str(erro)
                )


        # ====================================================
        # 📄 MOSTRAR RESULTADO SALVO
        # ====================================================

        if st.session_state.get(
            "ponte_processado",
            False
        ):

            resultado = st.session_state.get(
                "ponte_resultado",
                {}
            )


            conteudo_resultado = st.session_state.get(
                "ponte_conteudo",
                ""
            )


            st.markdown(
                "### 📄 Resultado"
            )


            if conteudo_resultado:

                st.code(
                    conteudo_resultado,
                    language="python"
                )

            else:

                st.warning(
                    "⚠️ Nenhum conteúdo de arquivo foi retornado."
                )


            # =================================================
            # ✏️ EDITOR DO ARQUIVO
            # =================================================

            if conteudo_resultado:

                st.markdown(
                    "### ✏️ Editar arquivo"
                )


                conteudo_editado = st.text_area(
                    "📝 Edite o conteúdo antes de baixar",
                    value=conteudo_resultado,
                    height=500,
                    key="editor_arquivo_ponte"
                )


                if st.button(
                    "💾 Salvar alterações",
                    type="primary",
                    use_container_width=True,
                    key="salvar_edicao_ponte"
                ):

                    st.session_state["ponte_conteudo"] = (
                        conteudo_editado
                    )


                    conteudo_resultado = (
                        conteudo_editado
                    )


                    st.success(
                        "✅ Alterações salvas! "
                        "O arquivo para download foi atualizado."
                    )


                    st.rerun()


            # =================================================
            # 📥 CRIAR ARQUIVO PARA DOWNLOAD
            # =================================================

            if conteudo_resultado:

                st.markdown(
                    "### 📥 Criar arquivo para download"
                )


                nome_download = st.text_input(
                    "Nome do arquivo",

                    value=st.session_state.get(
                        "ponte_nome_download",
                        "codigo_alex.py"
                    ),

                    key="nome_download_codigo"
                )


                # -------------------------------------------------
                # 🔐 LIMPAR NOME DO ARQUIVO
                # -------------------------------------------------

                nome_download = (
                    nome_download
                    .strip()
                    .replace("\\", "/")
                    .split("/")[-1]
                )


                if not nome_download:

                    nome_download = "codigo_alex.py"


                # -------------------------------------------------
                # 🔤 VERIFICAR UTF-8 REAL
                # -------------------------------------------------

                try:

                    conteudo_limpo = (
                        conteudo_resultado
                        .lstrip("\ufeff")
                    )


                    st.write(
                        "🔎 TESTE ANTES DO DOWNLOAD:",
                        repr(conteudo_limpo)
                    )


                    arquivo_utf8 = (
                        b"\xef\xbb\xbf"
                        + conteudo_limpo.encode("utf-8")
                    )


                except Exception as erro_utf8:

                    st.error(
                        "❌ Não foi possível preparar "
                        "o arquivo em UTF-8."
                    )


                    st.code(
                        str(erro_utf8)
                    )


                    arquivo_utf8 = None


                # -------------------------------------------------
                # ⬇️ DOWNLOAD DIRETO
                # -------------------------------------------------

                if arquivo_utf8 is not None:

                    st.download_button(
                        label="⬇️ Baixar arquivo",

                        data=arquivo_utf8,

                        file_name=nome_download,

                        mime=(
                            "text/x-python"
                            if nome_download.lower().endswith(".py")
                            else "text/plain"
                        ),

                        use_container_width=True,

                        key="baixar_arquivo_ponte"
                    )


            # =================================================
            # ✅ TESTE PYTHON
            # =================================================

            if resultado.get(
                "test_passed"
            ):

                st.success(
                    "✅ Execução Python aprovada pela Ponte."
                )

            else:

                st.warning(
                    "⚠️ O processamento foi concluído, "
                    "mas o teste de execução não foi aprovado."
                )



            # =================================================
            # 🧪 DIAGNÓSTICO DA EXECUÇÃO
            # =================================================

            execucao = resultado.get(
                "execution",
                {}
            )

            if not isinstance(
                execucao,
                dict
            ):
                execucao = {}

            compile_check = resultado.get(
                "compile_check",
                {}
            )

            if not isinstance(
                compile_check,
                dict
            ):
                compile_check = {}

            test_passed = resultado.get(
                "test_passed",
                False
            )

            test_message = resultado.get(
                "test_message",
                ""
            )

            st.markdown(
                "### 🧪 Diagnóstico da Ponte Alex v2"
            )

            if compile_check:
                st.write("**Compilação:**")
                st.json(compile_check)

            st.write("**Teste:**")
            st.write(
                test_message
                or (
                    "OK"
                    if test_passed
                    else "Não aprovado"
                )
            )

            stdout = execucao.get(
                "stdout",
                ""
            )

            if stdout:
                st.markdown(
                    "### 🖥️ Saída da execução"
                )

                st.code(
                    stdout,
                    language="text"
                )

            stderr = execucao.get(
                "stderr",
                ""
            )

            if stderr:
                st.markdown(
                    "### ⚠️ Erro da execução"
                )

                st.error(
                    "A Ponte retornou um erro "
                    "durante a execução do Python."
                )

                st.code(
                    stderr,
                    language="text"
                )

            if not stdout and not stderr:
                st.info(
                    "A Ponte não retornou saída nem "
                    "mensagem de erro da execução."
                )


    # ========================================================
    # 📎 CENTRAL DE ARQUIVOS
    # ========================================================

    elif ferramenta == "arquivo":

        st.markdown(
            "### 📎 Central de Arquivos"
        )


        st.caption(
            "Envie imagens, documentos, áudios, vídeos, "
            "códigos ou outros arquivos."
        )


        arquivos_enviados = st.file_uploader(

            "📤 Escolher arquivos",

            type=[

                # 🖼️ Imagens
                "png", "jpg", "jpeg", "webp",
                "gif", "bmp", "tiff",

                # 📄 Documentos
                "pdf", "txt", "doc", "docx",
                "rtf",

                # 📊 Dados
                "csv", "json", "xml", "md",
                "xls", "xlsx",

                # 🎵 Áudio
                "mp3", "wav", "ogg", "m4a",
                "flac", "aac",

                # 🎬 Vídeo
                "mp4", "mov", "avi", "mkv",
                "webm",

                # 💻 Código
                "py", "js", "ts", "html",
                "css", "java", "cpp", "c",
                "h", "sql", "sh",

                # 📦 Compactado
                "zip"
            ],

            accept_multiple_files=True,

            key="central_arquivos_upload"
        )


        if arquivos_enviados:

            st.success(
                f"📁 {len(arquivos_enviados)} "
                "arquivo(s) selecionado(s)."
            )


            for arquivo in arquivos_enviados:

                st.markdown(
                    f"**📄 {arquivo.name}**  \n"
                    f"Tamanho: "
                    f"{arquivo.size / 1024:.1f} KB"
                )


                nome = arquivo.name.lower()


                # ====================================================
                # 🖼️ IMAGEM — PREPARAÇÃO PARA VISÃO DA ALEX
                # ====================================================

                if nome.endswith((
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".webp",
                    ".gif",
                    ".bmp",
                    ".tiff"
                )):

                    st.image(
                        arquivo,
                        caption=arquivo.name,
                        use_container_width=True
                    )


                    if st.button(
                        f"👁️ Carregar imagem para a Alex — "
                        f"{arquivo.name}",
                        key=(
                            f"visao_"
                            f"{arquivo.name}_"
                            f"{arquivo.size}"
                        ),
                        type="primary"
                    ):

                        try:

                            imagem_bytes = (
                                arquivo.getvalue()
                            )


                            mime = (
                                arquivo.type
                                or "image/jpeg"
                            )


                            st.session_state.imagem_contexto = (
                                imagem_bytes
                            )


                            st.session_state.imagem_nome = (
                                arquivo.name
                            )


                            st.session_state.imagem_mime = (
                                mime
                            )


                            st.success(
                                f"👁️ {arquivo.name} "
                                "foi carregada para a visão "
                                "da Alex."
                            )


                            st.info(
                                "🤖 Agora você pode perguntar "
                                "à Alex sobre esta imagem."
                            )


                        except Exception as erro:

                            st.error(
                                "❌ Não foi possível carregar "
                                f"a imagem: {erro}"
                            )


                # ====================================================
                # 🎬 VÍDEO
                # ====================================================

                elif nome.endswith((
                    ".mp4",
                    ".mov",
                    ".avi",
                    ".mkv",
                    ".webm"
                )):

                    st.video(
                        arquivo
                    )


                # ====================================================
                # 🎵 ÁUDIO
                # ====================================================

                elif nome.endswith((
                    ".mp3",
                    ".wav",
                    ".ogg",
                    ".m4a",
                    ".flac",
                    ".aac"
                )):

                    st.audio(
                        arquivo
                    )


                # ====================================================
                # 📖 ARQUIVOS DE TEXTO / CÓDIGO
                # ====================================================

                elif nome.endswith((
                    ".txt",
                    ".py",
                    ".js",
                    ".ts",
                    ".html",
                    ".css",
                    ".java",
                    ".cpp",
                    ".c",
                    ".h",
                    ".sql",
                    ".sh",
                    ".json",
                    ".xml",
                    ".md",
                    ".csv"
                )):

                    if st.button(
                        f"📖 Ler {arquivo.name}",
                        key=(
                            f"ler_"
                            f"{arquivo.name}_"
                            f"{arquivo.size}"
                        )
                    ):

                        texto, erro = (
                            ler_arquivo(arquivo)
                        )


                        if erro:

                            st.error(
                                erro
                            )

                        else:

                            st.session_state.arquivo_contexto = (
                                texto[:50000]
                            )


                            st.session_state.arquivo_nome = (
                                arquivo.name
                            )


                            st.success(
                                f"✅ {arquivo.name} "
                                "foi carregado para a Alex."
                            )


                            with st.expander(
                                "👁️ Ver conteúdo"
                            ):

                                st.code(
                                    texto[:10000],
                                    language="text"
                                )


                # ====================================================
                # 📄 PDF / DOCX / RTF
                # ====================================================

                elif nome.endswith((
                    ".pdf",
                    ".doc",
                    ".docx",
                    ".rtf"
                )):

                    if st.button(
                        f"📖 Ler {arquivo.name}",
                        key=(
                            f"ler_"
                            f"{arquivo.name}_"
                            f"{arquivo.size}"
                        )
                    ):

                        texto, erro = (
                            ler_arquivo(arquivo)
                        )


                        if erro:

                            st.error(
                                erro
                            )

                        else:

                            st.session_state.arquivo_contexto = (
                                texto[:50000]
                            )


                            st.session_state.arquivo_nome = (
                                arquivo.name
                            )


                            st.success(
                                f"✅ {arquivo.name} "
                                "foi carregado para a Alex."
                            )


                            with st.expander(
                                "👁️ Ver conteúdo"
                            ):

                                st.text(
                                    texto[:10000]
                                )


                # ====================================================
                # 📦 ZIP INTELIGENTE
                # ====================================================

                elif nome.endswith(
                    ".zip"
                ):

                    st.markdown(
                        "### 📦 Arquivo ZIP"
                    )


                    st.caption(
                        "A Alex pode analisar os arquivos "
                        "internos do ZIP sem modificar o "
                        "arquivo original."
                    )


                    if st.button(
                        f"🔓 Analisar ZIP — {arquivo.name}",
                        key=(
                            f"analisar_zip_"
                            f"{arquivo.name}_"
                            f"{arquivo.size}"
                        ),
                        type="primary"
                    ):

                        with st.spinner(
                            "📦 Abrindo e analisando o ZIP..."
                        ):

                            texto, erro = (
                                ler_arquivo(arquivo)
                            )


                        if erro:

                            st.error(
                                f"❌ Não foi possível analisar "
                                f"o ZIP: {erro}"
                            )

                        else:

                            st.session_state.arquivo_contexto = (
                                texto[:50000]
                            )


                            st.session_state.arquivo_nome = (
                                arquivo.name
                            )


                            st.success(
                                f"✅ {arquivo.name} "
                                "foi analisado e carregado "
                                "para a Alex."
                            )


                            with st.expander(
                                "👁️ Ver análise interna do ZIP",
                                expanded=True
                            ):

                                st.text(
                                    texto[:20000]
                                )


                            st.info(
                                "🤖 Agora você pode perguntar "
                                "à Alex sobre os arquivos e "
                                "conteúdos encontrados dentro "
                                "deste ZIP."
                            )


    # ========================================================
    # 🎭 PERSONAGEM
    # ========================================================

    elif ferramenta == "personagem":

        nomes = listar_personagens()


        escolhido = st.selectbox(
            "🎭 Personagem salvo",
            ["Nenhum"] + nomes,
            key="personagem_escolhido"
        )


        dados = (

            carregar_personagem(
                escolhido
            )

            if escolhido != "Nenhum"

            else None
        )


        nome = st.text_input(
            "Nome",

            value=(
                dados.get("nome", "")
                if dados
                else ""
            ),

            key="personagem_nome"
        )


        idade = st.text_input(
            "Idade",

            value=(
                dados.get("idade", "")
                if dados
                else ""
            ),

            key="personagem_idade"
        )


        aparencia = st.text_area(
            "Aparência",

            value=(
                dados.get("aparencia", "")
                if dados
                else ""
            ),

            key="personagem_aparencia"
        )


        roupa = st.text_input(
            "Roupa",

            value=(
                dados.get("roupa", "")
                if dados
                else ""
            ),

            key="personagem_roupa"
        )


        personalidade = st.text_area(
            "Personalidade",

            value=(
                dados.get("personalidade", "")
                if dados
                else ""
            ),

            key="personagem_personalidade"
        )


        if st.button(
            "💾 Salvar personagem",
            key="salvar_personagem"
        ):

            if nome.strip():

                salvar_personagem(
                    nome,
                    idade,
                    aparencia,
                    roupa,
                    personalidade
                )


                st.session_state.personagem_atual = {

                    "nome":
                        nome,

                    "idade":
                        idade,

                    "aparencia":
                        aparencia,

                    "roupa":
                        roupa,

                    "personalidade":
                        personalidade,
                }


                st.success(
                    "✅ Personagem salvo."
                )

                st.rerun()


    # ========================================================
    # 🧠 MEMÓRIA
    # ========================================================

    elif ferramenta == "memoria":

        nova = st.text_area(
            "🧠 Salvar nova memória",
            key="memoria_nova"
        )


        if st.button(
            "💾 Salvar memória",
            key="salvar_memoria"
        ):

            if nova.strip():

                salvar_memoria(
                    nova.strip()
                )


                st.success(
                    "✅ Memória salva."
                )

                st.rerun()


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# 💬 CHAT
# ============================================================

pergunta = st.chat_input(
    "Digite sua mensagem para a Alex..."
)


if pergunta:

    pergunta = pergunta.strip()


    if not pergunta:
        st.stop()


    # ========================================================
    # 👤 MOSTRAR MENSAGEM IMEDIATAMENTE
    # ========================================================

    with st.chat_message(
        "user",
        avatar="👤"
    ):

        st.markdown(
            f"""
            <div class="user-message">
                {pergunta}
            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # 💾 SALVAR NO HISTÓRICO
    # ========================================================

    st.session_state.mensagens.append({

        "role":
            "user",

        "content":
            pergunta,
    })


    low = pergunta.lower()


    # ========================================================
    # 🖼️ COMANDO DE IMAGEM
    # ========================================================

    comandos_imagem = (

        "cria uma imagem",
        "criar uma imagem",
        "crie uma imagem",

        "faz uma imagem",
        "fazer uma imagem",
        "faça uma imagem",

        "cria imagem",
        "criar imagem",
        "crie imagem",

        "faz imagem",
        "fazer imagem",
        "faça imagem",
    )


    comando_imagem = any(
        low.startswith(comando)
        for comando in comandos_imagem
    )


    if comando_imagem:

        descricao = pergunta


        for comando in comandos_imagem:

            if low.startswith(comando):

                descricao = pergunta[
                    len(comando):
                ].strip()

                break


        if not descricao:

            st.warning(
                "🖼️ Diga o que você quer na imagem."
            )

            st.stop()


        try:

            with st.chat_message(
                "assistant",
                avatar="✨"
            ):

                st.markdown(
                    """
                    <div class="alex-name">
                        ✨ Alex IA
                    </div>
                    """,
                    unsafe_allow_html=True
                )


                with st.spinner(
                    "🖼️ Criando imagem... aguarde."
                ):

                    sucesso = mostrar_imagem(
                        descricao
                    )


                if sucesso:

                    caminho = (
                        st.session_state.get(
                            "ultima_imagem_caminho"
                        )
                    )


                    st.session_state.mensagens.append({

                        "role":
                            "assistant",

                        "content":
                            "🖼️ Imagem criada.",

                        "tipo":
                            "imagem",

                        "arquivo":
                            caminho,
                    })


                    st.rerun()


                else:

                    st.error(
                        "❌ Não foi possível criar a imagem."
                    )


        except Exception as erro:

            st.error(
                "❌ Erro no gerador de imagem."
            )

            st.code(
                str(erro)
            )


        st.stop()


    # ========================================================
    # 🎬 COMANDO DE VÍDEO
    # ========================================================

    if (
        "vídeo" in low
        or "video" in low
    ):

        descricao = pergunta


        prefixos = (

            "cria um vídeo",
            "criar um vídeo",
            "crie um vídeo",

            "faz um vídeo",
            "fazer um vídeo",
            "faça um vídeo",

            "cria vídeo",
            "criar vídeo",
            "crie vídeo",

            "faz vídeo",
            "fazer vídeo",
            "faça vídeo",

            "video:",
            "vídeo:",
        )


        for prefixo in prefixos:

            if low.startswith(prefixo):

                descricao = pergunta[
                    len(prefixo):
                ].strip()

                break


        if not descricao:

            st.warning(
                "🎬 Diga o que você quer no vídeo."
            )

            st.stop()


        try:

            with st.chat_message(
                "assistant",
                avatar="✨"
            ):

                st.markdown(
                    """
                    <div class="alex-name">
                        ✨ Alex IA
                    </div>
                    """,
                    unsafe_allow_html=True
                )


                with st.spinner(
                    "🎬 Gerando vídeo... aguarde."
                ):

                    resultado = gerar_video(

                        descricao=descricao,

                        camera="Sony FX6",

                        proporcao="16:9",

                        duracao=5,

                        width=512,

                        height=512,
                    )


                # ====================================================
                # 🔎 VALIDAR RESPOSTA DO GERENCIADOR
                # ====================================================

                if resultado is None:

                    st.error(
                        "❌ O gerenciador de vídeo "
                        "não retornou nenhuma resposta."
                    )

                    st.stop()


                if not isinstance(
                    resultado,
                    dict
                ):

                    st.error(
                        "❌ O gerenciador de vídeo "
                        "retornou uma resposta inválida."
                    )

                    st.code(
                        str(resultado)
                    )

                    st.stop()


                # ====================================================
                # 🎬 VÍDEO GERADO
                # ====================================================

                caminho = resultado.get(
                    "video"
                )

                motor_video = resultado.get(
                    "motor",
                    "motor automático"
                )

                sucesso = resultado.get(
                    "sucesso",
                    False
                )

                erro = resultado.get(
                    "erro"
                )


                if sucesso and caminho:

                    caminho = str(
                        caminho
                    )


                    # ================================================
                    # 📁 CONFIRMAR QUE O ARQUIVO EXISTE
                    # ================================================

                    if not os.path.exists(
                        caminho
                    ):

                        st.error(
                            "❌ O motor informou que "
                            "criou o vídeo, mas o "
                            "arquivo não existe."
                        )

                        st.code(
                            caminho
                        )

                        st.stop()


                    st.success(
                        "🎉 Vídeo gerado com sucesso!\n\n"
                        f"🎬 Motor: {motor_video}"
                    )


                    st.video(
                        caminho
                    )


                    st.session_state.mensagens.append({

                        "role":
                            "assistant",

                        "content": (
                            "🎬 Vídeo criado com "
                            f"sucesso usando {motor_video}."
                        ),

                        "tipo":
                            "video",

                        "arquivo":
                            caminho,
                    })


                else:

                    # ================================================
                    # ❌ NENHUM MOTOR CONSEGUIU GERAR
                    # ================================================

                    st.error(
                        "❌ Nenhum vídeo foi gerado."
                    )


                    if erro:

                        st.warning(
                            "Detalhes do erro:"
                        )

                        st.code(
                            str(erro)
                        )


                    # ================================================
                    # 🔎 DIAGNÓSTICO COMPLETO
                    # ================================================

                    st.markdown(
                        "### 🔎 Resposta do gerenciador"
                    )

                    st.json(
                        resultado
                    )


        except Exception as erro_video:

            st.error(
                "❌ O gerador de vídeo "
                "encontrou um erro."
            )

            st.code(
                str(erro_video)
            )


        st.stop()
    # ========================================================
    # 🧠 MEMORIZAR
    # ========================================================

    if low.startswith(
        "memorize:"
    ):

        texto_memoria = pergunta[
            len("memorize:"):
        ].strip()


        if texto_memoria:

            salvar_memoria(
                texto_memoria
            )


        st.success(
            "🧠 Memória salva."
        )

        st.stop()


    # ========================================================
    # 📚 CONTEXTO
    # ========================================================

    contexto = "\n".join(

        f"{m['role']}: {m['content']}"

        for m in st.session_state.mensagens[-20:]

        if m.get("tipo")
        not in (
            "imagem",
            "video"
        )
    )


    instrucao = (

        f"{SYSTEM_PROMPT}\n\n"

        "Responda sempre em português do Brasil.\n\n"

        f"Histórico:\n{contexto}\n\n"

        f"Pergunta:\n{pergunta}"
    )


    # ========================================================
    # 👁️ PREPARAR VISÃO DA ALEX
    # ========================================================

    conteudo_gemini = [
        instrucao
    ]


    if st.session_state.get(
        "imagem_contexto"
    ):

        try:

            from google.genai import types


            imagem_bytes = (
                st.session_state.imagem_contexto
            )


            imagem_mime = (
                st.session_state.get(
                    "imagem_mime"
                )
                or "image/jpeg"
            )


            conteudo_gemini.append(
                types.Part.from_bytes(
                    data=imagem_bytes,
                    mime_type=imagem_mime
                )
            )


        except Exception as erro_imagem:

            st.error(
                "❌ Não foi possível preparar "
                f"a imagem para o Gemini: {erro_imagem}"
            )

            st.stop()


    # ========================================================
    # ✨ GEMINI — RESPOSTA
    # ========================================================

    try:

        with st.spinner(
            "✨ Alex IA está pensando..."
        ):

            # ====================================================
            # 🧠 ULTRA CORE
            # ====================================================

            resultado_ultra = (
                ultra_brain.run(pergunta)
            )


            # ====================================================
            # ✨ RESPOSTA FINAL
            # ====================================================

            if isinstance(
                resultado_ultra,
                dict
            ):

                texto = (
                    resultado_ultra.get(
                        "final_response",
                        ""
                    )
                )

            else:

                texto = (
                    resultado_ultra
                    if isinstance(
                        resultado_ultra,
                        str
                    )
                    else ""
                )


            if not texto:

                texto = (
                    "Não consegui gerar uma resposta."
                )


        # ====================================================
        # ✨ MOSTRAR RESPOSTA DA ALEX
        # ====================================================

        with st.chat_message(
            "assistant",
            avatar="✨"
        ):

            st.markdown(
                """
                <div class="alex-name">
                    ✨ Alex IA
                </div>
                """,
                unsafe_allow_html=True
            )


            st.markdown(
                texto,
                unsafe_allow_html=False
            )


            # ================================================
            # 🔊 VOZ AUTOMÁTICA
            # ================================================

            if st.session_state.usar_voz:

                with st.spinner(
                    "🔊 Alex está falando..."
                ):

                    audio, erro, formato = (
                        gerar_audio(texto)
                    )


                if audio:

                    st.audio(
                        audio,
                        format=formato
                    )

                else:

                    st.warning(
                        "🔊 Não foi possível gerar "
                        f"a voz: {erro}"
                    )


            # ================================================
            # 🔊 BOTÃO PARA OUVIR NOVAMENTE
            # ================================================

            audio_key = (
                "audio_resposta_atual_"
                + str(
                    len(
                        st.session_state.mensagens
                    )
                )
            )


            if st.button(
                "🔊",
                key=audio_key
            ):

                with st.spinner(
                    "🔊 Preparando a voz..."
                ):

                    audio, erro, formato = (
                        gerar_audio(texto)
                    )


                if audio:

                    st.audio(
                        audio,
                        format=formato
                    )

                else:

                    st.error(
                        "❌ Não foi possível gerar "
                        f"a voz: {erro}"
                    )


        # ====================================================
        # 💾 SALVAR RESPOSTA
        # ====================================================

        st.session_state.mensagens.append({

            "role":
                "assistant",

            "content":
                texto,
        })


    except Exception as erro:

        st.error(
            "❌ Erro ao conversar com o Ultra Core: "
            f"{erro}"
        )
