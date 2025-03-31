# Airbnb Scraper

Um sistema de scraping e análise inteligente de anúncios do Airbnb, utilizando tecnologias modernas para obter, extrair e armazenar informações relevantes de listagens.

## Funcionalidades

- Scraping de páginas do Airbnb usando Puppeteer (JavaScript) ou Deno
- Extração inteligente de texto e metadados com Python (BeautifulSoup e Trafilatura)
- Armazenamento de dados em Supabase (PostgreSQL)
- Processamento em lote de múltiplas listagens
- Sistema de logs para monitoramento de execuções
- Captura de screenshots para debugging

## Estrutura do Projeto

```
.
├── output/            # Diretório para arquivos HTML capturados
├── extracted/         # Diretório para dados extraídos (JSON e texto)
├── screenshots/       # Diretório para screenshots (debugging)
├── batch_scraper.sh   # Script principal para execução em lote
├── run_scraper.sh     # Script para execução individual
├── extract_text.sh    # Script para extração de texto
├── text_extractor.py  # Extrator de texto/metadados (Python)
├── supabase_updater.py # Integração com Supabase (Python)
└── README.md          # Este arquivo
```

## Dependências

### Python
- beautifulsoup4
- trafilatura
- supabase
- requests

### Node.js
- puppeteer
- @supabase/supabase-js

## Configuração

### Variáveis de Ambiente

Crie as seguintes variáveis de ambiente:

```
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_do_supabase
```

### Estrutura do Banco de Dados (Supabase)

O projeto utiliza duas tabelas principais:

1. **rooms**: Armazena informações sobre os anúncios do Airbnb
   - `id`: UUID (primary key)
   - `room_id`: String (ID do anúncio no Airbnb)
   - `label`: String (título do anúncio)
   - `created_at`: Timestamp

2. **logs**: Registra informações sobre as execuções do scraper
   - `id`: UUID (primary key)
   - `service_time`: Float (tempo de execução em segundos)
   - `room_ids`: Integer[] (array de IDs processados)
   - `success_count`: Integer (número de sucessos)
   - `total_count`: Integer (número total de tentativas)
   - `created_at`: Timestamp

Para criar a tabela de logs, execute o SQL em `create_logs_table.sql` no Editor SQL do Supabase.

## Uso

### Executar Scraping de um Anúncio Individual

```bash
./run_scraper.sh ROOM_ID [OUTPUT_DIR] [SCRAPER_TYPE] [ACTION]
```

Exemplos:
```bash
# Apenas capturar o HTML
./run_scraper.sh 756587219584104742

# Capturar e extrair texto
./run_scraper.sh 756587219584104742 ./output puppeteer extract

# Capturar, extrair e atualizar Supabase
./run_scraper.sh 756587219584104742 ./output puppeteer extract-supabase
```

### Executar Scraping em Lote

```bash
./batch_scraper.sh [--limit NUMERO] [--extract] [--update-supabase]
```

Exemplos:
```bash
# Processar todos os anúncios registrados no Supabase
./batch_scraper.sh --update-supabase

# Processar apenas 5 anúncios
./batch_scraper.sh --limit=5 --update-supabase

# Apenas capturar HTML sem atualizar o Supabase
./batch_scraper.sh
```

### Extrair Texto dos Arquivos HTML

```bash
./extract_text.sh [--input-dir=DIR] [--output-dir=DIR] [--format=FORMAT] [--update-supabase]
```

Exemplos:
```bash
# Extrair texto de todos os arquivos HTML
./extract_text.sh

# Extrair e atualizar Supabase
./extract_text.sh --update-supabase
```

## Utilitários

### Verificar Estrutura da Tabela

```bash
python check_table_structure.py NOME_DA_TABELA
```

### Contar Registros na Tabela

```bash
python count_records.py NOME_DA_TABELA
```

### Criar Tabela de Logs

```bash
# SQL (recomendado)
# Execute o SQL em create_logs_table.sql no Editor SQL do Supabase

# Ou tente criar via API
python create_logs_table_directly.py
```

## Workflow Recomendado

1. **Configuração Inicial**:
   - Configure as variáveis de ambiente para Supabase
   - Crie a tabela `logs` no Supabase (use o SQL fornecido)
   - Adicione anúncios do Airbnb na tabela `rooms`

2. **Execução**:
   - Execute o script de processamento em lote:
     ```bash
     ./batch_scraper.sh --update-supabase
     ```

3. **Monitoramento**:
   - Verifique os logs no Supabase para acompanhar as execuções

## Troubleshooting

### Problemas com Tabela de Logs

Se encontrar problemas com a tabela de logs, como erros de coluna não encontrada:

1. Verifique a estrutura atual:
   ```bash
   python check_table_structure.py logs
   ```

2. Recriar a tabela:
   - Use o SQL em `create_logs_table.sql` no Editor SQL do Supabase

### Falhas no Scraping

- Verifique os arquivos de log
- Verifique se o Puppeteer está funcionando corretamente
- Tente usar o scraper Deno como alternativa