"""Gera o PDF de entrega a partir do Markdown, usando pandoc e LibreOffice."""

import re
import shutil
import subprocess
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
MARKDOWN = RAIZ / "ENTREGA-trabalho01.md"
REFERENCIA = RAIZ / "build" / "referencia-a4.odt"
ODT = RAIZ / "build" / "ENTREGA-trabalho01.odt"

PAGINA_A4 = {
    'fo:page-width="8.5in"': 'fo:page-width="21cm"',
    'fo:page-height="11in"': 'fo:page-height="29.7cm"',
    'fo:margin-left="1in"': 'fo:margin-left="2cm"',
    'fo:margin-right="1in"': 'fo:margin-right="2cm"',
    'fo:margin-top="1in"': 'fo:margin-top="2cm"',
    'fo:margin-bottom="1in"': 'fo:margin-bottom="2cm"',
}


def gera_referencia_a4():
    """A referencia padrao do pandoc vem em Letter, entao a pagina e trocada para A4."""
    padrao = REFERENCIA.with_name("referencia-padrao.odt")
    with padrao.open("wb") as arquivo:
        subprocess.run(
            ["pandoc", "--print-default-data-file", "reference.odt"],
            stdout=arquivo,
            check=True,
        )

    with zipfile.ZipFile(padrao) as origem, zipfile.ZipFile(
        REFERENCIA, "w", zipfile.ZIP_DEFLATED
    ) as destino:
        for item in origem.infolist():
            conteudo = origem.read(item.filename)
            if item.filename == "styles.xml":
                texto = conteudo.decode("utf-8")
                for antigo, novo in PAGINA_A4.items():
                    texto = texto.replace(antigo, novo)
                conteudo = texto.encode("utf-8")
            destino.writestr(item, conteudo)

    padrao.unlink()


def converte():
    subprocess.run(
        [
            "pandoc",
            str(MARKDOWN),
            f"--reference-doc={REFERENCIA}",
            "--resource-path", str(RAIZ),
            "-o", str(ODT),
        ],
        check=True,
        cwd=RAIZ,
    )
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(RAIZ / "build"), str(ODT)],
        check=True,
        capture_output=True,
    )
    shutil.move(ODT.with_suffix(".pdf"), RAIZ / "ENTREGA-trabalho01.pdf")


if __name__ == "__main__":
    (RAIZ / "build").mkdir(exist_ok=True)
    gera_referencia_a4()
    converte()
    print("gerado: ENTREGA-trabalho01.pdf")
