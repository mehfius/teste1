#!/bin/bash
# Script para extrair texto dos arquivos HTML do Airbnb

# Definir diretórios padrão
INPUT_DIR="./output"
OUTPUT_DIR="./extracted"
FORMAT="both"  # Opções: json, text, both

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
    --help)
      echo "Uso: $0 [--input-dir=DIR] [--output-dir=DIR] [--format=FORMAT]"
      echo ""
      echo "Opções:"
      echo "  --input-dir=DIR    Diretório com arquivos HTML (padrão: ./output)"
      echo "  --output-dir=DIR   Diretório para salvar os resultados (padrão: ./extracted)"
      echo "  --format=FORMAT    Formato de saída: json, text ou both (padrão: both)"
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

# Executar o extrator de texto Python
python text_extractor.py --input-dir="$INPUT_DIR" --output-dir="$OUTPUT_DIR" --format="$FORMAT"

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