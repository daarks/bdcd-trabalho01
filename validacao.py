"""Conferencias numericas das duas bases carregadas no Mongo.

Serve de base para a secao 4 do relatorio de uso de IA: em vez de olhar so o grafico,
comparar os valores calculados com os que as proprias fontes ja trazem.
"""

import json
from pathlib import Path

from pymongo import MongoClient

DADOS = Path(__file__).resolve().parent / "dados"

cliente = MongoClient("mongodb://localhost:27017")
dengue = cliente["dengue_br"]
ibge = cliente["ibge"]


def teste_contagem():
    """Nada pode ter sido perdido entre o arquivo coletado e a collection."""
    for arquivo, colecao in [
        ("alertas.json", dengue.alertas),
        ("municipios.json", ibge.municipios),
        ("populacao.json", ibge.populacao),
    ]:
        no_arquivo = len(json.loads((DADOS / arquivo).read_text(encoding="utf-8")))
        no_mongo = colecao.count_documents({})
        status = "OK" if no_arquivo == no_mongo else "FALHOU"
        print(f"[{status}] {arquivo}: {no_arquivo} no arquivo, {no_mongo} no Mongo")


def teste_casos_acumulados():
    """A soma das semanas tem que bater com notif_accum_year.

    Apesar do nome, esse campo acumula toda a janela pedida na API (2015 a 2024),
    e nao o ano calendario: foi o que a comparacao mostrou.
    """
    for geocode in [3550308, 3509502, 3106200, 4209102]:
        semanas = list(
            dengue.alertas.find(
                {"geocode": geocode},
                {"casos": 1, "notif_accum_year": 1, "municipio_nome": 1},
            )
        )
        soma = sum(s.get("casos") or 0 for s in semanas)
        acumulado = semanas[0]["notif_accum_year"]
        status = "OK" if soma == acumulado else "FALHOU"
        nome = semanas[0]["municipio_nome"]
        print(f"[{status}] {nome}: soma das semanas {soma}, notif_accum_year {acumulado}")


def teste_incidencia():
    """A incidencia calculada na mao tem que reproduzir o p_inc100k que a API devolve."""
    amostra = list(dengue.alertas.find({"casos": {"$gt": 0}}, limit=2000))
    divergentes = 0
    for semana in amostra:
        calculada = semana["casos"] / semana["pop"] * 100000
        if abs(calculada - semana["p_inc100k"]) > 0.01:
            divergentes += 1
    status = "OK" if divergentes == 0 else "FALHOU"
    print(f"[{status}] incidencia por 100 mil: {divergentes} divergencias em {len(amostra)} semanas")


def teste_populacao():
    """Todo municipio do IBGE precisa ter par na populacao, e o total precisa fazer sentido."""
    sem_par = ibge.municipios.aggregate(
        [
            {
                "$lookup": {
                    "from": "populacao",
                    "localField": "id",
                    "foreignField": "geocode",
                    "as": "par",
                }
            },
            {"$match": {"par": {"$size": 0}}},
            {"$count": "total"},
        ]
    )
    orfaos = next(sem_par, {}).get("total", 0)
    status = "OK" if orfaos == 0 else "FALHOU"
    print(f"[{status}] municipios sem populacao correspondente: {orfaos}")

    total = next(
        ibge.populacao.aggregate([{"$group": {"_id": None, "t": {"$sum": "$populacao"}}}])
    )["t"]
    plausivel = 200_000_000 < total < 230_000_000
    status = "OK" if plausivel else "FALHOU"
    print(f"[{status}] populacao total somada: {total:,} habitantes")


if __name__ == "__main__":
    teste_contagem()
    teste_casos_acumulados()
    teste_incidencia()
    teste_populacao()
