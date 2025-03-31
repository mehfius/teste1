# Usando o Airbnb Scraper com Docker

Este documento explica como usar o Airbnb Scraper dentro de um contêiner Docker, o que facilita a execução em qualquer ambiente sem se preocupar com dependências.

## Pré-requisitos

- [Docker](https://www.docker.com/get-started) instalado
- [Docker Compose](https://docs.docker.com/compose/install/) (opcional, mas recomendado)

## Opções de Execução

### 1. Usando Docker Compose (Recomendado)

O Docker Compose facilita a execução e a configuração do contêiner:

```bash
# Construir e executar o contêiner com o ID padrão (756587219584104742)
docker-compose up --build

# Executar com um ID personalizado
docker-compose run --rm airbnb-scraper NOVO_ID_DO_QUARTO

# Executar em background (modo daemon)
docker-compose up -d
```

### 2. Usando Docker Diretamente

Você também pode usar os comandos Docker padrão:

```bash
# Construir a imagem
docker build -t airbnb-scraper .

# Executar com o ID padrão
docker run --rm -v $(pwd)/docker_output:/app/output airbnb-scraper

# Executar com um ID personalizado
docker run --rm -v $(pwd)/docker_output:/app/output airbnb-scraper NOVO_ID_DO_QUARTO
```

## Persistência de Dados

Os arquivos HTML extraídos são salvos no diretório `docker_output/` na sua máquina local, que está mapeado para o diretório `/app/output` dentro do contêiner.

## Configurações Avançadas

### Modificar o Dockerfile

Você pode modificar o `Dockerfile` para ajustar configurações como:

- Versão do Deno
- Configurações de timeout
- Número de tentativas em caso de falha

### Modificar o Docker Compose

Edite o arquivo `docker-compose.yml` para:

- Mudar a zona de tempo
- Configurar execuções agendadas (adicionando um serviço cron)
- Modificar o volume de saída

## Solução de Problemas

Se encontrar problemas:

1. Verifique se os arquivos `Dockerfile` e `docker-compose.yml` estão corretos
2. Verifique se as permissões do volume estão corretas
3. Teste executando com um ID de quarto válido do Airbnb

## Automatização com Cron

Para execuções programadas, você pode adicionar ao `docker-compose.yml`:

```yaml
services:
  airbnb-scraper-cron:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - ./docker_output:/app/output
    entrypoint: /bin/sh
    command: -c "echo '0 */6 * * * /app/run_scraper.sh 756587219584104742 >> /var/log/cron.log 2>&1' > /etc/crontabs/root && crond -f"
```

Isso executará o scraper a cada 6 horas.