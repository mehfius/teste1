# Usando o Airbnb Scraper com Docker

Este documento explica como usar o Airbnb Scraper dentro de um contêiner Docker, o que facilita a execução em qualquer ambiente sem se preocupar com dependências.

## Pré-requisitos

- [Docker](https://www.docker.com/get-started) instalado
- [Docker Compose](https://docs.docker.com/compose/install/) (opcional, mas recomendado)
- Credenciais do Supabase (URL e chave de API) para usar o serviço full-scraper

## Opções de Serviços

O projeto oferece três variantes do scraper via Docker:

1. **airbnb-scraper**: Versão básica com Deno (apenas scraping)
2. **puppeteer-scraper**: Usando Puppeteer para melhor renderização de JavaScript
3. **full-scraper**: Versão completa com Python, Puppeteer e integração com Supabase

## Opções de Execução

### 1. Usando Docker Compose (Recomendado)

O Docker Compose facilita a execução e a configuração do contêiner:

```bash
# Executar a versão básica com o ID padrão (756587219584104742)
docker-compose up --build airbnb-scraper

# Executar a versão com Puppeteer 
docker-compose up --build puppeteer-scraper

# Executar a versão completa com suporte a Python e Supabase
# Primeiro configure as variáveis de ambiente
export SUPABASE_URL=sua_url_supabase
export SUPABASE_KEY=sua_chave_supabase
docker-compose up --build full-scraper

# Executar processamento em lote de todos os quartos do Supabase
docker-compose run --rm full-scraper --update-supabase

# Executar em background (modo daemon)
docker-compose up -d full-scraper
```

### 2. Usando Docker Diretamente

Você também pode usar os comandos Docker padrão:

```bash
# Construir a imagem completa
docker build -t airbnb-full-scraper -f Dockerfile.full .

# Executar com processamento em lote
docker run --rm \
  -v $(pwd)/docker_output:/app/output \
  -v $(pwd)/screenshots:/app/screenshots \
  -v $(pwd)/extracted:/app/extracted \
  -e SUPABASE_URL=sua_url_supabase \
  -e SUPABASE_KEY=sua_chave_supabase \
  airbnb-full-scraper --update-supabase
```

## Persistência de Dados

Os dados são persistidos nos seguintes diretórios:

- `docker_output/`: Arquivos HTML extraídos
- `screenshots/`: Capturas de tela das páginas do Airbnb
- `extracted/`: Arquivos de texto extraídos (.txt e .json)

## Configurações Avançadas

### Opções do Dockerfile.full

O `Dockerfile.full` combina todas as dependências necessárias:

- Node.js e Puppeteer para scraping
- Python 3 para processamento de texto
- Bibliotecas para extração de texto (trafilatura, beautifulsoup4)
- Supabase SDK para atualizações de banco de dados

### Variáveis de Ambiente para Supabase

Para usar a integração com o Supabase, defina as seguintes variáveis:

```
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-de-api
```

Essas variáveis podem ser definidas no sistema antes de executar `docker-compose` ou adicionadas a um arquivo `.env` no mesmo diretório do `docker-compose.yml`.

## Automatização com Cron

Para execuções programadas, você pode adicionar ao `docker-compose.yml`:

```yaml
services:
  airbnb-scraper-cron:
    build:
      context: .
      dockerfile: Dockerfile.full
    volumes:
      - ./docker_output:/app/output
      - ./screenshots:/app/screenshots
      - ./extracted:/app/extracted
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    entrypoint: /bin/sh
    command: -c "echo '0 */6 * * * /app/batch_scraper.sh --update-supabase >> /var/log/cron.log 2>&1' > /etc/crontabs/root && crond -f"
```

Isso executará o processamento em lote a cada 6 horas.