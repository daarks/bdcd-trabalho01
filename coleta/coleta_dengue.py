"""Coleta a Base 1 (InfoDengue/Fiocruz): alertas semanais de dengue, 2015 a 2024.

Escopo: municipios brasileiros com mais de 100 mil habitantes, segundo a estimativa
do IBGE ja coletada por coleta_ibge.py.
"""

import json
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DADOS = Path(__file__).resolve().parent.parent / "dados"

ANO_INICIAL = 2015
ANO_FINAL = 2024
POPULACAO_MINIMA = 100_000
TRABALHADORES = 6

# a API devolve estes campos como string, o que impediria $avg e comparacoes no Mongo
CAMPOS_DECIMAIS = ("tempmin", "tempmed", "tempmax", "umidmin", "umidmed", "umidmax")

URL_ALERTA = (
    "https://info.dengue.mat.br/api/alertcity"
    "?geocode={geocode}&disease=dengue&format=json"
    f"&ew_start=1&ew_end=53&ey_start={ANO_INICIAL}&ey_end={ANO_FINAL}"
)


def municipios_acima_de(pop_min):
    """Le populacao.json e devolve os geocodes dos municipios acima do corte."""
    populacao = json.loads((DADOS / "populacao.json").read_text(encoding="utf-8"))
    selecionados = []
    for municipio in populacao:
        if municipio["populacao"] > pop_min:
            selecionados.append(municipio["geocode"])
    return selecionados


def baixa_municipio(geocode, tentativas=3):
    """Busca as semanas de um municipio, com nova tentativa quando a API falha."""
    for tentativa in range(tentativas):
        try:
            with urllib.request.urlopen(
                URL_ALERTA.format(geocode=geocode), timeout=90
            ) as resposta:
                return json.load(resposta)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            if tentativa == tentativas - 1:
                return []
            time.sleep(3 * (tentativa + 1))
    return []


def converte_numero(valor, tipo):
    if valor is None or valor == "":
        return None
    return tipo(float(valor))


def prepara_documentos(geocode, semanas):
    """Acrescenta o geocode, converte a data em epoch para Date e tipa os campos numericos."""
    documentos = []
    for semana in semanas:
        semana["geocode"] = geocode
        semana["data_iniSE"] = {"$date": {"$numberLong": str(semana["data_iniSE"])}}
        semana["pop"] = converte_numero(semana.get("pop"), int)
        for campo in CAMPOS_DECIMAIS:
            semana[campo] = converte_numero(semana.get(campo), float)
        documentos.append(semana)
    return documentos


def main():
    geocodes = municipios_acima_de(POPULACAO_MINIMA)
    print(f"{len(geocodes)} municipios acima de {POPULACAO_MINIMA} habitantes")

    alertas = []
    vazios = []
    with ThreadPoolExecutor(max_workers=TRABALHADORES) as executor:
        for posicao, (geocode, semanas) in enumerate(
            zip(geocodes, executor.map(baixa_municipio, geocodes)), start=1
        ):
            if not semanas:
                vazios.append(geocode)
            alertas.extend(prepara_documentos(geocode, semanas))
            if posicao % 50 == 0:
                print(f"  {posicao}/{len(geocodes)} municipios | {len(alertas)} semanas")

    with (DADOS / "alertas.json").open("w", encoding="utf-8") as arquivo:
        json.dump(alertas, arquivo, ensure_ascii=False)

    print(f"alertas.json: {len(alertas)} registros")
    if vazios:
        print(f"municipios sem retorno da API: {vazios}")


if __name__ == "__main__":
    main()
