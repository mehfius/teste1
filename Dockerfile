FROM denoland/deno:1.40.1

WORKDIR /app

# Copiar os arquivos do projeto
COPY deps.ts .
COPY main.ts .
COPY scraper.ts .
COPY utils.ts .
COPY run_scraper.sh .

# Criar diretório de saída
RUN mkdir -p output

# Dar permissão de execução ao script
RUN chmod +x run_scraper.sh

# Configurar variáveis de ambiente
ENV PATH="${PATH}:/root/.deno/bin"

# Pré-baixar dependências
RUN deno cache deps.ts

# Comando padrão (pode ser substituído no momento da execução)
ENTRYPOINT ["./run_scraper.sh"]

# Argumento padrão para o ENTRYPOINT
CMD ["756587219584104742"]