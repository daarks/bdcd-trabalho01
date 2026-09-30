"""Coleta a Base 2 (IBGE): municipios brasileiros e populacao estimada."""

import gzip
import json
import urllib.request
from pathlib import Path

DADOS = Path(__file__).resolve().parent.parent / "dados"

URL_MUNICIPIOS = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
URL_SIDRA = "https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/all/p/last"


def baixa_json(url):
    # as APIs do IBGE respondem comprimido, entao a resposta e descomprimida antes do parse
    pedido = urllib.request.Request(url, headers={"Accept-Encoding": "gzip"})
    with urllib.request.urlopen(pedido, timeout=120) as resposta:
        corpo = resposta.read()
        if resposta.headers.get("Content-Encoding") == "gzip":
            corpo = gzip.decompress(corpo)
    return json.loads(corpo.decode("utf-8"))


def coleta_municipios():
    """Municipios com a hierarquia regiao/UF/mesorregiao, salvos como vieram da API."""
    municipios = baixa_json(URL_MUNICIPIOS)
    (DADOS / "municipios.json").write_text(
        json.dumps(municipios, ensure_ascii=False), encoding="utf-8"
    )
    return len(municipios)


def coleta_populacao():
    """Tabela 6579 do SIDRA: a primeira linha e cabecalho descritivo, entao e descartada."""
    bruto = baixa_json(URL_SIDRA)
    documentos = []
    for linha in bruto[1:]:
        documentos.append(
            {
                "geocode": int(linha["D1C"]),
                "municipio_uf": linha["D1N"],
                "ano": int(linha["D3C"]),
                "populacao": int(linha["V"]),
                "variavel": linha["D2N"],
            }
        )
    (DADOS / "populacao.json").write_text(
        json.dumps(documentos, ensure_ascii=False), encoding="utf-8"
    )
    return len(documentos)


if __name__ == "__main__":
    DADOS.mkdir(exist_ok=True)
    print(f"municipios.json: {coleta_municipios()} registros")
    print(f"populacao.json: {coleta_populacao()} registros")
