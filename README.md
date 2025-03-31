# Airbnb Scraper

Um sistema de scraping e análise inteligente de anúncios do Airbnb, utilizando tecnologias modernas para obter, extrair e armazenar informações relevantes de listagens.

## Funcionalidades

- Scraping de páginas do Airbnb usando Puppeteer (JavaScript) ou Deno
- Extração inteligente de texto e metadados com Python (BeautifulSoup e Trafilatura)
- Armazenamento de dados em Supabase (PostgreSQL)
- Processamento em lote de múltiplas listagens
- Sistema de logs para monitoramento de execuções
- Captura de screenshots para debugging
- Comparação de scrapes para detectar mudanças em listagens ao longo do tempo

## Estrutura do Projeto

```
.
├── output/                # Diretório para arquivos HTML capturados
├── extracted/             # Diretório para dados extraídos (JSON e texto)
├── screenshots/           # Diretório para screenshots (debugging)
├── comparison_reports/    # Diretório para relatórios de comparação
├── batch_scraper.sh       # Script principal para execução em lote
├── run_scraper.sh         # Script para execução individual
├── extract_text.sh        # Script para extração de texto
├── compare_scrapes.sh     # Script para comparar diferentes scrapes
├── compare_scrapes.py     # Implementação da comparação de scrapes
├── text_extractor.py      # Extrator de texto/metadados (Python)
├── supabase_updater.py    # Integração com Supabase (Python)
├── get_rooms.py           # Obtém os IDs dos quartos do Supabase
└── README.md              # Este arquivo
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
# Obter IDs disponíveis na tabela rooms
python get_rooms.py

# Apenas capturar o HTML (substitua ROOM_ID por um ID válido da tabela rooms)
./run_scraper.sh ROOM_ID

# Capturar e extrair texto
./run_scraper.sh ROOM_ID ./output puppeteer extract

# Capturar, extrair e atualizar Supabase
./run_scraper.sh ROOM_ID ./output puppeteer extract-supabase
```

### Executar Scraping em Lote

```bash
./batch_scraper.sh [--limit NUMERO] [--extract] [--update-supabase] [--compare] [--compare-format=FORMAT]
```

Exemplos:
```bash
# Processar todos os anúncios registrados no Supabase
./batch_scraper.sh --update-supabase

# Processar apenas 5 anúncios
./batch_scraper.sh --limit=5 --update-supabase

# Apenas capturar HTML sem atualizar o Supabase
./batch_scraper.sh

# Processar anúncios e comparar com versões anteriores (formato HTML)
./batch_scraper.sh --extract --compare

# Processar anúncios e gerar relatório de comparação em JSON
./batch_scraper.sh --extract --compare --compare-format=json
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

### Listar Room IDs Disponíveis

Para listar todos os IDs de quartos (room_ids) disponíveis na tabela 'rooms':

```bash
python get_rooms.py
```

Utilize estes IDs como parâmetro ao executar o scraper individualmente.

### Criar Tabela de Logs

```bash
# SQL (recomendado)
# Execute o SQL em create_logs_table.sql no Editor SQL do Supabase

# Ou tente criar via API
python create_logs_table_directly.py
```

### Comparar Scrapes do Airbnb

Para detectar mudanças em listagens do Airbnb ao longo do tempo:

```bash
./compare_scrapes.sh [--room-id=ID] [--format=FORMAT]
```

Exemplos:
```bash
# Comparar todas as versões de todos os quartos (relatório HTML)
./compare_scrapes.sh

# Comparar versões específicas de um quarto
./compare_scrapes.sh --room-id=123456789

# Gerar relatório em formato específico (html, json, txt)
./compare_scrapes.sh --format=json
```

Os relatórios são salvos no diretório `./comparison_reports` por padrão.

## Workflow Recomendado

1. **Configuração Inicial**:
   - Configure as variáveis de ambiente para Supabase
   - Crie a tabela `logs` no Supabase (use o SQL fornecido)
   - Adicione anúncios do Airbnb na tabela `rooms`

2. **Verificação dos Room IDs**:
   - Liste os IDs disponíveis na tabela `rooms`:
     ```bash
     python get_rooms.py
     ```

3. **Execução**:
   - Execute o script de processamento em lote:
     ```bash
     ./batch_scraper.sh --update-supabase
     ```
   - Ou processe um anúncio específico:
     ```bash
     ./run_scraper.sh ROOM_ID ./output puppeteer extract-supabase
     ```

4. **Monitoramento**:
   - Verifique os logs no Supabase para acompanhar as execuções
   
5. **Análise de Mudanças**:
   - Compare diferentes versões dos scrapes para detectar alterações:
     ```bash
     ./batch_scraper.sh --extract --compare
     ```
   - Ou execute a comparação separadamente:
     ```bash
     ./compare_scrapes.sh --format=html
     ```

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

### IDs de Quartos

- Este projeto foi atualizado para não utilizar IDs fixos codificados diretamente nos scripts
- Todos os IDs de quartos devem ser obtidos da tabela 'rooms' no Supabase
- Use `python get_rooms.py` para obter os IDs disponíveis
- Se precisar adicionar novos IDs, insira-os diretamente na tabela 'rooms' através do painel do Supabase