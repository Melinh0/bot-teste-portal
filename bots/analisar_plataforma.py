import os
from playwright.sync_api import Page

BASE_URL = os.getenv("BASE_URL")
TAMANHO_TEXTO = 3000


def capturar_erros(page: Page) -> list:
    erros = []
    page.on("console", lambda msg: erros.append({"tipo": msg.type, "texto": msg.text}) if msg.type == "error" else None)
    page.on("pageerror", lambda erro: erros.append({"tipo": "pageerror", "texto": str(erro)}))
    return erros


def capturar_falhas(page: Page) -> list:
    falhas = []
    page.on("requestfailed", lambda requisicao: falhas.append({"url": requisicao.url, "erro": str(requisicao.failure)}))
    return falhas


def capturar_estado(page: Page, erros: list, falhas: list) -> dict:
    campos = []
    for campo in page.locator("input, textarea, select").all():
        campos.append({
            "id": campo.get_attribute("id"),
            "name": campo.get_attribute("name"),
            "type": campo.get_attribute("type"),
            "placeholder": campo.get_attribute("placeholder"),
            "autocomplete": campo.get_attribute("autocomplete"),
            "aria_label": campo.get_attribute("aria-label"),
        })
    links = []
    for link in page.locator("a[href]").all():
        href = link.get_attribute("href")
        if href and href.startswith("/"):
            links.append({"href": href, "texto": link.inner_text().strip()})
    return {
        "rota": page.url,
        "url": page.url,
        "titulo": page.title(),
        "headings": page.locator("h1, h2").all_inner_texts(),
        "botoes": page.get_by_role("button").all_inner_texts(),
        "campos": campos,
        "links": links,
        "textos": page.locator("body").inner_text()[:TAMANHO_TEXTO],
        "erros": erros,
        "falhas": falhas,
    }
