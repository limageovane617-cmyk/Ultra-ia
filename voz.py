# ============================================================
# 🔊 ALEX IA ULTRA — SISTEMA DE VOZ
# Criada por Geovani
# ============================================================

import io
import re
import wave

import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS


# ============================================================
# ⚙️ CONFIGURAÇÃO
# ============================================================

MODELO_VOZ = "gemini-3.1-flash-tts-preview"

VOZ_ALEX = "Kore"


# ============================================================
# 🎵 PCM → WAV
# ============================================================

def pcm_para_wav(audio_pcm):

    arquivo = io.BytesIO()

    with wave.open(arquivo, "wb") as wav:

        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(24000)

        wav.writeframes(audio_pcm)

    return arquivo.getvalue()


# ============================================================
# 🧹 LIMPAR TEXTO
# ============================================================

def limpar_texto(texto):

    if not texto:
        return ""

    return re.sub(
        r"[\*\#\`\_\~\-\>]",
        "",
        texto
    ).strip()


# ============================================================
# 🔊 BACKUP — gTTS
# ============================================================

def gerar_audio_gtts(texto):

    try:

        texto_clean = limpar_texto(texto)

        if not texto_clean:
            return None, "O texto está vazio."

        if len(texto_clean) > 800:
            texto_clean = texto_clean[:800] + "..."

        fp = io.BytesIO()

        tts = gTTS(
            text=texto_clean,
            lang="pt",
            tld="com.br"
        )

        tts.write_to_fp(fp)

        return fp.getvalue(), None

    except Exception as erro:

        return None, str(erro)


# ============================================================
# 🎙️ GEMINI TTS
# ============================================================

def gerar_audio_gemini(texto):

    try:

        texto_clean = limpar_texto(texto)

        if not texto_clean:
            return None, "O texto está vazio."

        api_key = st.secrets["GEMINI_API_KEY"]

        cliente = genai.Client(
            api_key=api_key
        )

        resposta = cliente.models.generate_content(

            model=MODELO_VOZ,

            contents=texto_clean,

            config=types.GenerateContentConfig(

                response_modalities=["AUDIO"],

                speech_config=types.SpeechConfig(

                    voice_config=types.VoiceConfig(

                        prebuilt_voice_config=(
                            types.PrebuiltVoiceConfig(
                                voice_name=VOZ_ALEX
                            )
                        )

                    )

                )

            )

        )

        if not resposta.candidates:
            return None, "O Gemini não retornou candidatos."

        partes = (
            resposta
            .candidates[0]
            .content
            .parts
        )

        for parte in partes:

            if (
                hasattr(parte, "inline_data")
                and parte.inline_data
                and parte.inline_data.data
            ):

                audio_pcm = parte.inline_data.data

                audio_wav = pcm_para_wav(
                    audio_pcm
                )

                return audio_wav, None

        return None, "O Gemini não retornou dados de áudio."

    except Exception as erro:

        print(
            "❌ Erro no Gemini TTS:",
            erro
        )

        return None, str(erro)


# ============================================================
# 🔊 GERAR ÁUDIO
# ============================================================

def gerar_audio(texto):

    if not texto or not texto.strip():

        return (
            None,
            "O texto está vazio.",
            "none"
        )

    # ========================================================
    # 1️⃣ GEMINI TTS
    # ========================================================

    audio_gemini, erro_gemini = (
        gerar_audio_gemini(texto)
    )

    if audio_gemini:

        return (
            audio_gemini,
            None,
            "audio/wav"
        )

    # ========================================================
    # 2️⃣ BACKUP — gTTS
    # ========================================================

    audio_backup, erro_backup = (
        gerar_audio_gtts(texto)
    )

    if audio_backup:

        return (
            audio_backup,
            None,
            "audio/mp3"
        )

    # ========================================================
    # ❌ FALHA TOTAL
    # ========================================================

    return (
        None,
        (
            "Gemini TTS: "
            f"{erro_gemini or 'erro desconhecido'}\n"
            "gTTS: "
            f"{erro_backup or 'erro desconhecido'}"
        ),
        "none"
    )


# ============================================================
# 🔊 MOSTRAR ÁUDIO
# ============================================================

def mostrar_audio(texto):

    try:

        audio, erro, formato = gerar_audio(texto)

        if erro or not audio:

            st.error(
                f"❌ Não foi possível gerar o áudio: {erro}"
            )

            return False

        st.audio(
            audio,
            format=formato
        )

        return True

    except Exception as erro:

        st.error(
            f"❌ Erro ao reproduzir voz: {erro}"
        )

        return False
