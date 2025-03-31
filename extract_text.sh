#!/bin/bash
# Script para extrair texto dos arquivos HTML do Airbnb

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

# Executar o extrator de texto Python
python text_extractor.py --input-dir="$INPUT_DIR" --output-dir="$OUTPUT_DIR" --format="$FORMAT"

# Verificar o resultado
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
  echo ""
  echo "Extração de texto concluída com sucesso!"
  echo "Os arquivos extraídos estão disponíveis em: $OUTPUT_DIR"
  
  # Atualizar Supabase se solicitado
  if [ "$UPDATE_SUPABASE" = true ]; then
    echo ""
    echo "Verificando variáveis de ambiente para Supabase..."
    if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
      echo "⚠️  Aviso: As variáveis de ambiente SUPABASE_URL e/ou SUPABASE_KEY não estão definidas."
      echo "    A atualização do Supabase pode falhar."
    else
      echo "✅ Variáveis de ambiente para Supabase encontradas."
    fi
    
    echo ""
    echo "Iniciando atualização dos títulos no Supabase..."
    UPDATE_COUNT=0
    
    # Processar cada arquivo JSON extraído
    for JSON_FILE in "$OUTPUT_DIR"/*.json; do
      if [ -f "$JSON_FILE" ]; then
        FILENAME=$(basename "$JSON_FILE")
        ROOM_ID=$(echo "$FILENAME" | grep -oP 'airbnb_\K\d+(?=_)' || echo "")
        
        if [ -n "$ROOM_ID" ]; then
          # Extrair o título do arquivo JSON usando jq se disponível, ou grep como fallback
          if command -v jq &> /dev/null; then
            TITLE=$(jq -r '.listing.title // empty' "$JSON_FILE")
          else
            TITLE=$(grep -o '"title": "[^"]*"' "$JSON_FILE" | head -1 | cut -d'"' -f4)
          fi
          
          if [ -n "$TITLE" ]; then
            echo "🔄 Atualizando quarto $ROOM_ID com título: '$TITLE'"
            python supabase_updater.py "$ROOM_ID" "$TITLE"
            if [ $? -eq 0 ]; then
              UPDATE_COUNT=$((UPDATE_COUNT + 1))
            fi
          else
            echo "⚠️  Título não encontrado para o quarto $ROOM_ID"
          fi
        fi
      fi
    done
    
    echo ""
    echo "✅ Atualização do Supabase concluída! $UPDATE_COUNT títulos atualizados."
  fi
else
  echo ""
  echo "Erro durante a extração de texto. Código de saída: $EXIT_CODE"
fi

exit $EXIT_CODE