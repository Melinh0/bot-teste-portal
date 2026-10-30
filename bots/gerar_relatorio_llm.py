import json
import os
import re

import requests

from dotenv import load_dotenv
load_dotenv()

PASTA_RELATORIOS = os.getenv("PASTA_RELATORIOS", "reports")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "https://api.ollama.com")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")


def _carregar_json(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def _extrair_dados_para_llm(analise):
    paginas = []
    for entrada in analise:
        pagina = {
            "rota": entrada.get("rota"),
            "titulo": entrada.get("titulo"),
            "headings": entrada.get("headings", []),
            "botoes": entrada.get("botoes", []),
            "campos": [
                {
                    "tipo": c.get("type"),
                    "placeholder": c.get("placeholder"),
                    "label": c.get("aria_label"),
                    "id": c.get("id"),
                }
                for c in entrada.get("campos", [])
            ],
            "links": [
                {"href": l.get("href"), "texto": l.get("texto")}
                for l in entrada.get("links", [])
            ],
            "textos": entrada.get("textos", "")[:2000],
        }
        paginas.append(pagina)
    return paginas


def _montar_prompt(paginas):
    linhas = []
    linhas.append("A seguir estao os dados extraidos de uma varredura automatizada de um portal web.")
    linhas.append("Com base nisso, produza um documento de requisitos e documentacao da plataforma.")
    linhas.append("")
    linhas.append("## Paginas mapeadas")
    for pagina in paginas:
        linhas.append(f"### Rota: {pagina['rota']}")
        linhas.append(f"Titulo: {pagina['titulo']}")
        if pagina["headings"]:
            linhas.append(f"Headings: {', '.join(pagina['headings'])}")
        if pagina["botoes"]:
            linhas.append(f"Botoes: {', '.join(pagina['botoes'])}")
        if pagina["campos"]:
            linhas.append("Campos de formulario:")
            for campo in pagina["campos"]:
                linhas.append(f"  - tipo={campo['tipo']} placeholder={campo['placeholder']} label={campo['label']}")
        if pagina["links"]:
            linhas.append("Links internos:")
            for link in pagina["links"]:
                linhas.append(f"  - {link['href']}: {link['texto'][:80]}")
        if pagina["textos"]:
            linhas.append(f"Texto relevante: {pagina['textos'][:500]}")
        linhas.append("")
    linhas.append("## Saida esperada")
    linhas.append("Gere um documento em markdown com:")
    linhas.append("1. Resumo executivo da plataforma")
    linhas.append("2. Modulos e funcionalidades identificados")
    linhas.append("3. Fluxo de autenticacao e usuarios")
    linhas.append("4. Catálogo de produtos e categorias")
    linhas.append("5. Formularios e campos por tela")
    linhas.append("6. Requisitos funcionais para replicacao")
    linhas.append("7. Requisitos nao funcionais")
    linhas.append("8. Modelo de dados sugerido (entidades e relacionamentos)")
    linhas.append("")
    linhas.append("Nao inclua senhas, tokens, chaves de api ou dados pessoais reais.")
    return "\n".join(linhas)


def _chamar_ollama(prompt):
    if not OLLAMA_API_KEY:
        raise RuntimeError("OLLAMA_API_KEY deve estar definida no .env")
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": "Voce e um especialista em analise de requisitos de software e documentacao de plataformas web."},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }
    endpoints = [
        f"{OLLAMA_BASE_URL}/v1/chat/completions",
        f"{OLLAMA_BASE_URL}/api/chat",
    ]
    ultimo_erro = None
    for url in endpoints:
        try:
            headers = {"Authorization": f"Bearer {OLLAMA_API_KEY}"}
            if "v1" in url:
                headers["Content-Type"] = "application/json"
            resposta = requests.post(url, json=payload, headers=headers, timeout=120)
            if resposta.status_code == 200:
                resultado = resposta.json()
                if "message" in resultado:
                    return resultado["message"]["content"]
                return resultado["choices"][0]["message"]["content"]
            ultimo_erro = f"HTTP {resposta.status_code}: {resposta.text[:200]}"
        except requests.RequestException as erro:
            ultimo_erro = str(erro)
    raise RuntimeError(f"Erro ao chamar Ollama: {ultimo_erro}")


def _salvar_relatorio(conteudo):
    os.makedirs(PASTA_RELATORIOS, exist_ok=True)
    caminho = f"{PASTA_RELATORIOS}/requisitos_plataforma.md"
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo)
    return caminho


def gerar_relatorio():
    analise = _carregar_json(f"{PASTA_RELATORIOS}/analise.json")
    paginas = _extrair_dados_para_llm(analise)
    prompt = _montar_prompt(paginas)
    relatorio = _chamar_ollama(prompt)
    caminho = _salvar_relatorio(relatorio)
    return caminho


if __name__ == "__main__":
    caminho = gerar_relatorio()
    print(f"Relatorio salvo em: {caminho}")
