"""
Alex IA Ultra — Gerenciador de Vídeo

Motores:
1. Wan 2.2 14B FP8 — R3GM
2. Wan 2.2 14B I2V — Upsampler
3. LTX-2.3 — Hugging Face
4. Magic Hour — LTX-2.3

Sistema:
- Text-to-Video
- Image-to-Video
- Fallback automático
- Detecção de quota / ZeroGPU
- Pausa automática de motores indisponíveis
- Token Hugging Face
- Token Magic Hour
- Compatibilidade com app.py
"""

from __future__ import annotations

import os
import random
import re
import time
from pathlib import Path
from typing import Any, Optional

import requests
import streamlit as st

try:
    from gradio_client import Client, handle_file
except Exception:
    Client = None
    handle_file = None


# ============================================================
# CONFIGURAÇÃO
# ============================================================

NOME_MODULO = "Alex IA Ultra — Gerenciador de Vídeo"

DURACAO_PADRAO = 5.0

R3GM_SPACE = "r3gm/wan2-2-fp8da-aoti-preview"

UPSAMPLER_SPACE = "Upsampler/wan-2-2-14b-image-to-video"

LTX_HF_SPACE = "https://lightricks-ltx-2-3.hf.space"

MAGIC_HOUR_BASE_URL = "https://api.magichour.ai/v1"
MAGIC_HOUR_MODELO = "ltx-2.3"
MAGIC_HOUR_RESOLUCAO = "480p"
MAGIC_HOUR_DURACAO = 5

CAMERAS = [
    "Sony FX5",
    "Sony FX6",
    "Canon EOS C80",
    "ARRI Alexa Mini LF",
]

PROPORCOES = [
    "1:1",
    "16:9",
    "9:16",
]

MOTORES_VIDEO = [
    "Wan 2.2 — R3GM",
    "Wan 2.2 — Upsampler",
    "LTX-2.3 — Hugging Face",
    "Magic Hour — LTX-2.3",
]


# ============================================================
# PASTA DE SAÍDA
# ============================================================

PASTA = Path("videos_gerados")
PASTA.mkdir(parents=True, exist_ok=True)

# ============================================================
# WAN 2.2 — COMFYUI
# Integração isolada para teste seguro
# ============================================================

COMFYUI_URL = os.environ.get(
    "COMFYUI_URL",
    "http://127.0.0.1:8188"
).rstrip("/")

WAN_WORKFLOW_PATH = os.environ.get(
    "WAN_WORKFLOW_PATH",
    "wan22_i2v_workflow_49frames.json"
)

WAN_NODE_LOAD_IMAGE = "6"
WAN_NODE_POSITIVE = "3"
WAN_NODE_NEGATIVE = "4"
WAN_NODE_KSAMPLER = "8"
WAN_NODE_I2V = "7"


