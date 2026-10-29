import os
import uuid

from playwright.sync_api import Page

BASE_URL = os.getenv("BASE_URL")
SENHAS_CONTA = os.getenv("SENHA_CONTA")
NOME_TESTE = os.getenv("NOME_TESTE")
TELEFONE_TESTE = os.getenv("TELEFONE_TESTE")


def _gerar_email():
    return f"bruce.test.{uuid.uuid4().hex[:10]}@exemplo.com"


def criar_conta(page: Page) -> str:
    email = _gerar_email()
    page.goto(f"{BASE_URL}/entrar?volta=%2F")
    page.get_by_role("tab", name="Criar conta").click()
    page.wait_for_timeout(2000)
    page.get_by_label("Nome do responsável").fill(NOME_TESTE)
    page.get_by_label("Telefone / WhatsApp").fill(TELEFONE_TESTE)
    page.get_by_label("E-mail").fill(email)
    page.get_by_label("Crie uma senha").fill(SENHAS_CONTA)
    page.get_by_role("button", name="Criar conta").click()
    page.wait_for_timeout(12000)
    return email
