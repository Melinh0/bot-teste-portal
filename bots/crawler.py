import os
import time
import urllib.parse
from urllib.robotparser import RobotFileParser
from playwright.sync_api import Page

from bots.analisar_plataforma import capturar_estado, capturar_erros, capturar_falhas
from bots.fazer_login import obter_robots_txt, pode_acessar, esperar_rate_limit

BASE_URL = os.getenv("BASE_URL")

_ROBOTS_CACHE = {}


def _normalizar(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    path = urllib.parse.urlunparse(parsed._replace(query="", fragment=""))
    return path


def _eh_interno(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme and not parsed.netloc:
        return True
    return urllib.parse.urlparse(BASE_URL).netloc == parsed.netloc


def _extrair_links(page: Page) -> list[str]:
    links = []
    for a in page.locator("a[href]").all():
        href = a.get_attribute("href")
        if not href:
            continue
        if href.startswith("#") or href.startswith("javascript:"):
            continue
        abs_url = urllib.parse.urljoin(BASE_URL, href)
        if _eh_interno(abs_url):
            links.append(abs_url)
    return links


def varredura_controlada(page: Page, inicio: str, max_paginas: int = 50, max_depth: int = 2,
                         intervalo_segundos: float = 1.0) -> list[dict]:
    visitados = set()
    fila = [(inicio, 0)]
    erros = capturar_erros(page)
    falhas = capturar_falhas(page)
    resultados = []
    while fila and len(resultados) < max_paginas:
        url, profundidade = fila.pop(0)
        url_norm = _normalizar(url)
        if url_norm in visitados:
            continue
        if not pode_acessar(url):
            continue
        visitados.add(url_norm)
        try:
            page.goto(url, timeout=30000)
            page.wait_for_timeout(2500)
        except Exception:
            continue
        captura = capturar_estado(page, erros, falhas)
        captura["rota_crawler"] = url
        captura["profundidade"] = profundidade
        resultados.append(captura)
        esperar_rate_limit(intervalo_segundos)
        if profundidade >= max_depth:
            continue
        for link in _extrair_links(page):
            link_norm = _normalizar(link)
            if link_norm not in visitados and pode_acessar(link):
                fila.append((link, profundidade + 1))
    return resultados
