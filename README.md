# Airbnb Scraper (Deno)

Um sistema de scraping para monitorar listagens do Airbnb, coletar dados e armazenar histórico de mudanças. Versão completa em Deno, sem dependências Python.

## Tecnologias

- Deno (runtime JavaScript/TypeScript)
- Supabase (banco de dados e autenticação)
- GitHub Actions (automação e agendamento)

## Funcionalidades

- Extrai o conteúdo HTML completo de anúncios do Airbnb
- Extrai informações principais como título, preço e avaliações
- Armazena os dados extraídos em formatos JSON e texto
- Salva os títulos dos anúncios no Supabase
- Registra logs de execução para rastrear o desempenho

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
deno run --allow-net --allow-env get_rooms.ts
```

### Executando o scraper para um quarto específico

```bash
./run_scraper.sh ROOM_ID ./output deno extract-supabase
```

### Executando o processamento em lote

```bash
./batch_scraper_simplified.sh
```

Opções:
- `--limit=N`: Limita o processamento a N quartos
- `--update-supabase`: Atualiza os títulos no Supabase (ativado por padrão)

### Verificando o status do Supabase

```bash
/home/runner/.deno/bin/deno run --allow-net --allow-env check_supabase.ts
```

Este comando verifica a conexão com o Supabase e exibe informações sobre as tabelas `rooms` e `logs`.

## Estrutura do projeto

- `deps.ts`: Dependências do Deno
- `main.ts`: Ponto de entrada principal
- `scraper.ts`: Implementação do scraper
- `utils.ts`: Funções utilitárias
- `text_extractor.ts`: Extrator de texto do HTML
- `supabase_updater.ts`: Gerenciador de atualizações no Supabase
- `get_rooms.ts`: Script para listar quartos no Supabase
- `check_supabase.ts`: Script para verificar o status do Supabase
- `batch_scraper_simplified.sh`: Script para processamento em lote
- `run_scraper.sh`: Script para executar o scraper para um quarto específico
- `extract_text.sh`: Script para extrair texto de arquivos HTML

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