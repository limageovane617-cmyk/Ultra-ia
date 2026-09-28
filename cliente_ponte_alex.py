#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cliente_ponte_alex.py

Cliente oficial da Ponte Alex v2 para integracao externa segura via HTTPS.

Permite:
- testar a conexao com a Ponte;
- enviar codigo Python;
- solicitar processamento;
- validar o resultado;
- baixar o arquivo processado;
- salvar o resultado localmente.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional


DEFAULT_PONTE_URL = "https://ponte-alex-v2.onrender.com"


class ErroPonteAlex(Exception):
    """Erro de comunicacao ou processamento da Ponte Alex v2."""

    def __init__(
        self,
        mensagem: str,
        status_http: Optional[int] = None,
        detalhes: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(mensagem)
        self.status_http = status_http
        self.detalhes = detalhes or {}


class ClientePonteAlex:
    """
    Cliente oficial para comunicacao com a API HTTPS
    da Ponte Alex v2.
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (
            base_url
            or os.environ.get("PONTE_API_URL")
            or DEFAULT_PONTE_URL
        ).rstrip("/")

        self._secret = os.environ.get(
            "PONTE_API_SECRET",
            ""
        ).strip()

    def _obter_headers(self) -> Dict[str, str]:
        """
        Monta os headers necessarios para autenticacao.
        Nunca exibe o segredo.
        """

        if not self._secret:
            raise ErroPonteAlex(
                "PONTE_API_SECRET nao foi configurada no ambiente."
            )

        return {
            "Content-Type": "application/json; charset=utf-8",
            "x-api-secret": self._secret,
            "User-Agent": "ClientePonteAlex/2.0",
        }

    def ping(self) -> Dict[str, Any]:
        """
        Testa o endpoint publico:

        GET /api/ponte/v2/ping
        """

        url = f"{self.base_url}/api/ponte/v2/ping"

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "ClientePonteAlex/2.0"
            },
            method="GET",
        )

        try:
            with urllib.request.urlopen(
                req,
                timeout=15
            ) as response:

                corpo = response.read().decode(
                    "utf-8"
                )

                return json.loads(corpo)

        except urllib.error.HTTPError as e:

            corpo = e.read().decode(
                "utf-8",
                errors="replace"
            )

            raise ErroPonteAlex(
                f"Erro HTTP {e.code} no ping: {e.reason}",
                status_http=e.code,
                detalhes={"raw_error": corpo},
            )

        except urllib.error.URLError as e:

            raise ErroPonteAlex(
                f"Falha de conexao com a Ponte Alex v2: {e.reason}"
            )

    def processar_codigo(
        self,
        conteudo_codigo: str,
        instrucao: str,
        nome_arquivo: str = "script.py",
        nome_saida: Optional[str] = None,
        destino_local: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Envia codigo Python para processamento na Ponte,
        recebe o resultado e baixa o arquivo processado.
        """

        if not conteudo_codigo.strip():
            raise ErroPonteAlex(
                "O conteudo do codigo Python nao pode estar vazio."
            )

        if not nome_saida:

            nome_puro = Path(
                nome_arquivo
            ).stem

            nome_saida = (
                f"{nome_puro}_processado.py"
            )

        url_processar = (
            f"{self.base_url}/api/ponte/v2/processar"
        )

        payload = {
            "filename": nome_arquivo,
            "outputFilename": nome_saida,
            "instruction": instrucao,
            "fileContent": conteudo_codigo,
        }

        headers = self._obter_headers()

        dados_envio = json.dumps(
            payload
        ).encode("utf-8")

        req = urllib.request.Request(
            url_processar,
            data=dados_envio,
            headers=headers,
            method="POST",
        )

        try:

            with urllib.request.urlopen(
                req,
                timeout=30
            ) as response:

                status_code = response.getcode()

                corpo_resposta = response.read().decode(
                    "utf-8"
                )

                resultado_json = json.loads(
                    corpo_resposta
                )

        except urllib.error.HTTPError as e:

            status_code = e.code

            corpo_erro = e.read().decode(
                "utf-8",
                errors="replace"
            )

            detalhes = {}

            try:
                detalhes = json.loads(
                    corpo_erro
                )

            except Exception:
                detalhes = {
                    "raw_error": corpo_erro
                }

            if status_code == 400:

                mensagem = (
                    detalhes.get("error")
                    or detalhes.get("testMessage")
                    or "Requisicao invalida."
                )

                raise ErroPonteAlex(
                    f"Erro HTTP 400: {mensagem}",
                    status_http=400,
                    detalhes=detalhes,
                )

            if status_code == 401:

                raise ErroPonteAlex(
                    "Erro HTTP 401: "
                    "o segredo x-api-secret foi rejeitado.",
                    status_http=401,
                    detalhes=detalhes,
                )

            if status_code == 500:

                mensagem = (
                    detalhes.get("error")
                    or "Erro interno na Ponte Alex v2."
                )

                raise ErroPonteAlex(
                    f"Erro HTTP 500: {mensagem}",
                    status_http=500,
                    detalhes=detalhes,
                )

            raise ErroPonteAlex(
                f"Erro HTTP {status_code}: {e.reason}",
                status_http=status_code,
                detalhes=detalhes,
            )

        except urllib.error.URLError as e:

            raise ErroPonteAlex(
                f"Falha de rede ao conectar na Ponte: {e.reason}"
            )

        if not resultado_json.get("success"):

            raise ErroPonteAlex(
                "A operacao nao foi bem sucedida: "
                + str(
                    resultado_json.get(
                        "testMessage",
                        "Sem mensagem"
                    )
                ),
                detalhes=resultado_json,
            )

        processed_file_info = (
            resultado_json.get(
                "processedFile",
                {}
            )
        )

        download_url_relativa = (
            processed_file_info.get(
                "downloadUrl",
                ""
            )
        )

        if not download_url_relativa:

            raise ErroPonteAlex(
                "A Ponte nao retornou um downloadUrl valido."
            )

        if (
            download_url_relativa.startswith(
                "http://"
            )
            or
            download_url_relativa.startswith(
                "https://"
            )
        ):

            url_download_completa = (
                download_url_relativa
            )

        else:

            url_download_completa = (
                urllib.parse.urljoin(
                    self.base_url,
                    download_url_relativa
                )
            )

        caminho_salvar = Path(
            destino_local or nome_saida
        )

        caminho_salvar.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        req_download = urllib.request.Request(
            url_download_completa,
            headers={
                "User-Agent": "ClientePonteAlex/2.0"
            },
            method="GET",
        )

        try:

            with urllib.request.urlopen(
                req_download,
                timeout=30
            ) as resposta:

                conteudo_baixado = (
                    resposta.read()
                )

            with open(
                caminho_salvar,
                "wb"
            ) as arquivo:

                arquivo.write(
                    conteudo_baixado
                )

        except urllib.error.HTTPError as e:

            raise ErroPonteAlex(
                "Falha ao baixar arquivo processado: "
                f"HTTP {e.code}",
                status_http=e.code,
            )

        except urllib.error.URLError as e:

            raise ErroPonteAlex(
                f"Falha de conexao no download: {e.reason}"
            )

        tamanho_salvo = (
            caminho_salvar.stat().st_size
        )

        return {
            "status_http": status_code,
            "arquivo_salvo": str(
                caminho_salvar.resolve()
            ),
            "nome_arquivo": (
                caminho_salvar.name
            ),
            "tamanho_bytes": tamanho_salvo,
            "download_url": (
                url_download_completa
            ),
            "test_passed": (
                resultado_json.get(
                    "testPassed",
                    False
                )
            ),
            "test_message": (
                resultado_json.get(
                    "testMessage",
                    ""
                )
            ),
            "compile_check": (
                resultado_json.get(
                    "compileCheck",
                    {}
                )
            ),
            "execution": (
                resultado_json.get(
                    "execution",
                    {}
                )
            ),
            "original_sha256": (
                resultado_json.get(
                    "originalFile",
                    {}
                ).get(
                    "sha256",
                    ""
                )
            ),
            "processed_sha256": (
                processed_file_info.get(
                    "sha256",
                    ""
                )
            ),
            "resposta_completa": (
                resultado_json
            ),
        }

    def processar_arquivo(
        self,
        caminho_arquivo: str,
        instrucao: str,
        arquivo_saida: Optional[str] = None,
        destino_local: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Le um arquivo Python local e envia para a Ponte.
        """

        caminho = Path(
            caminho_arquivo
        )

        if not caminho.exists():

            raise FileNotFoundError(
                f"Arquivo de entrada "
                f"'{caminho_arquivo}' nao encontrado."
            )

        if not caminho.is_file():

            raise ValueError(
                f"O caminho '{caminho_arquivo}' "
                "nao e um arquivo."
            )

        with open(
            caminho,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as arquivo:

            conteudo = arquivo.read()

        nome_saida = (
            arquivo_saida
            or f"{caminho.stem}_processado.py"
        )

        destino = (
            destino_local
            or nome_saida
        )

        return self.processar_codigo(
            conteudo_codigo=conteudo,
            instrucao=instrucao,
            nome_arquivo=caminho.name,
            nome_saida=nome_saida,
            destino_local=destino,
        )


def main():

    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Cliente oficial da Ponte Alex v2"
        )
    )

    parser.add_argument(
        "arquivo",
        help=(
            "Arquivo Python de entrada"
        ),
    )

    parser.add_argument(
        "--instruction",
        "-i",
        required=True,
        help=(
            "Instrucao de modificacao"
        ),
    )

    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help=(
            "Arquivo de saida"
        ),
    )

    parser.add_argument(
        "--url",
        "-u",
        default=None,
        help=(
            "URL da Ponte Alex v2"
        ),
    )

    parser.add_argument(
        "--ping",
        action="store_true",
        help=(
            "Apenas testa a conectividade"
        ),
    )

    args = parser.parse_args()

    try:

        cliente = ClientePonteAlex(
            base_url=args.url
        )

        if args.ping:

            print(
                "Testando Ponte Alex v2..."
            )

            resultado_ping = (
                cliente.ping()
            )

            print(
                f"Status: "
                f"{resultado_ping.get('status')}"
            )

            print(
                f"Versao: "
                f"{resultado_ping.get('version')}"
            )

            print(
                f"Runtime: "
                f"{resultado_ping.get('pythonRuntime')}"
            )

            return 0

        print("=" * 60)
        print(
            "PONTE ALEX v2 - "
            "CLIENTE OFICIAL"
        )
        print("=" * 60)

        print(
            f"Arquivo: {args.arquivo}"
        )

        print(
            f"Servidor: {cliente.base_url}"
        )

        resultado = (
            cliente.processar_arquivo(
                caminho_arquivo=args.arquivo,
                instrucao=args.instruction,
                arquivo_saida=args.output,
            )
        )

        print()
        print(
            "PROCESSAMENTO CONCLUIDO"
        )

        print(
            f"Arquivo salvo: "
            f"{resultado['arquivo_salvo']}"
        )

        print(
            f"Tamanho: "
            f"{resultado['tamanho_bytes']} bytes"
        )

        print(
            f"Teste: "
            f"{resultado['test_passed']}"
        )

        print(
            f"Mensagem: "
            f"{resultado['test_message']}"
        )

        execution = resultado.get(
            "execution",
            {}
        )

        if execution.get("stdout"):

            print()
            print(
                "Saida da execucao:"
            )

            print(
                execution["stdout"].strip()
            )

        print("=" * 60)

        return 0

    except ErroPonteAlex as e:

        print(
            f"ERRO NA PONTE ALEX: {e}",
            file=sys.stderr
        )

        if e.detalhes:

            print(
                f"Detalhes: "
                f"{json.dumps(e.detalhes, indent=2)}",
                file=sys.stderr
            )

        return 1

    except Exception as e:

        print(
            f"ERRO INESPERADO: {e}",
            file=sys.stderr
        )

        return 2


if __name__ == "__main__":
    sys.exit(main())
