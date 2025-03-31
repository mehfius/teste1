#!/bin/bash
# Script para extrair texto dos arquivos HTML do Airbnb (versão Deno)

# Definir diretórios padrão
INPUT_DIR="./output"
OUTPUT_DIR="./extracted"
FORMAT="both"  # Opções: json, text, both
UPDATE_SUPABASE=false  # Por padrão, não atualiza o Supabase

# Processar argumentos da linha de comando
while [[ $# -gt 0 ]]; do
  case $1 in
    --input-dir=*)
      INPUT_DIR="${1#*=}"
      shift
      ;;
    --output-dir=*)
      OUTPUT_DIR="${1#*=}"
      shift
      ;;
    --format=*)
      FORMAT="${1#*=}"
      shift
      ;;
    --update-supabase)
      UPDATE_SUPABASE=true
      shift
      ;;
    --help)
      echo "Uso: $0 [--input-dir=DIR] [--output-dir=DIR] [--format=FORMAT] [--update-supabase]"
      echo ""
      echo "Opções:"
      echo "  --input-dir=DIR    Diretório com arquivos HTML (padrão: ./output)"
      echo "  --output-dir=DIR   Diretório para salvar os resultados (padrão: ./extracted)"
      echo "  --format=FORMAT    Formato de saída: json, text ou both (padrão: both)"
      echo "  --update-supabase  Atualiza títulos extraídos no Supabase"
      echo "  --help             Mostra esta ajuda"
      exit 0
      ;;
    *)
      echo "Parâmetro desconhecido: $1"
      echo "Use --help para ver as opções disponíveis."
      exit 1
      ;;
  esac
done

# Verificar se o diretório de entrada existe
if [ ! -d "$INPUT_DIR" ]; then
  echo "Erro: Diretório de entrada '$INPUT_DIR' não existe."
  exit 1
fi

# Verificar se há arquivos HTML no diretório de entrada
HTML_COUNT=$(find "$INPUT_DIR" -name "*.html" | wc -l)
if [ $HTML_COUNT -eq 0 ]; then
  echo "Aviso: Nenhum arquivo HTML encontrado em '$INPUT_DIR'."
  exit 1
fi

echo "Iniciando extração de texto de $HTML_COUNT arquivos HTML..."
echo "  Diretório de entrada: $INPUT_DIR"
echo "  Diretório de saída: $OUTPUT_DIR"
echo "  Formato: $FORMAT"
echo ""

# Verificar se o Deno está instalado
if command -v deno &> /dev/null; then
  DENO_CMD="deno"
elif [ -f "/home/runner/.deno/bin/deno" ]; then
  DENO_CMD="/home/runner/.deno/bin/deno"
  export PATH="/home/runner/.deno/bin:$PATH"
else
  echo "Deno não encontrado. Instalando..."
  curl -fsSL https://deno.land/x/install/install.sh > install_deno.sh
  DENO_INSTALL=/home/runner/.deno sh install_deno.sh v1.40.1
  rm install_deno.sh
  
  if [ -f "/home/runner/.deno/bin/deno" ]; then
    DENO_CMD="/home/runner/.deno/bin/deno"
    export PATH="/home/runner/.deno/bin:$PATH"
  else
    echo "Falha ao instalar Deno. Saindo."
    exit 1
  fi
fi

# Construir os argumentos para o extrator Deno
DENO_ARGS="--allow-read --allow-write --allow-env"
CMD_ARGS="--input-dir=$INPUT_DIR --output-dir=$OUTPUT_DIR --format=$FORMAT"

if [ "$UPDATE_SUPABASE" = true ]; then
  CMD_ARGS="$CMD_ARGS --update-supabase"
  
  # Verificar variáveis de ambiente para Supabase
  echo "Verificando variáveis de ambiente para Supabase..."
  if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo "⚠️  Aviso: As variáveis de ambiente SUPABASE_URL e/ou SUPABASE_KEY não estão definidas."
    echo "    A atualização do Supabase pode falhar."
  else
    echo "✅ Variáveis de ambiente para Supabase encontradas."
    # Adicionar permissão de rede para o Deno
    DENO_ARGS="$DENO_ARGS --allow-net"
  fi
fi

# Executar o extrator de texto Deno
echo "Executando com Deno: $DENO_CMD run $DENO_ARGS text_extractor.ts $CMD_ARGS"
"$DENO_CMD" run $DENO_ARGS text_extractor.ts $CMD_ARGS

# Verificar o resultado
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
  echo ""
  echo "Extração de texto concluída com sucesso!"
  echo "Os arquivos extraídos estão disponíveis em: $OUTPUT_DIR"
else
  echo ""
  echo "Erro durante a extração de texto. Código de saída: $EXIT_CODE"
fi

exit $EXIT_CODE