import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bots.gerar_relatorio_llm import _extrair_paginas, _extrair_sitemap, _montar_prompt


def test_extrair_paginas_retorna_lista_estruturada():
    analise = [
        {
            "rota": "/produtos",
            "titulo": "Produtos",
            "headings": ["Catalogo"],
            "botoes": ["Adicionar"],
            "campos": [
                {"type": "text", "placeholder": "Buscar", "aria_label": "busca", "id": "busca", "name": "busca"}
            ],
            "links": [{"href": "/produto/1", "texto": "Produto 1"}],
            "textos": "texto da pagina",
            "erros": [{"tipo": "error", "texto": "erro x"}],
            "falhas": [{"url": "/api/x", "erro": "falha y"}],
        }
    ]
    paginas = _extrair_paginas(analise)
    assert len(paginas) == 1
    assert paginas[0]["rota"] == "/produtos"
    assert paginas[0]["campos"][0]["tipo"] == "text"


def test_extrair_sitemap_retorna_rotas():
    sitemap = [
        {"rota_crawler": "/", "profundidade": 0},
        {"rota_crawler": "/produtos", "profundidade": 1},
    ]
    rotas = _extrair_sitemap(sitemap)
    assert len(rotas) == 2
    assert rotas[0]["profundidade"] == 0


def test_montar_prompt_contrai_secoes_obrigatorias():
    paginas = [{"rota": "/", "titulo": "Home", "headings": [], "botoes": [], "campos": [], "links": [], "textos": "", "erros": [], "falhas": []}]
    rotas = [{"rota": "/", "profundidade": 0}]
    prompt = _montar_prompt(paginas, rotas)
    for secao in ["Resumo Executivo", "Requisitos Funcionais", "Modelo de Dados", "Endpoints", "Glossario"]:
        assert secao in prompt



