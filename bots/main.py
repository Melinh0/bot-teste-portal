import json
import os
import re

from dotenv import load_dotenv
load_dotenv()

from playwright.sync_api import sync_playwright

from bots.analisar_plataforma import capturar_estado, capturar_erros, capturar_falhas
from bots.crawler import varredura_controlada
from bots.fazer_login import (
    BASE_URL,
    cadastrar_loja_cnpj,
    fazer_login,
    pode_acessar,
)

PASTA_RELATORIOS = "reports"
PASTA_SHOTS = f"{PASTA_RELATORIOS}/screenshots"
PASTA_HTML = f"{PASTA_RELATORIOS}/html"


def _abrir_contexto(navegador):
    contexto = navegador.new_context(viewport={"width": 1440, "height": 900})
    page = contexto.new_page()
    return contexto, page


def _nome_arquivo(rota: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9/._-]", "_", rota)
    return safe.strip("/").replace("/", "_")[:100] or "home"


def _salvar_html(rota: str, conteudo: str) -> None:
    os.makedirs(PASTA_HTML, exist_ok=True)
    nome = _nome_arquivo(rota)
    with open(f"{PASTA_HTML}/{nome}.html", "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo)


def _salvar_json(caminho: str, dados) -> None:
    os.makedirs(PASTA_RELATORIOS, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def _eh_rota_produto(rota: str) -> bool:
    return rota.startswith("/produto/")


def main() -> None:
    with sync_playwright() as p:
        headless = os.getenv("HEADLESS", "true").lower() in {"1", "true", "yes"}
        navegador = p.chromium.launch(headless=headless)
        contexto, page = _abrir_contexto(navegador)
        fazer_login(page)

        if not pode_acessar(f"{BASE_URL}/"):
            raise RuntimeError(f"robots.txt bloqueia acesso a {BASE_URL}/")

        page.goto(f"{BASE_URL}/", timeout=15000)
        page.wait_for_timeout(2000)
        cadastrar_loja_cnpj(page)
        _salvar_html("/", page.content())

        erros = capturar_erros(page)
        falhas = capturar_falhas(page)
        relatorio_inicial = capturar_estado(page, erros, falhas)

        vistos = set()
        rotas = []
        for r in ["/"] + [link["href"] for link in relatorio_inicial["links"] if link["href"].startswith("/")]:
            if r not in vistos and not _eh_rota_produto(r):
                vistos.add(r)
                rotas.append(r)

        relatorios = []
        for rota in rotas[:15]:
            url = f"{BASE_URL}{rota}"
            if not pode_acessar(url):
                continue
            try:
                page.goto(url, timeout=15000)
                page.wait_for_timeout(2000)
                cadastrar_loja_cnpj(page)
                _salvar_html(rota, page.content())
                captura = capturar_estado(page, erros, falhas)
                captura["rota"] = rota
                relatorios.append(captura)
                page.screenshot(path=f"{PASTA_SHOTS}/{_nome_arquivo(rota)}.png")
            except Exception:
                continue

        _salvar_json(f"{PASTA_RELATORIOS}/analise.json", relatorios)

        contexto.close()
        navegador.close()


if __name__ == "__main__":
    main()