def _arredondar_wan(valor: int) -> int:
    """Garante dimensões compatíveis com o workflow do Wan."""
    try:
        valor = int(valor)
    except (TypeError, ValueError):
        valor = 704

    valor = max(256, valor)
    return max(16, (valor // 16) * 16)


def _carregar_workflow_wan() -> dict:
    caminho = Path(WAN_WORKFLOW_PATH)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Workflow do Wan 2.2 não encontrado: {caminho}"
        )

    import json

    with caminho.open("r", encoding="utf-8") as arquivo:
        workflow = json.load(arquivo)

    if not isinstance(workflow, dict):
        raise RuntimeError(
            "O workflow do Wan 2.2 não possui formato JSON válido."
        )

    return workflow


def _upload_imagem_comfyui(
    imagem_bytes: bytes,
    nome_arquivo: str,
) -> str:
    """Envia a imagem de referência para o ComfyUI."""

    if not imagem_bytes:
        raise ValueError("Imagem de referência vazia.")

    nome = Path(nome_arquivo or "wan_input.png").name

    resposta = requests.post(
        f"{COMFYUI_URL}/upload/image",
        files={
            "image": (
                nome,
                imagem_bytes,
                "application/octet-stream",
            )
        },
        data={
            "overwrite": "true",
        },
        timeout=120,
    )

    resposta.raise_for_status()

    dados = resposta.json()

    nome_retornado = str(dados.get("name") or "").strip()
    subpasta = str(dados.get("subfolder") or "").strip()

    if not nome_retornado:
        raise RuntimeError(
            f"ComfyUI não retornou o nome da imagem: {dados}"
        )

    if subpasta:
        return f"{subpasta}/{nome_retornado}"

    return nome_retornado


def _extrair_saida_comfyui(
    historico: dict,
) -> Optional[str]:
    """
    Procura o vídeo gerado pelo SaveVideo dentro
    do histórico retornado pelo ComfyUI.
    """

    if not isinstance(historico, dict):
        return None

    outputs = historico.get("outputs", {})

    if not isinstance(outputs, dict):
        return None

    for dados_node in outputs.values():

        if not isinstance(dados_node, dict):
            continue

        for chave in (
            "videos",
            "gifs",
            "images",
        ):
            arquivos = dados_node.get(chave)

            if not isinstance(arquivos, list):
                continue

            for arquivo in arquivos:

                if not isinstance(arquivo, dict):
                    continue

                filename = str(
                    arquivo.get("filename") or ""
                ).strip()

                if not filename:
                    continue

                if not filename.lower().endswith(".mp4"):
                    continue

                subfolder = str(
                    arquivo.get("subfolder") or ""
                ).strip()

                tipo = str(
                    arquivo.get("type") or "output"
                ).strip()

                params = {
                    "filename": filename,
                    "type": tipo,
                }

                if subfolder:
                    params["subfolder"] = subfolder

                from urllib.parse import urlencode

                return (
                    f"{COMFYUI_URL}/view?"
                    f"{urlencode(params)}"
                )

    return None


def gerar_wan_comfyui(
    imagem_bytes: bytes,
    imagem_nome: str,
    prompt: str,
    negative_prompt: Optional[str] = None,
    width: int = 704,
    height: int = 1248,
    seed: Optional[int] = None,
    timeout: int = 900,
) -> dict[str, Any]:
    """
    Gera vídeo usando o workflow validado do Wan 2.2
    através de uma instância ComfyUI.

    IMPORTANTE:
    Esta função é isolada inicialmente.
    Ela NÃO altera o fallback existente.
    """

    import copy
    import json
    import uuid

    inicio = time.time()

    try:
        # ----------------------------------------------------
        # 1. Carregar workflow validado
        # ----------------------------------------------------

        workflow = _carregar_workflow_wan()

        # Trabalhamos em uma cópia para nunca alterar
        # o arquivo JSON original.
        workflow = copy.deepcopy(workflow)

        # ----------------------------------------------------
        # 2. Enviar imagem para o ComfyUI
        # ----------------------------------------------------

        imagem_comfy = _upload_imagem_comfyui(
            imagem_bytes,
            imagem_nome,
        )

        # ----------------------------------------------------
        # 3. Atualizar somente os parâmetros necessários
        # ----------------------------------------------------

        if WAN_NODE_LOAD_IMAGE not in workflow:
            raise RuntimeError(
                f"Nó {WAN_NODE_LOAD_IMAGE} (LoadImage) "
                "não encontrado no workflow."
            )

        if WAN_NODE_POSITIVE not in workflow:
            raise RuntimeError(
                f"Nó {WAN_NODE_POSITIVE} (positive) "
                "não encontrado no workflow."
            )

        if WAN_NODE_NEGATIVE not in workflow:
            raise RuntimeError(
                f"Nó {WAN_NODE_NEGATIVE} (negative) "
                "não encontrado no workflow."
            )

        if WAN_NODE_KSAMPLER not in workflow:
            raise RuntimeError(
                f"Nó {WAN_NODE_KSAMPLER} (KSampler) "
                "não encontrado no workflow."
            )

        if WAN_NODE_I2V not in workflow:
            raise RuntimeError(
                f"Nó {WAN_NODE_I2V} (Wan I2V) "
                "não encontrado no workflow."
            )

        # Imagem de referência
        workflow[WAN_NODE_LOAD_IMAGE]["inputs"]["image"] = imagem_comfy

        # Prompt
        workflow[WAN_NODE_POSITIVE]["inputs"]["text"] = (
            prompt or ""
        )

        # Negative prompt
        workflow[WAN_NODE_NEGATIVE]["inputs"]["text"] = (
            negative_prompt
            or montar_negative_prompt()
        )

        # Seed
        if seed is None:
            seed = random.randint(1, 2_147_483_647)

        workflow[WAN_NODE_KSAMPLER]["inputs"]["seed"] = int(seed)

        # ----------------------------------------------------
        # 4. Dimensões
        # ----------------------------------------------------

        width = _arredondar_wan(width)
        height = _arredondar_wan(height)

        workflow[WAN_NODE_I2V]["inputs"]["width"] = width
        workflow[WAN_NODE_I2V]["inputs"]["height"] = height

        # ----------------------------------------------------
        # 5. Enviar workflow para ComfyUI
        # ----------------------------------------------------

        client_id = str(uuid.uuid4())

        resposta = requests.post(
            f"{COMFYUI_URL}/prompt",
            json={
                "prompt": workflow,
                "client_id": client_id,
            },
            timeout=120,
        )

        resposta.raise_for_status()

        dados_prompt = resposta.json()

        prompt_id = str(
            dados_prompt.get("prompt_id") or ""
        ).strip()

        if not prompt_id:
            raise RuntimeError(
                "ComfyUI não retornou prompt_id: "
                + json.dumps(dados_prompt, ensure_ascii=False)
            )

        # ----------------------------------------------------
        # 6. Esperar geração
        # ----------------------------------------------------

        limite = time.time() + timeout

        while time.time() < limite:

            time.sleep(2)

            resposta_historico = requests.get(
                f"{COMFYUI_URL}/history/{prompt_id}",
                timeout=60,
            )

            resposta_historico.raise_for_status()

            historico_total = resposta_historico.json()

            historico = historico_total.get(prompt_id)

            if not historico:
                continue

            # Se o ComfyUI registrou erro
            status = historico.get("status", {})

            if isinstance(status, dict):
                mensagens = status.get("messages", [])

                texto_status = str(mensagens)

                if (
                    "error" in texto_status.lower()
                    or "failed" in texto_status.lower()
                ):
                    raise RuntimeError(
                        f"ComfyUI informou erro: {texto_status}"
                    )

            # Procurar MP4
            video_url = _extrair_saida_comfyui(
                historico
            )

            if not video_url:
                continue

            # ------------------------------------------------
            # 7. Baixar MP4 para videos_gerados
            # ------------------------------------------------

            destino = _nome_saida("wan22_comfyui")

            resposta_video = requests.get(
                video_url,
                timeout=300,
            )

            resposta_video.raise_for_status()

            destino.write_bytes(
                resposta_video.content
            )

            if (
                not destino.exists()
                or destino.stat().st_size <= 0
            ):
                raise RuntimeError(
                    "O vídeo gerado pelo ComfyUI está vazio."
                )

            return {
                "sucesso": True,
                "video": str(destino),
                "motor": "Wan 2.2 — ComfyUI",
                "erro": "",
                "prompt_id": prompt_id,
                "seed": seed,
                "width": width,
                "height": height,
                "tempo": round(
                    time.time() - inicio,
                    2,
                ),
            }

        raise TimeoutError(
            "O Wan 2.2 via ComfyUI não terminou "
            f"dentro de {timeout} segundos."
        )

    except Exception as erro:

        _registrar_erro_motor(
            "Wan 2.2 — ComfyUI",
            erro,
        )

        return {
            "sucesso": False,
            "video": None,
            "motor": "Wan 2.2 — ComfyUI",
            "erro": str(erro),
            }


# ============================================================
# CONTROLE DE MOTORES
# ============================================================

PAUSA_PADRAO_MINUTOS = 30
PAUSA_QUOTA_MINUTOS = 30
PAUSA_AUTORIZACAO_MINUTOS = 60
PAUSA_ERRO_TEMPORARIO_MINUTOS = 10


def _estado_motores() -> dict[str, dict[str, Any]]:
    if "video_motores_bloqueados" not in st.session_state:
        st.session_state.video_motores_bloqueados = {}

    return st.session_state.video_motores_bloqueados


def _pausar_motor(nome: str, minutos: int, motivo: str) -> None:
    estado = _estado_motores()

    estado[nome] = {
        "ate": time.time() + (minutos * 60),
        "motivo": str(motivo),
    }


def _motor_pausado(nome: str) -> bool:
    estado = _estado_motores()
    dados = estado.get(nome)

    if not dados:
        return False

    ate = dados.get("ate", 0)

    if time.time() >= ate:
        estado.pop(nome, None)
        return False

    return True


def _motivo_pausa(nome: str) -> str:
    dados = _estado_motores().get(nome)

    if not dados:
        return ""

    return str(dados.get("motivo", ""))


def _tempo_restante(nome: str) -> int:
    dados = _estado_motores().get(nome)

    if not dados:
        return 0

    restante = dados.get("ate", 0) - time.time()

    return max(0, int(restante))


# ============================================================
# SECRETS
# ============================================================

def _secret(nome: str) -> str:
    try:
        valor = st.secrets.get(nome, "")
    except Exception:
        valor = ""

    if not valor:
        valor = os.environ.get(nome, "")

    return str(valor or "").strip()


def obter_api_key_magichour() -> str:
    return _secret("MAGIC_HOUR_API_KEY")


def obter_token_huggingface() -> str:
    return _secret("HF_TOKEN") or _secret("HUGGINGFACE_TOKEN")


def obter_token_replicate() -> str:
    return _secret("REPLICATE_API_TOKEN")


def headers_magichour() -> dict[str, str]:
    chave = obter_api_key_magichour()

    if not chave:
        raise RuntimeError(
            "MAGIC_HOUR_API_KEY não foi encontrada."
        )

    return {
        "Authorization": f"Bearer {chave}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


# ============================================================
# UTILIDADES
# ============================================================

def _nome_saida(prefixo: str) -> Path:
    return PASTA / f"{prefixo}_{int(time.time() * 1000)}.mp4"


def _extensao_imagem(nome: str) -> str:
    extensao = Path(nome).suffix.lower()

    if extensao not in (".png", ".jpg", ".jpeg", ".webp"):
        return ".png"

    return extensao


def _salvar_imagem_temp(
    imagem_bytes: bytes,
    nome: str,
    prefixo: str,
) -> Path:
    if not imagem_bytes:
        raise ValueError("Imagem vazia.")

    extensao = _extensao_imagem(nome)

    caminho = (
        PASTA
        / f"{prefixo}_{int(time.time() * 1000)}{extensao}"
    )

    caminho.write_bytes(imagem_bytes)

    return caminho


def _duracao_segura(valor: float) -> float:
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        valor = DURACAO_PADRAO

    return max(1.0, min(valor, 5.0))


def _normalizar_proporcao(proporcao: str) -> str:
    if proporcao not in PROPORCOES:
        return "16:9"

    return proporcao


def _ajustar_dimensoes_por_proporcao(
    width: int,
    height: int,
    proporcao: str,
) -> tuple[int, int]:
    proporcao = _normalizar_proporcao(proporcao)

    try:
        width = max(256, int(width))
        height = max(256, int(height))
    except (TypeError, ValueError):
        width, height = 512, 512

    if proporcao == "16:9":
        return width, max(256, int(width * 9 / 16))

    if proporcao == "9:16":
        return max(256, int(height * 9 / 16)), height

    return width, height


# ============================================================
# PROMPT
# ============================================================

def montar_prompt(
    movimento: str,
    camera: str = "Sony FX6",
) -> str:
    movimento = (movimento or "").strip()

    return f"""
Animate the provided reference image into a realistic
cinematic image-to-video sequence.

MAIN MOTION:
{movimento}

CAMERA:
{camera}

CHARACTER CONSISTENCY IS EXTREMELY IMPORTANT.

Keep exactly the same person or character from the input image.

Preserve:
- exact face
- facial identity
- hairstyle
- hair color
- clothing
- clothing colors
- body proportions
- accessories
- skin tone
- character identity
- environment whenever possible

The character must remain consistent throughout the clip.

Only animate the requested movement.

The movement must be smooth, natural and physically plausible.

Maintain temporal consistency from the first frame to the last frame.

Use realistic cinematic lighting and natural motion.

Camera movement should be subtle and cinematic.

Do NOT:
- create another person
- change the face
- change the hairstyle
- change the clothes
- change the body
- duplicate the person
- create extra limbs
- change the character identity
- add another person

Do not add subtitles.
Do not add text.
Do not add logos.
Do not add watermarks.
""".strip()


def montar_negative_prompt() -> str:
    return (
        "static image, frozen character, blurry, low quality, "
        "distorted face, different person, different face, "
        "different clothes, changed hairstyle, duplicate person, "
        "duplicate body, extra person, extra arms, extra legs, "
        "extra fingers, deformed hands, bad anatomy, warped face, "
        "flickering, morphing, identity change, text, subtitles, "
        "watermark, logo"
    )


# ============================================================
# EXTRAIR VÍDEO
# ============================================================

def _extrair_video_gradio(resultado: Any) -> Optional[str]:
    if resultado is None:
        return None

    if isinstance(resultado, str):
        valor = resultado.strip()

        if not valor:
            return None

        if (
            valor.startswith(("http://", "https://"))
            or valor.lower().endswith(".mp4")
            or Path(valor).exists()
        ):
            return valor

        return None

    if isinstance(resultado, dict):
        for chave in (
            "video",
            "output",
            "path",
            "url",
            "video_path",
            "file",
            "file_path",
            "value",
        ):
            if chave not in resultado:
                continue

            encontrado = _extrair_video_gradio(
                resultado.get(chave)
            )

            if encontrado:
                return encontrado

        return None

    if isinstance(resultado, (list, tuple)):
        for item in resultado:
            encontrado = _extrair_video_gradio(item)

            if encontrado:
                return encontrado

    return None


# ============================================================
# SALVAR VÍDEO
# ============================================================

def _salvar_video_gradio(
    origem: str,
    destino: Path,
) -> str:
    if not origem:
        raise RuntimeError("Origem do vídeo está vazia.")

    origem = str(origem)

    if Path(origem).exists():
        destino.write_bytes(Path(origem).read_bytes())

    elif origem.startswith(("http://", "https://")):
        resposta = requests.get(origem, timeout=300)
        resposta.raise_for_status()
        destino.write_bytes(resposta.content)

    else:
        raise RuntimeError(f"Vídeo não acessível: {origem}")

    if not destino.exists() or destino.stat().st_size <= 0:
        raise RuntimeError("O vídeo retornado está vazio.")

    return str(destino)


# ============================================================
# DETECÇÃO DE QUOTA
# ============================================================

def _erro_e_quota(erro: Exception | str) -> bool:
    texto = str(erro).lower()

    palavras = (
        "zerogpu",
        "quota",
        "exceeded",
        "rate limit",
        "too many requests",
        "try again in",
        "requested vs.",
        "daily limit",
        "zero gpu",
    )

    return any(palavra in texto for palavra in palavras)


def _extrair_tempo_quota(texto: str) -> Optional[int]:
    encontrados = re.findall(
        r"try again in\s+(\d+):(\d+):(\d+)",
        str(texto),
        flags=re.IGNORECASE,
    )

    if not encontrados:
        return None

    horas, minutos, segundos = encontrados[0]

    total = (
        int(horas) * 3600
        + int(minutos) * 60
        + int(segundos)
    )

    return max(1, (total // 60) + 1)


def _registrar_erro_motor(
    nome: str,
    erro: Exception | str,
) -> None:
    texto = str(erro)
    texto_lower = texto.lower()

    if _erro_e_quota(texto):
        minutos = _extrair_tempo_quota(texto)

        if minutos is None:
            minutos = PAUSA_QUOTA_MINUTOS

        _pausar_motor(nome, minutos, texto)
        return

    erro_autorizacao = (
        "401" in texto_lower
        or "unauthorized" in texto_lower
        or "authentication" in texto_lower
        or "api key" in texto_lower
        or ("token" in texto_lower and "invalid" in texto_lower)
    )

    if erro_autorizacao:
        _pausar_motor(
            nome,
            PAUSA_AUTORIZACAO_MINUTOS,
            texto,
        )
        return

    erro_temporario = (
        "timeout" in texto_lower
        or "temporarily" in texto_lower
        or "503" in texto_lower
        or "502" in texto_lower
        or "500" in texto_lower
        or "connection" in texto_lower
    )

    if erro_temporario:
        _pausar_motor(
            nome,
            PAUSA_ERRO_TEMPORARIO_MINUTOS,
            texto,
        )


# ============================================================
# MOTOR 1 — WAN 2.2 R3GM
# ============================================================

def gerar_r3gm(
    imagem_bytes: bytes,
    nome_imagem: str,
    movimento: str,
    camera: str = "Sony FX6",
    duracao: float = 5.0,
) -> dict[str, Any]:
    nome_motor = "Wan 2.2 — R3GM"

    if _motor_pausado(nome_motor):
        raise RuntimeError(
            "Motor pausado temporariamente: "
            + _motivo_pausa(nome_motor)
        )

    if Client is None:
        raise RuntimeError("gradio_client não está instalado.")

    if handle_file is None:
        raise RuntimeError("handle_file não está disponível.")

    if not imagem_bytes:
        raise ValueError("O R3GM precisa de uma imagem.")

    entrada = _salvar_imagem_temp(
        imagem_bytes,
        nome_imagem,
        "entrada_r3gm",
    )

    prompt = montar_prompt(movimento, camera)

    seed = random.randint(0, 2147483647)
    duracao_segundos = _duracao_segura(duracao)

    try:
        client = Client(R3GM_SPACE)

        resultado = client.predict(
            input_image=handle_file(str(entrada)),
            last_image=None,
            prompt=prompt,
            steps=4,
            negative_prompt=montar_negative_prompt(),
            duration_seconds=duracao_segundos,
            guidance_scale=1.0,
            guidance_scale_2=1.0,
            seed=seed,
            randomize_seed=True,
            quality=5,
            scheduler="UniPCMultistep",
            flow_shift=3.0,
            frame_multiplier=16,
            video_component=True,
            api_name="/generate_video",
        )

    except Exception as erro:
        _registrar_erro_motor(nome_motor, erro)
        raise

    video = _extrair_video_gradio(resultado)

    if not video:
        raise RuntimeError("R3GM não retornou vídeo.")

    destino = _nome_saida("video_r3gm")
    caminho = _salvar_video_gradio(video, destino)

    return {
        "sucesso": True,
        "success": True,
        "motor": nome_motor,
        "video": caminho,
        "video_url": caminho,
        "arquivo": caminho,
        "arquivo_video": caminho,
        "duracao": duracao_segundos,
        "fallback": False,
        "erro": None,
    }


# ============================================================
# MOTOR 2 — WAN 2.2 UPSAMPLER
# ============================================================

def gerar_upsampler(
    imagem_bytes: bytes,
    nome_imagem: str,
    movimento: str,
    camera: str = "Sony FX6",
    duracao: float = 5.0,
) -> dict[str, Any]:
    nome_motor = "Wan 2.2 — Upsampler"

    if _motor_pausado(nome_motor):
        raise RuntimeError(
            "Motor pausado temporariamente: "
            + _motivo_pausa(nome_motor)
        )

    if Client is None:
        raise RuntimeError("gradio_client não está instalado.")

    if handle_file is None:
        raise RuntimeError("handle_file não está disponível.")

    if not imagem_bytes:
        raise ValueError("O Upsampler precisa de uma imagem.")

    entrada = _salvar_imagem_temp(
        imagem_bytes,
        nome_imagem,
        "entrada_upsampler",
    )

    prompt = montar_prompt(movimento, camera)
    duracao_segundos = _duracao_segura(duracao)

    try:
        client = Client(UPSAMPLER_SPACE)

        resultado = client.predict(
            input_image=handle_file(str(entrada)),
            prompt=prompt,
            steps=4,
            negative_prompt=montar_negative_prompt(),
            duration_seconds=duracao_segundos,
            guidance_scale=1.0,
            seed=random.randint(0, 2147483647),
            randomize_seed=True,
            api_name="/generate_video",
        )

    except Exception as erro:
        _registrar_erro_motor(nome_motor, erro)
        raise

    video = _extrair_video_gradio(resultado)

    if not video:
        raise RuntimeError("Upsampler não retornou vídeo.")

    destino = _nome_saida("video_upsampler")
    caminho = _salvar_video_gradio(video, destino)

    return {
        "sucesso": True,
        "success": True,
        "motor": nome_motor,
        "video": caminho,
        "video_url": caminho,
        "arquivo": caminho,
        "arquivo_video": caminho,
        "duracao": duracao_segundos,
        "fallback": True,
        "erro": None,
    }


# ============================================================
# MOTOR 3 — LTX-2.3 HUGGING FACE
# ============================================================

def gerar_ltx_huggingface(
    prompt: str,
    duration: float = 5.0,
    height: int = 512,
    width: int = 512,
    imagem_bytes: Optional[bytes] = None,
    nome_imagem: str = "imagem.png",
) -> dict[str, Any]:
    nome_motor = "LTX-2.3 — Hugging Face"

    if _motor_pausado(nome_motor):
        raise RuntimeError(
            "Motor pausado temporariamente: "
            + _motivo_pausa(nome_motor)
        )

    if Client is None:
        raise RuntimeError("gradio_client não está instalado.")

    prompt = (prompt or "").strip()

    if not prompt:
        raise ValueError("O prompt está vazio.")

    caminho_imagem = None

    if imagem_bytes:
        caminho_imagem = _salvar_imagem_temp(
            imagem_bytes,
            nome_imagem,
            "entrada_ltx",
        )

    token_hf = obter_token_huggingface()

    print("[LTX] Token Hugging Face:", bool(token_hf))

    try:
        if token_hf:
            try:
                client = Client(
                    LTX_HF_SPACE,
                    token=token_hf,
                )
            except TypeError:
                client = Client(
                    LTX_HF_SPACE,
                    hf_token=token_hf,
                )
        else:
            client = Client(LTX_HF_SPACE)

    except Exception as erro:
        _registrar_erro_motor(nome_motor, erro)
        raise

    duracao_segundos = _duracao_segura(duration)

    if caminho_imagem:
        imagem_input = (
            handle_file(str(caminho_imagem))
            if handle_file
            else str(caminho_imagem)
        )
    else:
        imagem_input = None

    try:
        resultado = client.predict(
            input_image=imagem_input,
            prompt=prompt,
            duration=duracao_segundos,
            enhance_prompt=True,
            seed=random.randint(0, 2147483647),
            randomize_seed=True,
            height=int(height),
            width=int(width),
            api_name="/generate_video",
        )

    except Exception as erro:
        _registrar_erro_motor(nome_motor, erro)
        raise

    video = _extrair_video_gradio(resultado)

    if not video:
        raise RuntimeError("LTX-2.3 não retornou vídeo.")

    destino = _nome_saida("video_ltx")
    caminho = _salvar_video_gradio(video, destino)

    return {
        "sucesso": True,
        "success": True,
        "motor": nome_motor,
        "video": caminho,
        "video_url": caminho,
        "arquivo": caminho,
        "arquivo_video": caminho,
        "duracao": duracao_segundos,
        "fallback": True,
        "erro": None,
    }


# ============================================================
# MOTOR 4 — MAGIC HOUR
# ============================================================

def obter_url_upload(extensao: str) -> tuple[str, str]:
    ext = str(extensao).lower().replace(".", "")

    resposta = requests.post(
        f"{MAGIC_HOUR_BASE_URL}/files/upload-urls",
        headers=headers_magichour(),
        json={
            "items": [
                {
                    "type": "image",
                    "extension": ext,
                }
            ]
        },
        timeout=60,
    )

    if resposta.status_code != 200:
        raise RuntimeError(
            f"Magic Hour HTTP {resposta.status_code}: "
            f"{resposta.text}"
        )

    dados = resposta.json()
    itens = dados.get("items") or []

    if not itens:
        raise RuntimeError(
            "Magic Hour não retornou URL de upload."
        )

    item = itens[0]

    upload_url = item.get("upload_url")
    file_path = item.get("file_path")

    if not upload_url or not file_path:
        raise RuntimeError(
            "Magic Hour retornou upload incompleto."
        )

    return upload_url, file_path


def enviar_imagem_magichour(
    imagem_bytes: bytes,
    nome: str,
) -> str:
    if not imagem_bytes:
        raise ValueError("Imagem vazia.")

    ext = (
        Path(nome)
        .suffix
        .lower()
        .replace(".", "")
        or "png"
    )

    upload_url, file_path = obter_url_upload(ext)

    resposta = requests.put(
        upload_url,
        data=imagem_bytes,
        timeout=120,
    )

    if resposta.status_code not in (200, 201, 204):
        raise RuntimeError(
            "Falha no upload Magic Hour: "
            f"HTTP {resposta.status_code}"
        )

    return file_path


def encontrar_url_video(dados: Any) -> Optional[str]:
    if isinstance(dados, str):
        if dados.startswith(("http://", "https://")):
            return dados

        return None

    if isinstance(dados, dict):
        for chave in (
            "video_url",
            "download_url",
            "output_url",
            "url",
            "video",
        ):
            valor = dados.get(chave)
            encontrado = encontrar_url_video(valor)

            if encontrado:
                return encontrado

        for valor in dados.values():
            encontrado = encontrar_url_video(valor)

            if encontrado:
                return encontrado

    elif isinstance(dados, (list, tuple)):
        for item in dados:
            encontrado = encontrar_url_video(item)

            if encontrado:
                return encontrado

    return None


def gerar_magichour(
    imagem_bytes: bytes,
    nome_arquivo: str,
    prompt: str,
) -> dict[str, Any]:
    nome_motor = "Magic Hour — LTX-2.3"

    if _motor_pausado(nome_motor):
        raise RuntimeError(
            "Motor pausado temporariamente: "
            + _motivo_pausa(nome_motor)
        )

    if not imagem_bytes:
        raise ValueError("Magic Hour precisa de imagem.")

    file_path = enviar_imagem_magichour(
        imagem_bytes,
        nome_arquivo,
    )

    dados = {
        "name": "Alex IA Ultra",
        "end_seconds": MAGIC_HOUR_DURACAO,
        "model": MAGIC_HOUR_MODELO,
        "resolution": MAGIC_HOUR_RESOLUCAO,
        "audio": False,
        "style": {
            "prompt": prompt,
        },
        "assets": {
            "image_file_path": file_path,
        },
    }

    try:
        resposta = requests.post(
            f"{MAGIC_HOUR_BASE_URL}/image-to-video",
            headers=headers_magichour(),
            json=dados,
            timeout=120,
        )

        if resposta.status_code not in (200, 201, 202):
            raise RuntimeError(
                f"Magic Hour HTTP {resposta.status_code}: "
                f"{resposta.text}"
            )

        resultado = resposta.json()
        projeto = resultado.get("id")

        if not projeto:
            raise RuntimeError(
                "Magic Hour não retornou ID."
            )

        inicio = time.time()

        while time.time() - inicio < 300:
            resposta = requests.get(
                f"{MAGIC_HOUR_BASE_URL}/video-projects/{projeto}",
                headers=headers_magichour(),
                timeout=60,
            )

            if resposta.status_code == 200:
                dados_status = resposta.json()
                url = encontrar_url_video(dados_status)

                if url:
                    video = requests.get(
                        url,
                        timeout=180,
                    )

                    video.raise_for_status()

                    if not video.content:
                        raise RuntimeError(
                            "Magic Hour retornou vídeo vazio."
                        )

                    caminho = _nome_saida(
                        "video_magichour"
                    )

                    caminho.write_bytes(video.content)

                    return {
                        "sucesso": True,
                        "success": True,
                        "motor": nome_motor,
                        "video": str(caminho),
                        "video_url": str(caminho),
                        "arquivo": str(caminho),
                        "arquivo_video": str(caminho),
                        "duracao": MAGIC_HOUR_DURACAO,
                        "fallback": True,
                        "erro": None,
                    }

            time.sleep(5)

    except Exception as erro:
        _registrar_erro_motor(nome_motor, erro)
        raise

    raise RuntimeError(
        "Magic Hour demorou mais de 300 segundos."
    )


# ============================================================
# FALLBACK PRINCIPAL
# ============================================================

def gerar_video_automatico(
    prompt: Optional[str] = None,
    imagem_bytes: Optional[bytes] = None,
    nome_imagem: str = "imagem.png",
    duracao: float = 5.0,
    width: int = 512,
    height: int = 512,
    descricao: Optional[str] = None,
    camera: str = "Sony FX6",
    proporcao: str = "16:9",
    **kwargs: Any,
) -> dict[str, Any]:
    texto = (prompt or descricao or "").strip()

    if not texto:
        return {
            "sucesso": False,
            "success": False,
            "video": None,
            "video_url": None,
            "arquivo": None,
            "arquivo_video": None,
            "motor": None,
            "duracao": _duracao_segura(duracao),
            "erro": "O movimento está vazio.",
            "erros": [],
        }

    erros: list[str] = []

    duracao_segura = _duracao_segura(duracao)
    proporcao = _normalizar_proporcao(proporcao)
    width, height = _ajustar_dimensoes_por_proporcao(
        width,
        height,
        proporcao,
    )

    # ========================================================
    # 1 — R3GM
    # ========================================================

    if imagem_bytes:
        nome_motor = "Wan 2.2 — R3GM"

        if not _motor_pausado(nome_motor):
            try:
                resultado = gerar_r3gm(
                    imagem_bytes,
                    nome_imagem,
                    texto,
                    camera,
                    duracao_segura,
                )

                resultado["erros_anteriores"] = erros
                return resultado

            except Exception as erro:
                erros.append(f"R3GM: {erro}")
        else:
            erros.append(
                "R3GM: motor pausado — "
                + _motivo_pausa(nome_motor)
            )
    else:
        erros.append("R3GM: precisa de imagem.")

    # ========================================================
    # 2 — Upsampler
    # ========================================================

    if imagem_bytes:
        nome_motor = "Wan 2.2 — Upsampler"

        if not _motor_pausado(nome_motor):
            try:
                resultado = gerar_upsampler(
                    imagem_bytes,
                    nome_imagem,
                    texto,
                    camera,
                    duracao_segura,
                )

                resultado["erros_anteriores"] = erros
                return resultado

            except Exception as erro:
                erros.append(f"Upsampler: {erro}")
        else:
            erros.append(
                "Upsampler: motor pausado — "
                + _motivo_pausa(nome_motor)
            )
    else:
        erros.append("Upsampler: precisa de imagem.")

    # ========================================================
    # 3 — LTX-2.3
    # ========================================================

    nome_motor = "LTX-2.3 — Hugging Face"

    if not _motor_pausado(nome_motor):
        try:
            prompt_ltx = (
                montar_prompt(texto, camera)
                if imagem_bytes
                else texto
            )

            resultado = gerar_ltx_huggingface(
                prompt=prompt_ltx,
                duration=duracao_segura,
                height=height,
                width=width,
                imagem_bytes=imagem_bytes,
                nome_imagem=nome_imagem,
            )

            resultado["erros_anteriores"] = erros
            return resultado

        except Exception as erro:
            erros.append(f"LTX-2.3: {erro}")
    else:
        erros.append(
            "LTX-2.3: motor pausado — "
            + _motivo_pausa(nome_motor)
        )

    # ========================================================
    # 4 — Magic Hour
    # ========================================================

    nome_motor = "Magic Hour — LTX-2.3"

    if imagem_bytes:
        if not _motor_pausado(nome_motor):
            if obter_api_key_magichour():
                try:
                    resultado = gerar_magichour(
                        imagem_bytes,
                        nome_imagem,
                        montar_prompt(texto, camera),
                    )

                    resultado["erros_anteriores"] = erros
                    return resultado

                except Exception as erro:
                    erros.append(f"Magic Hour: {erro}")
            else:
                erros.append(
                    "Magic Hour: "
                    "MAGIC_HOUR_API_KEY não configurada."
                )
        else:
            erros.append(
                "Magic Hour: motor pausado — "
                + _motivo_pausa(nome_motor)
            )
    else:
        erros.append("Magic Hour: precisa de imagem.")

    # ========================================================
    # NENHUM MOTOR
    # ========================================================

    mensagem = (
        "❌ NENHUM MOTOR DE VÍDEO "
        "CONSEGUIU GERAR O VÍDEO.\n\n"
        + "\n\n".join(erros)
    )

    return {
        "sucesso": False,
        "success": False,
        "video": None,
        "video_url": None,
        "arquivo": None,
        "arquivo_video": None,
        "motor": None,
        "duracao": duracao_segura,
        "erro": mensagem,
        "erros": erros,
    }


# ============================================================
# COMPATIBILIDADE COM APP.PY
# ============================================================

def gerar_video(
    prompt: Optional[str] = None,
    imagem_bytes: Optional[bytes] = None,
    nome_imagem: str = "imagem.png",
    duracao: float = 5.0,
    width: int = 512,
    height: int = 512,
    descricao: Optional[str] = None,
    camera: str = "Sony FX6",
    proporcao: str = "16:9",
    **kwargs: Any,
) -> dict[str, Any]:
    return gerar_video_automatico(
        prompt=prompt,
        imagem_bytes=imagem_bytes,
        nome_imagem=nome_imagem,
        duracao=duracao,
        width=width,
        height=height,
        descricao=descricao,
        camera=camera,
        proporcao=proporcao,
        **kwargs,
    )


def gerar_video_texto(
    prompt: str,
    duracao: float = 5.0,
    **kwargs: Any,
) -> dict[str, Any]:
    return gerar_video(
        prompt=prompt,
        duracao=duracao,
        **kwargs,
    )


def gerar_video_imagem(
    imagem_bytes: bytes,
    nome_imagem: str,
    prompt: str,
    duracao: float = 5.0,
    **kwargs: Any,
) -> dict[str, Any]:
    return gerar_video(
        prompt=prompt,
        imagem_bytes=imagem_bytes,
        nome_imagem=nome_imagem,
        duracao=duracao,
        **kwargs,
    )


def gerar(
    prompt: str,
    **kwargs: Any,
) -> dict[str, Any]:
    return gerar_video(
        prompt,
        **kwargs,
    )


def gerar_video_fallback(
    prompt: str,
    **kwargs: Any,
) -> Optional[str]:
    resultado = gerar_video(
        prompt,
        **kwargs,
    )

    return (
        resultado.get("video")
        or resultado.get("arquivo")
    )


# ============================================================
# CONFIGURAÇÃO DO APP.PY
# ============================================================

def mostrar_configuracao_video() -> tuple[str, str, float]:
    st.subheader("🎬 Configuração de Vídeo")

    camera_video = st.selectbox(
        "📷 Câmera",
        CAMERAS,
        index=1,
        key="video_camera",
    )

    proporcao_video = st.selectbox(
        "📐 Proporção",
        PROPORCOES,
        index=1,
        key="video_proporcao",
    )

    duracao_video = st.number_input(
        "⏱️ Duração do vídeo",
        min_value=1.0,
        max_value=5.0,
        value=5.0,
        step=0.5,
        key="video_duracao",
    )

    st.write("**🎥 Motores disponíveis:**")

    for motor in MOTORES_VIDEO:
        if _motor_pausado(motor):
            restante = _tempo_restante(motor)
            minutos = restante // 60
            segundos = restante % 60

            st.write(
                f"• {motor} ⏸️ "
                f"({minutos}m {segundos}s)"
            )
        else:
            st.write(f"• {motor} ✅")

    return (
        camera_video,
        proporcao_video,
        duracao_video,
    )


# ============================================================
# STATUS
# ============================================================

def verificar_magic_hour() -> tuple[bool, str]:
    try:
        chave = obter_api_key_magichour()

        if chave:
            return (
                True,
                "✅ MAGIC_HOUR_API_KEY encontrada.",
            )

        return (
            False,
            "❌ MAGIC_HOUR_API_KEY não encontrada.",
        )

    except Exception as erro:
        return False, f"❌ Erro: {erro}"


def status_video() -> dict[str, Any]:
    status: dict[str, Any] = {}

    for motor in MOTORES_VIDEO:
        status[motor] = {
            "disponivel": not _motor_pausado(motor),
            "tempo_restante": _tempo_restante(motor),
            "motivo": _motivo_pausa(motor),
        }

    status["gradio_client"] = Client is not None
    status["magic_hour"] = bool(obter_api_key_magichour())
    status["huggingface"] = bool(obter_token_huggingface())
    status["replicate"] = bool(obter_token_replicate())
    status["ltx"] = LTX_HF_SPACE

    return status


# ============================================================
# LIMPAR PAUSAS
# ============================================================

def limpar_bloqueios_video() -> None:
    st.session_state["video_motores_bloqueados"] = {}


# ============================================================
# EXPORTAÇÕES
# ============================================================

__all__ = [
    "NOME_MODULO",
    "MOTORES_VIDEO",
    "CAMERAS",
    "PROPORCOES",
    "DURACAO_PADRAO",
    "gerar_video",
    "gerar_video_automatico",
    "gerar_video_fallback",
    "gerar",
    "gerar_video_texto",
    "gerar_video_imagem",
    "gerar_r3gm",
    "gerar_upsampler",
    "gerar_ltx_huggingface",
    "gerar_magichour",
    "mostrar_configuracao_video",
    "verificar_magic_hour",
    "obter_api_key_magichour",
    "obter_token_huggingface",
    "obter_token_replicate",
    "status_video",
    "limpar_bloqueios_video",
]
