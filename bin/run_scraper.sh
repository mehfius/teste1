#!/bin/bash
# Run Airbnb Scraper with provided room ID
# Versão atualizada: Processamento em memória, sem criar arquivos
# Example usage: ./run_scraper.sh ROOM_ID

# Check if room ID is provided
if [ -z "$1" ]; then
  echo "Error: Room ID is required"
  echo "Usage: ./run_scraper.sh ROOM_ID [SCRAPER_TYPE] [ACTION]"
  echo "Example: ./run_scraper.sh ROOM_ID"
  echo "Example with scraper selection (força Deno): ./run_scraper.sh ROOM_ID deno"
  echo ""
  echo "Use 'deno run --allow-net --allow-env src/database/get_rooms.ts' para listar os IDs disponíveis na tabela rooms do Supabase."
  exit 1
fi

ROOM_ID=$1
SCRAPER_TYPE=${2:-"deno"}  # Default to deno, sempre use Deno agora
ACTION=${3:-"memory"}      # Sempre processar em memória

# Verifica Deno 
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

# Executa o scraper Deno no modo memória 
echo "Running Airbnb scraper (Deno) for room ID: $ROOM_ID"
echo "Using Deno at: $DENO_CMD"

# Executa o main.ts com a opção de processar em memória e atualizar o Supabase
"$DENO_CMD" run --allow-net --allow-env src/core/main.ts --room-id=$ROOM_ID --memory-only --update-supabase

exit_code=$?
if [ $exit_code -eq 0 ]; then
  echo "Deno scraper completed successfully!"
else
  echo "Deno scraper failed with exit code: $exit_code"
fi

exit $exit_code