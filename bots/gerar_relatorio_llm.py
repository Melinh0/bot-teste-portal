import json
import os

import requests

from dotenv import load_dotenv
load_dotenv()

PASTA_RELATORIOS = os.getenv("PASTA_RELATORIOS", "reports")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "https://api.ollama.com")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:31b-cloud")


def _carregar_json(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def _extrair_paginas(analise):
    paginas = []
    for entrada in analise:
        pagina = {
            "rota": entrada.get("rota") or entrada.get("rota_crawler") or entrada.get("url"),
            "titulo": entrada.get("titulo"),
            "headings": entrada.get("headings", []),
            "botoes": entrada.get("botoes", []),
            "campos": [
                {
                    "tipo": c.get("type"),
                    "placeholder": c.get("placeholder"),
                    "label": c.get("aria_label"),
                    "id": c.get("id"),
                    "name": c.get("name"),
                }
                for c in entrada.get("campos", [])
            ],
            "links": [
                {"href": l.get("href"), "texto": l.get("texto")}
                for l in entrada.get("links", [])
            ],
            "textos": entrada.get("textos", "")[:2000],
            "erros": entrada.get("erros", []),
            "falhas": entrada.get("falhas", []),
        }
        paginas.append(pagina)
    return paginas


def _extrair_sitemap(sitemap):
    rotas = []
    for entrada in sitemap:
        rotas.append({
            "rota": entrada.get("rota_crawler") or entrada.get("rota") or entrada.get("url"),
            "profundidade": entrada.get("profundidade"),
        })
    return rotas


def _montar_prompt(paginas, rotas_sitemap):
    linhas = []
    linhas.append("Voce e um especialista em analise de requisitos de software e documentacao de plataformas web.")
    linhas.append("A seguir estao os dados extraidos de uma varredura automatizada de um portal web de representacao comercial.")
    linhas.append("Com base nisso, produza um documento de requisitos detalhado e estruturado para replicacao da plataforma.")
    linhas.append("")
    linhas.append("# Dados das paginas mapeadas")
    for pagina in paginas:
        linhas.append(f"## Rota: {pagina['rota']}")
        linhas.append(f"Titulo: {pagina['titulo']}")
        if pagina["headings"]:
            linhas.append(f"Headings: {', '.join(pagina['headings'])}")
        if pagina["botoes"]:
            linhas.append(f"Botoes: {', '.join(pagina['botoes'])}")
        if pagina["campos"]:
            linhas.append("Campos de formulario:")
            for campo in pagina["campos"]:
                linhas.append(f"  - tipo={campo['tipo']} placeholder={campo['placeholder']} label={campo['label']} id={campo['id']} name={campo['name']}")
        if pagina["links"]:
            linhas.append("Links internos:")
            for link in pagina["links"]:
                linhas.append(f"  - {link['href']}: {link['texto'][:80]}")
        if pagina["erros"]:
            linhas.append("Erros de console:")
            for erro in pagina["erros"][:5]:
                linhas.append(f"  - {erro.get('tipo')}: {erro.get('texto')[:100]}")
        if pagina["falhas"]:
            linhas.append("Falhas de requisicao:")
            for falha in pagina["falhas"][:5]:
                linhas.append(f"  - {falha.get('url')}: {falha.get('erro')[:100]}")
        if pagina["textos"]:
            linhas.append(f"Texto relevante: {pagina['textos'][:600]}")
        linhas.append("")
    linhas.append("# Rotas do sitemap")
    for rota in rotas_sitemap:
        linhas.append(f"- {rota['rota']} (profundidade {rota['profundidade']})")
    linhas.append("")
    linhas.append("# Saida esperada")
    linhas.append("Gere um documento em markdown com as secoes abaixo, mantendo essa ordem e esses titulos exatos:")
    linhas.append("1. Resumo Executivo")
    linhas.append("2. Atores e Papéis de Usuario")
    linhas.append("3. Fluxo de Autenticacao e Cadastro de Loja")
    linhas.append("4. Catalogo de Funcionalidades por Modulo")
    linhas.append("5. Requisitos Funcionais (RF-001 a RF-N) com descricao, prioridade e criterios de aceitacao")
    linhas.append("6. Requisitos Nao Funcionais (desempenho, seguranca, usabilidade, compatibilidade)")
    linhas.append("7. Modelo de Dados Sugerido (entidades, atributos e relacionamentos)")
    linhas.append("8. Endpoints e Rotas Mapeados")
    linhas.append("9. Formularios e Campos por Tela")
    linhas.append("10. Regras de Negocio")
    linhas.append("11. Navegacao e Experiencia do Usuario")
    linhas.append("12. Riscos e Dependencias")
    linhas.append("13. Glossario")
    linhas.append("14. Anexo: Mapa do Site Resumido")
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


def _salvar_arquivo(conteudo, nome_arquivo):
    os.makedirs(PASTA_RELATORIOS, exist_ok=True)
    caminho = f"{PASTA_RELATORIOS}/{nome_arquivo}"
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo)
    return caminho


def gerar_relatorio():
    analise = _carregar_json(f"{PASTA_RELATORIOS}/analise.json")
    paginas = _extrair_paginas(analise)
    try:
        sitemap = _carregar_json(f"{PASTA_RELATORIOS}/sitemap.json")
        rotas_sitemap = _extrair_sitemap(sitemap)
    except FileNotFoundError:
        rotas_sitemap = []
    prompt = _montar_prompt(paginas, rotas_sitemap)
    relatorio = _chamar_ollama(prompt)
    caminho = _salvar_arquivo(relatorio, "requisitos_plataforma.md")
    return caminho


if __name__ == "__main__":
    caminho = gerar_relatorio()
    print(f"Relatorio salvo em: {caminho}")
