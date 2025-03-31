# Airbnb HTML Scraper

Uma aplicação que extrai, salva e processa conteúdo de anúncios do Airbnb.

## Funcionalidades

- Extrai e salva o conteúdo HTML de anúncios do Airbnb
- Suporta dois métodos de scraping:
  - **Scraper Deno**: Baseado na API fetch (conteúdo HTML inicial)
  - **Scraper Puppeteer**: Captura conteúdo dinâmico carregado via JavaScript
- Extração de texto e metadados dos arquivos HTML
- Aceita o parâmetro room_id para identificar o anúncio
- Processa URLs como https://www.airbnb.com.br/rooms/756587219584104742
- Interface simples de linha de comando
- Tratamento de erros com tentativas automáticas de reconexão
- Script shell unificado para facilitar a execução
- Suporte para captura de screenshots (modo Puppeteer)
- Suporte para execução em Docker

## Pré-requisitos

- [Deno](https://deno.land/) instalado (o script de execução tentará instalar automaticamente se não estiver disponível)
- Conexão com a internet
- Permissões adequadas para acesso à rede e sistema de arquivos
- (Opcional) Docker e Docker Compose para execução em contêiner

## Instalação

Não é necessária instalação além do Deno, que o script pode instalar automaticamente.

## Uso

### 1. Usando o Script Shell Unificado (Recomendado)

```bash
# Formato básico
./run_scraper.sh ROOM_ID [OUTPUT_DIR] [SCRAPER_TYPE]

# Exemplos:
# Usando Puppeteer (padrão)
./run_scraper.sh 756587219584104742

# Usando Deno
./run_scraper.sh 756587219584104742 ./output deno

# Especificando diretório de saída personalizado
./run_scraper.sh 756587219584104742 ./custom_output
```

### 2. Usando Scripts Específicos

**Para o scraper Puppeteer:**
```bash
./run_puppeteer.sh ROOM_ID [OUTPUT_DIR] [SCREENSHOT_DIR]
```

**Para o scraper Deno:**
```bash
deno run --allow-net --allow-read --allow-write --allow-env main.ts --room-id=ROOM_ID [--output-dir=./output]
```

### 3. Usando Docker (Requer Docker instalado)

```bash
# Construir imagens
docker-compose build

# Executar o scraper baseado em Deno
docker-compose run --rm airbnb-scraper ROOM_ID

# Executar o scraper baseado em Puppeteer
docker-compose run --rm puppeteer-scraper ROOM_ID
```

### 4. Extração de conteúdo textual

```bash
# Usar o script shell simplificado (recomendado)
./extract_text.sh

# Com parâmetros personalizados
./extract_text.sh --input-dir=./output --output-dir=./extracted --format=both

# Ou usando o Python diretamente
# Processar um único arquivo
python text_extractor.py --input output/airbnb_756587219584104742_*.html

# Processar todos os arquivos de um diretório
python text_extractor.py --input-dir output --output-dir extracted
```

Veja o arquivo `DOCKER_README.md` para instruções detalhadas sobre o uso com Docker.

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

Usando Docker Compose com ID personalizado:
```bash
docker-compose run --rm airbnb-scraper 756587219584104742
```

Isso salvará o conteúdo HTML do anúncio do Airbnb no diretório de saída especificado (padrão: ./output).

## Como Funciona

### Scraper Deno (Conteúdo HTML Básico)
- Usa a API fetch nativa para baixar o conteúdo HTML dos anúncios do Airbnb
- Cabeçalhos user-agent realistas para simular um navegador
- Lógica de tentativas para lidar com problemas de rede
- Configurações de timeout personalizáveis
- Criação automática do diretório de saída

### Scraper Puppeteer (Conteúdo HTML Completo com JavaScript)
- Usa um navegador headless controlado por Puppeteer
- Aguarda o carregamento completo do JavaScript
- Captura o conteúdo dinâmico renderizado na página
- Suporte para captura de screenshots
- Filtro de requisições para melhorar o desempenho
- Lógica de tentativas e recuperação avançada

### Extrator de Texto
- Processa os arquivos HTML para extrair conteúdo textual estruturado
- Usa a biblioteca trafilatura para extrair texto limpo e semântico
- Identifica metadados importantes como título, preço, localização, etc.
- Exporta dados em formato JSON para análise posterior
- Organiza o conteúdo de texto em arquivos separados

Todos os componentes usam nomes de arquivos com timestamps para fácil rastreamento.

## Automação no Replit

Este projeto inclui uma configuração de fluxo de trabalho para o Replit que permite a execução automatizada do scraper. O workflow "Airbnb Scraper" executa o script para o ID de quarto especificado. Por padrão, o workflow agora usa o scraper baseado em Puppeteer para capturar conteúdo dinâmico.

Para alterar o tipo de scraper ou o ID do quarto, você pode:

1. Editar o arquivo `run_scraper.sh` para modificar o comportamento padrão
2. Adicionar um parâmetro adicional ao workflow:
   ```
   ./run_scraper.sh 756587219584104742 ./output deno
   ```

## Estrutura do Projeto

### Código Principal
- `main.ts`: Ponto de entrada para o scraper Deno
- `scraper.ts`: Implementação do scraper usando API fetch
- `utils.ts`: Funções utilitárias para operações de arquivo e validação
- `deps.ts`: Gerenciamento de dependências
- `puppeteer_scraper.js`: Implementação do scraper baseado em Puppeteer
- `text_extractor.py`: Script Python para extrair conteúdo textual dos arquivos HTML

### Scripts Shell
- `run_scraper.sh`: Script shell unificado (escolhe entre Deno e Puppeteer)
- `run_puppeteer.sh`: Script shell específico para o scraper Puppeteer
- `extract_text.sh`: Script shell para extrair texto dos arquivos HTML

### Docker
- `Dockerfile`: Configuração para criar uma imagem Docker do scraper Deno
- `Dockerfile.puppeteer`: Configuração para criar uma imagem Docker do scraper Puppeteer
- `docker-compose.yml`: Configuração para execução com Docker Compose
- `DOCKER_README.md`: Instruções detalhadas para execução com Docker

### Diretórios de Dados
- `output/`: Diretório onde os arquivos HTML são salvos
- `screenshots/`: Diretório para capturas de tela feitas pelo Puppeteer
- `extracted/`: Diretório para os dados extraídos (texto e JSON)
- `docker_output/`: Diretório para saída quando executado com Docker

## Modificando o ID do Quarto

Para modificar o ID do quarto a ser raspado, edite o parâmetro no arquivo `run_scraper.sh` ou adicione um novo workflow com o ID desejado.
