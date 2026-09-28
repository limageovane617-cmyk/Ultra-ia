# ============================================================
# 📄 ALEX IA ULTRA — SISTEMA DE ARQUIVOS
# Criada por Geovani
# ============================================================

from io import BytesIO
from pathlib import Path
import csv
import json
import zipfile

import PyPDF2
from docx import Document

try:
    import openpyxl
except ImportError:
    openpyxl = None


# ============================================================
# 📝 TXT
# ============================================================

def ler_txt(arquivo):
    """Lê um arquivo TXT."""

    try:
        conteudo = arquivo.read()

        if isinstance(conteudo, bytes):
            conteudo = conteudo.decode("utf-8", errors="ignore")

        return conteudo, None

    except Exception as erro:
        return None, str(erro)


# ============================================================
# 📕 PDF
# ============================================================

def ler_pdf(arquivo):
    """Extrai texto de um arquivo PDF."""

    try:
        leitor = PyPDF2.PdfReader(arquivo)

        paginas = []

        for pagina in leitor.pages:
            texto = pagina.extract_text()

            if texto:
                paginas.append(texto)

        return "\n\n".join(paginas), None

    except Exception as erro:
        return None, str(erro)


# ============================================================
# 📘 DOCX
# ============================================================

def ler_docx(arquivo):
    """Extrai texto de um arquivo DOCX."""

    try:
        documento = Document(BytesIO(arquivo.read()))

        paragrafos = []

        for paragrafo in documento.paragraphs:

            if paragrafo.text.strip():
                paragrafos.append(paragrafo.text)

        return "\n".join(paragrafos), None

    except Exception as erro:
        return None, str(erro)


# ============================================================
# 📊 CSV
# ============================================================

def ler_csv(arquivo):
    """Lê um arquivo CSV."""

    try:
        conteudo = arquivo.read()

        if isinstance(conteudo, bytes):
            conteudo = conteudo.decode("utf-8", errors="ignore")

        linhas = []

        leitor = csv.reader(conteudo.splitlines())

        for linha in leitor:
            linhas.append(" | ".join(linha))

        return "\n".join(linhas), None

    except Exception as erro:
        return None, str(erro)


# ============================================================
# 📊 XLSX
# ============================================================

def ler_xlsx(arquivo):
    """Extrai dados de uma planilha XLSX."""

    if openpyxl is None:
        return None, "A biblioteca openpyxl não está instalada."

    try:
        dados = []

        planilha = openpyxl.load_workbook(
            BytesIO(arquivo.read()),
            read_only=True,
            data_only=True
        )

        for nome_planilha in planilha.sheetnames:

            folha = planilha[nome_planilha]

            dados.append(
                f"\n=== PLANILHA: {nome_planilha} ==="
            )

            for linha in folha.iter_rows(values_only=True):

                valores = []

                for valor in linha:

                    if valor is not None:
                        valores.append(str(valor))

                if valores:
                    dados.append(" | ".join(valores))

        return "\n".join(dados), None

    except Exception as erro:
        return None, str(erro)


# ============================================================
# 💻 CÓDIGO / TEXTO ESTRUTURADO
# ============================================================

def ler_codigo(arquivo):
    """Lê arquivos de código como texto."""

    try:
        conteudo = arquivo.read()

        if isinstance(conteudo, bytes):
            conteudo = conteudo.decode("utf-8", errors="ignore")

        return conteudo, None

    except Exception as erro:
        return None, str(erro)


# ============================================================
# ⚙️ JSON
# ============================================================

def ler_json(arquivo):
    """Lê e organiza um arquivo JSON."""

    try:
        conteudo = arquivo.read()

        if isinstance(conteudo, bytes):
            conteudo = conteudo.decode("utf-8", errors="ignore")

        dados = json.loads(conteudo)

        return json.dumps(
            dados,
            indent=2,
            ensure_ascii=False
        ), None

    except Exception as erro:
        return None, str(erro)


# ============================================================
# 📦 ZIP
# ============================================================

def ler_zip(arquivo):
    """
    Analisa um arquivo ZIP e mostra sua estrutura.
    """

    try:
        dados = []

        with zipfile.ZipFile(arquivo) as zip_arquivo:

            arquivos = zip_arquivo.namelist()

            dados.append(
                f"Total de itens no ZIP: {len(arquivos)}"
            )

            dados.append("\n=== CONTEÚDO ===")

            for nome in arquivos:
                dados.append(nome)

        return "\n".join(dados), None

    except Exception as erro:
        return None, str(erro)


# ============================================================
# 📋 INFORMAÇÕES DO ARQUIVO
# ============================================================

def obter_info_arquivo(arquivo):
    """Retorna informações básicas do arquivo."""

    try:
        nome = arquivo.name
        tamanho = arquivo.size

        extensao = Path(nome).suffix.lower()

        return {
            "nome": nome,
            "tamanho_bytes": tamanho,
            "tamanho_kb": round(tamanho / 1024, 2),
            "extensao": extensao,
        }, None

    except Exception as erro:
        return None, str(erro)


# ============================================================
# 🧠 FUNÇÃO PRINCIPAL
# ============================================================

def ler_arquivo(arquivo):
    """
    Identifica o tipo do arquivo e extrai seu conteúdo.
    """

    if arquivo is None:
        return None, "Nenhum arquivo foi enviado."

    nome = arquivo.name.lower()

    # ----------------------------
    # 📄 Documentos
    # ----------------------------

    if nome.endswith(".txt"):
        return ler_txt(arquivo)

    if nome.endswith(".pdf"):
        return ler_pdf(arquivo)

    if nome.endswith(".docx"):
        return ler_docx(arquivo)

    # ----------------------------
    # 📊 Planilhas
    # ----------------------------

    if nome.endswith(".csv"):
        return ler_csv(arquivo)

    if nome.endswith(".xlsx"):
        return ler_xlsx(arquivo)

    # ----------------------------
    # ⚙️ Dados
    # ----------------------------

    if nome.endswith(".json"):
        return ler_json(arquivo)

    # ----------------------------
    # 💻 Código
    # ----------------------------

    extensoes_codigo = (
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
        ".md",
        ".xml",
        ".rtf",
    )

    if nome.endswith(extensoes_codigo):
        return ler_codigo(arquivo)

    # ----------------------------
    # 📦 ZIP
    # ----------------------------

    if nome.endswith(".zip"):
        return ler_zip(arquivo)

    # ----------------------------
    # 🖼️ / 🎵 / 🎬
    # ----------------------------

    extensoes_multimidia = (
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".gif",
        ".bmp",
        ".tiff",
        ".tif",
        ".mp3",
        ".wav",
        ".ogg",
        ".m4a",
        ".flac",
        ".aac",
        ".mp4",
        ".mov",
        ".avi",
        ".mkv",
        ".webm",
        ".mpeg4",
    )

    if nome.endswith(extensoes_multimidia):

        return (
            "",
            None
        )

    return None, (
        f"Formato não suportado: {Path(nome).suffix}"
      )
