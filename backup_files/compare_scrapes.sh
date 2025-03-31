#!/bin/bash
# Script para comparar diferentes scrapes do Airbnb e detectar mudanças
# Uso: ./compare_scrapes.sh [--room-id=ID] [--format=FORMAT]

# Diretórios padrão
EXTRACTED_DIR="./extracted"
OUTPUT_DIR="./comparison_reports"
REPORT_FORMAT="html"  # Por padrão, usar html para melhor visualização
ROOM_ID=""

# Processar parâmetros
while [ "$1" != "" ]; do
  case $1 in
    --room-id=*)
      ROOM_ID="${1#*=}"
      ;;
    --format=*)
      REPORT_FORMAT="${1#*=}"
      ;;
    --extracted-dir=*)
      EXTRACTED_DIR="${1#*=}"
      ;;
    --output-dir=*)
      OUTPUT_DIR="${1#*=}"
      ;;
    --help)
      echo "Uso: $0 [--room-id=ID] [--format=FORMAT] [--extracted-dir=DIR] [--output-dir=DIR]"
      echo "Compara diferentes versões de scraping do Airbnb e gera relatório de alterações."
      echo ""
      echo "Opções:"
      echo "  --room-id=ID        ID específico de um quarto para comparar (opcional)"
      echo "  --format=FORMAT     Formato do relatório: json, txt, html (padrão: html)"
      echo "  --extracted-dir=DIR Diretório com arquivos extraídos (padrão: ./extracted)"
      echo "  --output-dir=DIR    Diretório para salvar relatórios (padrão: ./comparison_reports)"
      echo "  --help              Mostra esta ajuda"
      echo ""
      echo "Para listar os IDs de quartos disponíveis, execute: python get_rooms.py"
      exit 0
      ;;
    *)
      echo "Opção desconhecida: $1"
      echo "Use --help para ver as opções disponíveis."
      exit 1
      ;;
  esac
  shift
done

# Verificar se o script de comparação existe
if [ ! -f "./compare_scrapes.py" ]; then
  echo "Erro: Script de comparação (compare_scrapes.py) não encontrado."
  exit 1
fi

# Verificar se o diretório extracted existe
if [ ! -d "$EXTRACTED_DIR" ]; then
  echo "Erro: Diretório de arquivos extraídos ($EXTRACTED_DIR) não encontrado."
  exit 1
fi

# Verificar se há arquivos para comparar
JSON_COUNT=$(find "$EXTRACTED_DIR" -name "airbnb_*.json" | wc -l)
if [ "$JSON_COUNT" -lt 2 ]; then
  echo "Erro: Não há arquivos JSON suficientes para comparação no diretório $EXTRACTED_DIR."
  echo "Mínimo 2 arquivos necessários para o mesmo room_id."
  exit 1
fi

# Criar diretório de saída se não existir
mkdir -p "$OUTPUT_DIR"

# Montar o comando com os parâmetros corretos
CMD="python compare_scrapes.py --extracted-dir=\"$EXTRACTED_DIR\" --output-dir=\"$OUTPUT_DIR\" --report-format=\"$REPORT_FORMAT\""

if [ -n "$ROOM_ID" ]; then
  echo "Comparando scrapes para o room_id: $ROOM_ID"
  CMD="$CMD --room-id=\"$ROOM_ID\""
else
  echo "Comparando scrapes para todos os room_ids disponíveis"
fi

echo "Executando: $CMD"
eval $CMD

EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
  echo "Comparação concluída com sucesso!"
  
  # Abrir o relatório automaticamente se for HTML
  if [ "$REPORT_FORMAT" = "html" ]; then
    LATEST_REPORT=$(find "$OUTPUT_DIR" -name "comparison*.$REPORT_FORMAT" -type f -printf "%T@ %p\n" | sort -n | tail -1 | cut -f2- -d" ")
    if [ -n "$LATEST_REPORT" ]; then
      echo ""
      echo "Relatório HTML gerado em: $LATEST_REPORT"
      
      # Tentativa de abrir o navegador automaticamente (funciona em alguns ambientes)
      if command -v xdg-open &> /dev/null; then
        echo "Tentando abrir o relatório no navegador..."
        xdg-open "$LATEST_REPORT" &
      elif command -v open &> /dev/null; then
        echo "Tentando abrir o relatório no navegador..."
        open "$LATEST_REPORT" &
      else
        echo "Abra o relatório manualmente em seu navegador."
      fi
    fi
  else
    echo "Verifique o diretório $OUTPUT_DIR para o relatório gerado."
  fi
else
  echo "Falha na comparação de scrapes com código de saída: $EXIT_CODE"
  exit $EXIT_CODE
fi