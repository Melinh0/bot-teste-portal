import os
import re

import markdown

from playwright.sync_api import sync_playwright

PASTA_RELATORIOS = os.getenv("PASTA_RELATORIOS", "reports")

_CSS = """
@page {
    size: A4;
    margin: 2.2cm 2cm 2.2cm 2cm;
    @top-center { content: "Documento de Requisitos - Portal de Pedidos"; font-size: 8pt; color: #666; font-family: Arial, sans-serif; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; margin-bottom: 0.5em; }
    @bottom-center { content: "Pagina " counter(page) " de " counter(pages); font-size: 8pt; color: #666; font-family: Arial, sans-serif; }
}
* { box-sizing: border-box; }
body { font-family: "DejaVu Sans", "Liberation Sans", Arial, sans-serif; font-size: 10.5pt; line-height: 1.6; color: #222; }
h1 { font-size: 17pt; border-bottom: 2px solid #333; padding-bottom: 0.3em; page-break-after: avoid; margin-top: 1.5em; }
h2 { font-size: 13.5pt; page-break-after: avoid; margin-top: 1.4em; }
h3 { font-size: 11.5pt; page-break-after: avoid; margin-top: 1.2em; }
p { margin: 0.5em 0; text-align: justify; }
ul, ol { margin: 0.5em 0 0.5em 1.5em; padding: 0; }
li { margin: 0.3em 0; text-align: justify; }
table { border-collapse: collapse; width: 100%; margin: 0.8em 0; table-layout: fixed; page-break-inside: avoid; }
th, td { border: 1px solid #999; padding: 0.4em 0.5em; text-align: left; vertical-align: top; overflow-wrap: break-word; word-wrap: break-word; font-size: 9pt; }
th { background: #f0f0f0; font-weight: bold; }
tr { page-break-inside: avoid; }
code { font-family: "DejaVu Sans Mono", monospace; background: #f5f5f5; padding: 0.15em 0.3em; border-radius: 3px; font-size: 9pt; word-break: break-all; }
strong { font-weight: bold; }
em { font-style: italic; }
hr { border: 0; border-top: 1px solid #ccc; margin: 1em 0; }
.blockquote, blockquote { border-left: 3px solid #ccc; margin: 0.8em 0; padding: 0.5em 1em; background: #f9f9f9; }
"""

_EXTENSOES = ["tables", "fenced_code", "attr_list", "def_list", "footnotes", "sane_lists", "smarty"]

_MATEMATICA_PARA_TEXTO = {
    "$$\\rightarrow$$": " → ",
    "$\\rightarrow$": " → ",
    "\\rightarrow": " → ",
    "$$\\leftarrow$$": " ← ",
    "$\\leftarrow$": " ← ",
    "\\leftarrow": " ← ",
    "$$\\Rightarrow$$": " ⇒ ",
    "$\\Rightarrow$": " ⇒ ",
    "\\Rightarrow": " ⇒ ",
    "$$\\Leftarrow$$": " ⇐ ",
    "$\\Leftarrow$": " ⇐ ",
    "\\Leftarrow": " ⇐ ",
    "$$\\uparrow$$": " ↑ ",
    "$\\uparrow$": " ↑ ",
    "\\uparrow": " ↑ ",
    "$$\\downarrow$$": " ↓ ",
    "$\\downarrow$": " ↓ ",
    "\\downarrow": " ↓ ",
}


def _limpar_notacao_matematica(texto: str) -> str:
    for padrao, substituto in _MATEMATICA_PARA_TEXTO.items():
        texto = texto.replace(padrao, substituto)
    texto = re.sub(r"\$[^$]+\$", " ", texto)
    texto = re.sub(r"\$\$[^$]+\$\$", " ", texto)
    return texto


def _converter_para_html(caminho_md):
    with open(caminho_md, "r", encoding="utf-8") as arquivo:
        md = arquivo.read()
    md = _limpar_notacao_matematica(md)
    html = markdown.markdown(md, extensions=_EXTENSOES)
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{_CSS}</style></head><body>{html}</body></html>"


def _renderizar_pdf(html, caminho_pdf):
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page()
        pagina.set_content(html, wait_until="networkidle")
        pagina.pdf(path=caminho_pdf, format="A4", print_background=True, margin={"top": "2.2cm", "right": "2cm", "bottom": "2.2cm", "left": "2cm"})
        navegador.close()


def gerar_pdf(caminho_md, caminho_pdf=None):
    if caminho_pdf is None:
        base = os.path.splitext(caminho_md)[0]
        caminho_pdf = f"{base}.pdf"
    html = _converter_para_html(caminho_md)
    _renderizar_pdf(html, caminho_pdf)
    return caminho_pdf


if __name__ == "__main__":
    caminho = gerar_pdf(f"{PASTA_RELATORIOS}/requisitos_plataforma.md")
    print(f"PDF salvo em: {caminho}")
