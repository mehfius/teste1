# Airbnb Scraper (Deno) - Versão em Memória

Um sistema de scraping para monitorar listagens do Airbnb, coletar dados e atualizar um banco de dados Supabase. Esta versão otimizada processa todo o conteúdo em memória sem criar arquivos temporários.

## Tecnologias

- Deno (runtime JavaScript/TypeScript)
- Supabase (banco de dados e autenticação)
- Processamento em memória (sem arquivos temporários)

## Funcionalidades

- Extrai o conteúdo HTML dos anúncios do Airbnb diretamente em memória
- Extrai informações principais como título, preço e avaliações
- Atualiza os títulos dos anúncios no Supabase em tempo real
- Registra logs de execução para rastrear o desempenho
- Processamento completo sem criar arquivos temporários

## Configuração

### Pré-requisitos

- Deno instalado (versão 1.x ou superior)
- Conta no Supabase com as seguintes tabelas:
  - `rooms`: Para armazenar os IDs e títulos dos quartos
  - `logs`: Para registrar logs de execução

### Variáveis de ambiente

```
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_do_supabase
```

## Uso

### Listando os IDs de quartos disponíveis

```bash
deno run --allow-net --allow-env src/database/get_rooms.ts
```

### Executando o scraper para um quarto específico

```bash
bin/run_scraper.sh ROOM_ID
```

### Executando o processamento em lote

```bash
bin/batch_scraper_simplified.sh
```

Opções:
- `--limit=N`: Limita o processamento a N quartos
- `--update-supabase`: Opção mantida por compatibilidade (sempre ativada)

### Verificando o status do Supabase

```bash
deno run --allow-net --allow-env src/database/check_supabase.ts
```

Este comando verifica a conexão com o Supabase e exibe informações sobre as tabelas `rooms` e `logs`.

## Processamento em Memória

Esta versão foi totalmente otimizada para processar dados em memória:

1. O HTML é obtido da página do Airbnb e mantido em memória
2. A extração de informações acontece diretamente no conteúdo HTML em memória
3. Os dados extraídos são enviados diretamente para o Supabase
4. Nenhum arquivo temporário é criado durante o processo

## Estrutura do projeto

- `bin/`: Scripts executáveis
  - `batch_scraper_simplified.sh`: Script para processamento em lote em memória
  - `run_scraper.sh`: Script para executar o scraper para um quarto específico
  - `cleanup.sh`: Script para limpeza do ambiente
  - `extract_text.sh`: Script auxiliar para extração de texto
  - `run_puppeteer.sh`: Script para execução do Puppeteer (NodeJS)
- `src/`: Código fonte
  - `core/`: Implementação principal
    - `main.ts`: Ponto de entrada principal (modo memória)
    - `scraper.ts`: Implementação do scraper
    - `text_extractor.ts`: Extrator de texto do HTML
  - `database/`: Código relacionado ao banco de dados
    - `supabase_updater.ts`: Gerenciador de atualizações no Supabase
    - `get_rooms.ts`: Script para listar quartos no Supabase
    - `check_supabase.ts`: Script para verificar o status do Supabase
  - `utils/`: Utilitários
    - `deps.ts`: Dependências do Deno
    - `utils.ts`: Funções utilitárias
  - `scripts/`: Scripts auxiliares
    - `puppeteer_scraper.js`: Implementação alternativa usando Puppeteer
    - `supabase_uploader.js`: Implementação NodeJS para Supabase
    - `temp_log.js`: Utilitário de logging
- `config/`: Arquivos de configuração
  - `create_logs_table.sql`: SQL para criação da tabela de logs

## Banco de dados

### Tabela `rooms`

Estrutura:
- `id`: Chave primária gerada automaticamente
- `room_id`: ID do quarto no Airbnb (string numérica)
- `label`: Título do anúncio (opcional)
- `created_at`: Data de criação do registro

### Tabela `logs`

Estrutura:
- `id`: Chave primária gerada automaticamente
- `service_time`: Tempo de execução em segundos (número)
- `room_ids`: Lista de IDs dos quartos processados (array)
- `success_count`: Número de quartos processados com sucesso (número)
- `total_count`: Número total de quartos processados (número)
- `created_at`: Data de registro do log