import json
import os

from dotenv import load_dotenv
load_dotenv()

from playwright.sync_api import sync_playwright

from bots.analisar_plataforma import capturar_estado, capturar_erros, capturar_falhas
from bots.crawler import varredura_controlada
from bots.registrar_conta import BASE_URL, criar_conta

PASTA_RELATORIOS = "reports"
PASTA_SHOTS = f"{PASTA_RELATORIOS}/screenshots"


def _abrir_contexto(navegador):
    contexto = navegador.new_context(viewport={"width": 1440, "height": 900})
    page = contexto.new_page()
    return contexto, page


def _rota_diretorio(rota: str) -> str:
    import re
    safe = re.sub(r"[^A-Za-z0-9/._-]", "_", rota)
    return safe.strip("/").replace("/", "_")[:100] or "home"


def _salvar(relatorios: list) -> None:
    os.makedirs(PASTA_RELATORIOS, exist_ok=True)
    os.makedirs(PASTA_SHOTS, exist_ok=True)
    with open(f"{PASTA_RELATORIOS}/analise.json", "w", encoding="utf-8") as arquivo:
        json.dump(relatorios, arquivo, ensure_ascii=False, indent=2)


def _salvar_sitemap(dados: list) -> None:
    os.makedirs(PASTA_RELATORIOS, exist_ok=True)
    with open(f"{PASTA_RELATORIOS}/sitemap.json", "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def main() -> None:
    with sync_playwright() as p:
        headless = os.getenv("HEADLESS", "true").lower() in {"1", "true", "yes"}
        navegador = p.chromium.launch(headless=headless)
        contexto, page = _abrir_contexto(navegador)
        criar_conta(page)
        page.goto(f"{BASE_URL}/")
        page.wait_for_timeout(3000)
        erros = capturar_erros(page)
        falhas = capturar_falhas(page)
        relatorio_inicial = capturar_estado(page, erros, falhas)
        vistos = set()
        rotas = []
        for r in ["/"] + [link["href"] for link in relatorio_inicial["links"] if link["href"].startswith("/")]:
            if r not in vistos:
                vistos.add(r)
                rotas.append(r)
        relatorios = []
        for rota in rotas[:30]:
            page.goto(f"{BASE_URL}{rota}")
            page.wait_for_timeout(3000)
            captura = capturar_estado(page, erros, falhas)
            captura["rota"] = rota
            relatorios.append(captura)
            page.screenshot(path=f"{PASTA_SHOTS}/{_rota_diretorio(rota)}.png")
        _salvar(relatorios)
        sitemap = varredura_controlada(page, f"{BASE_URL}/", max_paginas=200, max_depth=3)
        for idx, entrada in enumerate(sitemap):
            rota_url = entrada.get("rota_crawler", "")
            try:
                page.screenshot(path=f"{PASTA_SHOTS}/crawler_{idx:03d}_{_rota_diretorio(rota_url)}.png")
            except Exception:
                pass
        _salvar_sitemap(sitemap)
        contexto.close()
        navegador.close()


if __name__ == "__main__":
    main()
