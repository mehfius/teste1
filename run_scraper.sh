#!/bin/bash
# Run Airbnb Scraper with provided room ID
# Example usage: ./run_scraper.sh ROOM_ID
# Example with scraper selection: ./run_scraper.sh ROOM_ID ./output puppeteer
# Example with text extraction: ./run_scraper.sh ROOM_ID ./output puppeteer extract
# Example with Supabase update: ./run_scraper.sh ROOM_ID ./output puppeteer extract-supabase

# Check if room ID is provided
if [ -z "$1" ]; then
  echo "Error: Room ID is required"
  echo "Usage: ./run_scraper.sh ROOM_ID [OUTPUT_DIR] [SCRAPER_TYPE] [ACTION]"
  echo "Example: ./run_scraper.sh ROOM_ID ./custom_output"
  echo "Example with scraper selection: ./run_scraper.sh ROOM_ID ./output puppeteer"
  echo "Example with text extraction: ./run_scraper.sh ROOM_ID ./output puppeteer extract"
  echo "Example with Supabase update: ./run_scraper.sh ROOM_ID ./output puppeteer extract-supabase"
  echo ""
  echo "Use python get_rooms.py para listar os IDs disponíveis na tabela rooms do Supabase."
  exit 1
fi

ROOM_ID=$1
OUTPUT_DIR=${2:-"./output"}
SCRAPER_TYPE=${3:-"puppeteer"} # Default to puppeteer, alternatives: "deno"
ACTION=${4:-"scrape"} # scrape, extract, extract-supabase

# Se for usar o puppeteer, chama o script correspondente
if [ "$SCRAPER_TYPE" = "puppeteer" ]; then
  echo "Using Puppeteer-based scraper"
  
  # Verificar se o Node.js está instalado
  if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. The Puppeteer-based scraper requires Node.js."
    exit 1
  fi
  
  # Executar o scraper Puppeteer
  echo "Running Airbnb scraper (Puppeteer) for room ID: $ROOM_ID"
  ./run_puppeteer.sh "$ROOM_ID" "$OUTPUT_DIR" "./screenshots"
  
  exit_code=$?
  if [ $exit_code -eq 0 ]; then
    echo "Puppeteer scraper completed successfully!"
    
    # Se solicitado, executar extração de texto
    if [[ "$ACTION" == "extract" || "$ACTION" == "extract-supabase" ]]; then
      echo ""
      echo "==============================================="
      echo "Iniciando extração de texto..."
      
      # Determinar se deve atualizar o Supabase
      if [ "$ACTION" == "extract-supabase" ]; then
        ./extract_text.sh --input-dir="$OUTPUT_DIR" --format=both --update-supabase
      else
        ./extract_text.sh --input-dir="$OUTPUT_DIR" --format=both
      fi
      
      extract_exit_code=$?
      if [ $extract_exit_code -eq 0 ]; then
        echo "Processo completo: Scraping e extração de texto concluídos com sucesso!"
      else
        echo "Scraping concluído, mas a extração de texto falhou com código: $extract_exit_code"
        exit_code=$extract_exit_code
      fi
    fi
  else
    echo "Puppeteer scraper failed with exit code: $exit_code"
  fi
  
  exit $exit_code
fi

# Se chegou aqui, é para usar o scraper baseado em Deno
echo "Using Deno-based scraper"

# Try to use the system Deno installation first
if command -v deno &> /dev/null; then
  DENO_CMD="deno"
elif [ -f "/home/runner/.deno/bin/deno" ]; then
  DENO_CMD="/home/runner/.deno/bin/deno"
  export PATH="/home/runner/.deno/bin:$PATH"
else
  echo "Deno not found. Installing..."
  curl -fsSL https://deno.land/x/install/install.sh > install_deno.sh
  DENO_INSTALL=/home/runner/.deno sh install_deno.sh v1.40.1
  rm install_deno.sh
  
  if [ -f "/home/runner/.deno/bin/deno" ]; then
    DENO_CMD="/home/runner/.deno/bin/deno"
    export PATH="/home/runner/.deno/bin:$PATH"
  else
    echo "Failed to install Deno. Exiting."
    exit 1
  fi
fi

# Run the Deno scraper
echo "Running Airbnb scraper (Deno) for room ID: $ROOM_ID"
echo "Output directory: $OUTPUT_DIR"
echo "Using Deno at: $DENO_CMD"

"$DENO_CMD" run --allow-net --allow-read --allow-write --allow-env main.ts --room-id=$ROOM_ID --output-dir=$OUTPUT_DIR

exit_code=$?
if [ $exit_code -eq 0 ]; then
  echo "Deno scraper completed successfully!"
  
  # Se solicitado, executar extração de texto
  if [[ "$ACTION" == "extract" || "$ACTION" == "extract-supabase" ]]; then
    echo ""
    echo "==============================================="
    echo "Iniciando extração de texto..."
    
    # Determinar se deve atualizar o Supabase
    if [ "$ACTION" == "extract-supabase" ]; then
      ./extract_text.sh --input-dir="$OUTPUT_DIR" --format=both --update-supabase
    else
      ./extract_text.sh --input-dir="$OUTPUT_DIR" --format=both
    fi
    
    extract_exit_code=$?
    if [ $extract_exit_code -eq 0 ]; then
      echo "Processo completo: Scraping e extração de texto concluídos com sucesso!"
    else
      echo "Scraping concluído, mas a extração de texto falhou com código: $extract_exit_code"
      exit_code=$extract_exit_code
    fi
  fi
else
  echo "Deno scraper failed with exit code: $exit_code"
fi

exit $exit_code