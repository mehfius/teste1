# Airbnb HTML Scraper

Uma aplicação Deno que extrai e salva conteúdo HTML de anúncios do Airbnb.

## Funcionalidades

- Extrai e salva o conteúdo HTML de anúncios do Airbnb
- Aceita o parâmetro room_id para identificar o anúncio
- Processa URLs como https://www.airbnb.com.br/rooms/756587219584104742
- Armazena o conteúdo HTML completo
- Interface simples de linha de comando
- Tratamento de erros com tentativas automáticas de reconexão
- Sem dependências de navegador (usa a API fetch)
- Script shell para facilitar a execução

## Pré-requisitos

- [Deno](https://deno.land/) instalado (o script de execução tentará instalar automaticamente se não estiver disponível)
- Conexão com a internet
- Permissões adequadas para acesso à rede e sistema de arquivos

## Instalação

Não é necessária instalação além do Deno, que o script pode instalar automaticamente.

## Uso

Você pode executar a aplicação de duas maneiras:

### 1. Usando o Script Shell (Recomendado)

```bash
./run_scraper.sh ROOM_ID [OUTPUT_DIR]
```

### 2. Usando Deno Diretamente

```bash
deno run --allow-net --allow-read --allow-write --allow-env main.ts --room-id=ROOM_ID [--output-dir=./output]
```

## Exemplos

Usando o script shell:
```bash
./run_scraper.sh 756587219584104742
```

Usando um diretório de saída personalizado:
```bash
./run_scraper.sh 756587219584104742 ./custom_output
```

Usando Deno diretamente:
```bash
deno run --allow-net --allow-read --allow-write --allow-env main.ts --room-id=756587219584104742
```

Isso salvará o conteúdo HTML do anúncio do Airbnb no diretório de saída especificado (padrão: ./output).

## Como Funciona

A aplicação usa a API fetch nativa para baixar o conteúdo HTML dos anúncios do Airbnb. Inclui:

- Cabeçalhos user-agent realistas para simular um navegador
- Lógica de tentativas para lidar com problemas de rede
- Configurações de timeout personalizáveis
- Criação automática do diretório de saída
- Nomes de arquivos com timestamps para fácil rastreamento

## Automação no Replit

Este projeto inclui uma configuração de fluxo de trabalho para o Replit que permite a execução automatizada do scraper. O workflow "Airbnb Scraper" executa o script para o ID de quarto especificado.

## Estrutura do Projeto

- `main.ts`: Ponto de entrada da aplicação
- `scraper.ts`: Implementação da classe AirbnbScraper
- `utils.ts`: Funções utilitárias para operações de arquivo e validação
- `deps.ts`: Gerenciamento de dependências
- `run_scraper.sh`: Script shell para simplificar a execução
- `output/`: Diretório onde os arquivos HTML são salvos

## Modificando o ID do Quarto

Para modificar o ID do quarto a ser raspado, edite o parâmetro no arquivo `run_scraper.sh` ou adicione um novo workflow com o ID desejado.
