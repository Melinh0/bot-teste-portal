import os
import time
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin

from playwright.sync_api import Page

BASE_URL = os.getenv("BASE_URL")
LOGIN_URL = os.getenv("LOGIN_URL")
LOGIN_EMAIL = os.getenv("LOGIN_EMAIL")
LOGIN_SENHA = os.getenv("LOGIN_SENHA")
LOGIN_CNPJ = os.getenv("LOGIN_CNPJ")
NOME_TESTE = os.getenv("NOME_TESTE", "Responsavel Teste")
TELEFONE_TESTE = os.getenv("TELEFONE_TESTE", "11999999999")

_ROBOTS_CACHE = {}


def obter_robots_txt(base_url: str) -> RobotFileParser:
    if base_url in _ROBOTS_CACHE:
        return _ROBOTS_CACHE[base_url]
    parsed = urljoin(base_url, "/robots.txt")
    rp = RobotFileParser()
    rp.set_url(parsed)
    try:
        rp.read()
    except Exception:
        pass
    _ROBOTS_CACHE[base_url] = rp
    return rp


def pode_acessar(url: str, user_agent: str = "bot-teste-portal/1.0") -> bool:
    rp = obter_robots_txt(BASE_URL or "")
    return rp.can_fetch(user_agent, url)


def esperar_rate_limit(intervalo_segundos: float = 0.5) -> None:
    time.sleep(intervalo_segundos)


def _esta_logado(page: Page) -> bool:
    try:
        corpo = page.locator("body").inner_text().lower()
        return "olá," in corpo or "ola," in corpo
    except Exception:
        return False


def fazer_login(page: Page) -> None:
    if not LOGIN_URL or not LOGIN_EMAIL or not LOGIN_SENHA:
        raise RuntimeError("LOGIN_URL, LOGIN_EMAIL e LOGIN_SENHA devem estar definidos no .env")

    if not pode_acessar(LOGIN_URL):
        raise RuntimeError(f"robots.txt bloqueia acesso a {LOGIN_URL}")

    page.goto(LOGIN_URL, timeout=30000)
    page.wait_for_timeout(2000)

    page.get_by_label("E-mail").fill(LOGIN_EMAIL)
    page.wait_for_timeout(500)
    page.get_by_label("Senha").fill(LOGIN_SENHA)
    page.wait_for_timeout(500)
    page.get_by_role("button", name="Entrar").click()
    page.wait_for_timeout(5000)

    if not _esta_logado(page):
        raise RuntimeError("Falha no login: credenciais não aceitas")


def cadastrar_loja_cnpj(page: Page) -> None:
    if not LOGIN_CNPJ:
        return
    try:
        corpo = page.locator("body").inner_text()
        if "cnpj da loja" not in corpo.lower() and "digite o cnpj" not in corpo.lower():
            return
    except Exception:
        return
    inputs = page.locator("input").all()
    for inp in inputs:
        try:
            tipo = inp.get_attribute("type") or ""
            if tipo in {"email", "password", "search"}:
                continue
            valor = inp.input_value() or ""
            if valor.strip():
                continue
            placeholder = inp.get_attribute("placeholder") or ""
            if "cnpj" not in placeholder.lower() and "00.000" not in placeholder:
                continue
            inp.fill(LOGIN_CNPJ)
            page.wait_for_timeout(1000)
            break
        except Exception:
            continue
