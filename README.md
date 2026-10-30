# Bot de Teste Automatizado — Portal de Representação Comercial

Bot de teste automatizado para portal web, com foco em autenticação por CNPJ e análise profunda das funcionalidades acessíveis após o login.

## Objetivo

- Autenticar no portal via login por CNPJ/senha
- Analisar as telas e funcionalidades acessíveis após o login (catálogo, pedidos, comissões, relatórios)
- Registrar erros de console, falhas de requisição e estruturas de formulários encontrados
- Gerar um mapa do site (sitemap) e capturas de tela por rota para uso como referência na construção de uma plataforma similar

## Stack

- Python 3.10+
- Playwright (automação de navegador)
- python-dotenv (variáveis de ambiente)
- pytest (testes unitários)

## Estrutura de diretórios

```
bot-teste-portal/
├── bots/
│   ├── __init__.py
│   ├── main.py
│   ├── registrar_conta.py
│   ├── fazer_login.py
│   ├── analisar_plataforma.py
│   └── crawler.py
├── tests/
│   ├── __init__.py
│   └── test_crawler.py
├── assets/
├── reports/
├── .env.example
├── .env (ignorado pelo git)
├── .gitignore
├── pyproject.toml
└── README.md
```

## Configuração

Copie o exemplo de variáveis de ambiente:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com os valores do seu ambiente. O arquivo `.env` está no `.gitignore` e nunca deve ser versionado.

| Variável | Descrição | Obrigatório |
|---|---|---|
| `BASE_URL` | URL base do portal | Sim |
| `LOGIN_URL` | URL da página de login | Sim |
| `LOGIN_CNPJ` | CNPJ usado para autenticação | Sim |
| `LOGIN_SENHA` | Senha usada para autenticação | Sim |
| `HEADLESS` | Executa o browser sem interface (`true`/`false`) | Não |
| `PASTA_RELATORIOS` | Diretório de saída dos relatórios | Não |

> **Segurança:** nunca informe credenciais reais no `.env.example` e nunca faça commit do `.env`. Mantenha senhas fora do repositório.

## Execução

```bash
uv sync
uv run playwright install chromium
uv run python -m bots.main
```

Ou via console script:

```bash
bot-teste
```

## Relatório gerado

- `reports/analise.json`: estado capturado das rotas visitadas após o login
- `reports/sitemap.json`: varredura controlada da estrutura do site com profundidade e metadados
- `reports/screenshots/`: capturas de tela por rota e por crawler

## Gráficos de resultados (exemplos genéricos)

Os diagramas abaixo ilustram a estrutura de saída do bot e mésticas típicas de uma varredura. Eles não contêm dados do portal alvo.

### Fluxo de automação

```mermaid
flowchart TD
    A[Iniciar navegador] --> B[Acessar página de login]
    B --> C[Autenticar com CNPJ/senha]
    C --> D[Mapear rotas internas]
    D --> E[Capturar formulários e botões]
    E --> F[Detectar erros de console e rede]
    F --> G[Gerar relatórios JSON]
    G --> H[Salvar capturas de tela]
```

### Camadas de profundidade do crawler

```mermaid
graph TD
    L0[Página inicial - profundidade 0]
    L1[Rotas diretas - profundidade 1]
    L2[Rotas secundárias - profundidade 2]
    L3[Rotas terciárias - profundidade 3]
    L0 --> L1
    L1 --> L2
    L2 --> L3
```

### Exemplo de dashboard de métricas (representativo)

```mermaid
pie title Distribuição de elementos por tipo de página
    "Formulários" : 35
    "Listagens" : 30
    "Painéis" : 20
    "Outros" : 15
```

## Fluxo de automação

1. Acessar a página de login definida em `LOGIN_URL`
2. Autenticar com `LOGIN_CNPJ` e `LOGIN_SENHA`
3. Navegar para a página inicial após o login
4. Coletar links internos acessíveis
5. Executar varredura controlada das rotas descobertas
6. Capturar formulários, botões, textos, erros de console e falhas de requisição
7. Salvar relatórios em JSON e capturas de tela por rota

## Testes

Executar a suíte de testes unitários:

```bash
uv run pytest
```

## Segurança e uso responsável

- Execute varreduras apenas em portais dos quais você tem autorização explícita
- Respeite o `robots.txt` e adicione intervalos entre requisições para não sobrecarregar o servidor
- Não inclua senhas, tokens ou dados pessoais reais nos relatórios gerados
- Os relatórios e capturas ficam locais e não devem ser publicados sem revisão

## Plataforma similar na Vercel (gratuita)

O objetivo final é construir uma plataforma própria para empresa de representação comercial, hospedada 100% na nuvem da Vercel no plano gratuito (Hobby), com frontend e backend em JavaScript.

### Stack recomendada

| Camada | Tecnologia | Custo (Vercel Hobby) |
|---|---|---|
| Frontend | Next.js (App Router) + React | Gratuito |
| Backend | Vercel Serverless Functions (API Routes) | Gratuito |
| Banco de dados | Vercel Postgres (nível gratuito) ou Supabase Free | Gratuito |
| Deploy | GitHub + Vercel (automático) | Gratuito |

### Funcionalidades alvo (espelhando o portal varrido)

- Autenticação por CNPJ/CPF e senha
- Cadastro de representantes e clientes
- Catálogo de produtos com preços e tabelas
- Emissão e acompanhamento de pedidos
- Cálculo de comissões por representante
- Relatórios de faturamento e vendas
- Painel administrativo

### Estrutura sugerida do projeto JS

```
plataforma-representacao/
├── app/                 # Next.js App Router (frontend + rotas de API)
│   ├── login/           # Página de autenticação CNPJ/senha
│   ├── dashboard/       # Painel principal
│   ├── catalogo/        # Listagem de produtos
│   ├── pedidos/         # Emissão e consulta de pedidos
│   ├── comissoes/       # Cálculo de comissões
│   ├── relatorios/      # Relatórios de faturamento
│   └── api/             # Serverless Functions (backend)
├── components/          # Componentes React reutilizáveis
├── lib/                 # Prisma/DB client, utilitários
├── prisma/              # Esquema do banco (Vercel Postgres)
├── .env.example         # Variáveis de ambiente (não commitadas)
├── .env.local           # Variáveis locais (ignorado pelo git)
├── next.config.js
├── package.json
└── README.md
```

### Variáveis de ambiente (configurar no dashboard da Vercel)

```
DATABASE_URL=postgresql://...
NEXTAUTH_SECRET=
NEXTAUTH_URL=https://seu-dominio.vercel.app
```

### Passos de deploy na Vercel

1. Criar repositório GitHub com o código JS/Next.js
2. Conectar o repositório na Vercel (vercel.com)
3. Adicionar variáveis de ambiente no dashboard da Vercel (Project Settings > Environment Variables)
4. Criar banco Vercel Postgres no painel da Vercel e vincular ao projeto
5. Fazer push — o deploy é automático a cada commit na branch principal

### Limites do plano gratuito da Vercel (Hobby)

- Bandwidth: 100 GB/mês
- Build minutos: 6.000/mês
- Serverless Function invocações: 100.000/dia
- Banco Postgres: limites do hobby (suficiente para MVP)

