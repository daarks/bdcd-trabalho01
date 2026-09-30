"""Transforma as saidas reais gravadas em saidas/ nos printscreens usados no documento."""

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parent
SAIDAS = RAIZ / "saidas"
PRINTS = RAIZ / "prints"

COLUNAS = 116
FONTE = 11
FUNDO = "#1e1e2e"
TEXTO = "#e8e8e8"


def quebra(texto):
    """Quebra linhas longas para nenhuma escapar da largura da imagem."""
    linhas = []
    for linha in texto.rstrip().expandtabs(4).split("\n"):
        while len(linha) > COLUNAS:
            linhas.append(linha[:COLUNAS])
            linha = "    " + linha[COLUNAS:]
        linhas.append(linha)
    return linhas


def renderiza(texto, destino):
    linhas = quebra(texto)
    altura = 0.215 * len(linhas) + 0.35
    figura = plt.figure(figsize=(11.6, altura), facecolor=FUNDO)
    figura.text(
        0.012,
        1 - 0.16 / altura,
        "\n".join(linhas),
        family="monospace",
        fontsize=FONTE,
        color=TEXTO,
        va="top",
        linespacing=1.38,
        # sem isso o matplotlib tenta interpretar os $ dos operadores do Mongo como formula
        parse_math=False,
    )
    figura.savefig(destino, dpi=150, facecolor=FUNDO)
    plt.close(figura)
    print(f"{destino.name}: {len(linhas)} linhas")


def le(nome):
    return (SAIDAS / nome).read_text(encoding="utf-8")


def divide_consultas(texto):
    blocos = re.split(r"(?=^=+\nCONSULTA )", texto, flags=re.M)
    return [bloco.strip() for bloco in blocos if bloco.strip()]


if __name__ == "__main__":
    PRINTS.mkdir(exist_ok=True)

    renderiza(le("carga_mongo.txt"), PRINTS / "d-carga-mongo.png")
    renderiza(le("collections.txt"), PRINTS / "e-collections.png")

    for base in ["dengue", "ibge"]:
        for numero, bloco in enumerate(divide_consultas(le(f"consultas_{base}.txt")), start=1):
            renderiza(bloco, PRINTS / f"f-{base}-consulta{numero}.png")
        renderiza(le(f"indice_{base}.txt"), PRINTS / f"g-indice-{base}.png")

    renderiza(le("validacao.txt"), PRINTS / "validacao.png")
