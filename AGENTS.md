# agents.md — Regras e Contexto do Repositório

## O que é este repositório

Bot de teste automatizado para portal web de representação comercial. Autentica via e-mail/senha, mapeia funcionalidades após o login, captura erros de console, falhas de requisição e estruturas de formulários. Gera relatórios JSON e capturas de tela por rota. O objetivo é extrair as features para construir uma plataforma similar hospedada gratuitamente na Vercel (frontend e backend em JavaScript, banco gratuito).

## Regras de código

- Não usar comentários internos nos arquivos Python
- Não usar docstrings informativas
- Manter funções curtas e com nomes autoexplicativos
- Arquivos úteis (screenshots de debug, HTML salvo) devem ser movidos para `reports/arquivos_uteis/`, nunca ficar na raiz
- Arquivos inúteis (scripts de debug temporários, HTML salvo) devem ser removidos ao final da execução
- O arquivo `.env` contém credenciais e está no `.gitignore` — nunca commitar
- O `.env.example` contém apenas placeholders, sem credenciais reais

## Variáveis de ambiente obrigatórias (.env)

- `BASE_URL`: URL base do portal
- `LOGIN_URL`: URL da página de login
- `LOGIN_EMAIL`: e-mail usado para autenticação
- `LOGIN_SENHA`: senha usada para autenticação
- `HEADLESS`: `true` ou `false` (padrão: `true`)
- `PASTA_RELATORIOS`: diretório de saída dos relatórios (padrão: `reports`)

## Fluxo de execução

1. `uv sync --only-group dev`
2. `uv run playwright install chromium`
3. `uv run python -m bots.main`
4. Relatórios gerados em `reports/analise.json` e `reports/sitemap.json`
5. Capturas em `reports/screenshots/`
6. Limpeza automática de arquivos inúteis e move arquivos úteis para `reports/arquivos_uteis/`

## Testes

- Executar: `uv run pytest`
- Testes unitários em `tests/test_crawler.py`

## Hospedagem na Vercel

- Frontend: Next.js (App Router) + React
- Backend: Vercel Serverless Functions (API Routes)
- Banco: Vercel Postgres (nível gratuito) ou Supabase Free
- Variáveis de ambiente configuradas no dashboard da Vercel
- Deploy automático via GitHub
