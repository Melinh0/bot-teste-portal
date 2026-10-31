import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bots.gerar_pdf import _converter_para_html, gerar_pdf


def test_converter_para_html_retorna_html_com_body():
    caminho_md = os.path.join(os.path.dirname(__file__), "fixture_requisitos.md")
    with open(caminho_md, "w", encoding="utf-8") as arquivo:
        arquivo.write("# Titulo\n\nTexto de teste.\n")
    try:
        html = _converter_para_html(caminho_md)
        assert "<html>" in html
        assert "<body>" in html
        assert "Titulo" in html
    finally:
        os.remove(caminho_md)


def test_gerar_pdf_cria_arquivo_nao_vazio(tmp_path):
    caminho_md = os.path.join(tmp_path, "requisitos.md")
    with open(caminho_md, "w", encoding="utf-8") as arquivo:
        arquivo.write("# Relatorio\n\nConteudo de teste.\n")
    caminho_pdf = os.path.join(tmp_path, "requisitos.pdf")
    resultado = gerar_pdf(caminho_md, caminho_pdf)
    assert resultado == caminho_pdf
    assert os.path.exists(caminho_pdf)
    assert os.path.getsize(caminho_pdf) > 0
