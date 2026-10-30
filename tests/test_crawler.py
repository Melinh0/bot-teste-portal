import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bots.crawler import _normalizar, _eh_interno, varredura_controlada


def test_normalizar_remove_query_e_fragmento():
    url = "https://exemplo.com.br/produto/1?ordenar=preco#secao"
    assert _normalizar(url) == "https://exemplo.com.br/produto/1"


def test_normalizar_caminho_simples():
    assert _normalizar("https://exemplo.com.br/contato") == "https://exemplo.com.br/contato"


def test_eh_interno_retorna_true_para_caminho_relativo(monkeypatch):
    monkeypatch.setattr("bots.crawler.BASE_URL", "https://exemplo.com.br")
    assert _eh_interno("/contato") is True


def test_eh_interno_retorna_true_para_mesmo_dominio(monkeypatch):
    monkeypatch.setattr("bots.crawler.BASE_URL", "https://exemplo.com.br")
    assert _eh_interno("https://exemplo.com.br/produto") is True


def test_eh_interno_retorna_falso_para_dominio_diferente(monkeypatch):
    monkeypatch.setattr("bots.crawler.BASE_URL", "https://exemplo.com.br")
    assert _eh_interno("https://outro.com.br/contato") is False


def test_varredura_respeita_limite_de_paginas(monkeypatch):
    monkeypatch.setattr("bots.crawler.BASE_URL", "https://exemplo.com.br")

    class FakePage:
        def __init__(self):
            self.url = "https://exemplo.com.br/"

        def on(self, event, callback):
            pass

        def title(self):
            return "Pagina falsa"

        def get_by_role(self, role, **kwargs):
            return FakeLocator()

        def goto(self, url, timeout=30000):
            self.url = url

        def wait_for_timeout(self, ms):
            pass

        def locator(self, selector):
            return FakeLocator()

    class FakeLocator:
        def all(self):
            return []

        def all_inner_texts(self):
            return []

        def inner_text(self):
            return ""

    resultados = varredura_controlada(FakePage(), "https://exemplo.com.br/", max_paginas=3, max_depth=1)
    assert len(resultados) <= 3
