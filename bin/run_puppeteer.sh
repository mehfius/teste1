#!/bin/bash
# Run Airbnb Puppeteer Scraper with provided room ID
# Example usage: ./run_puppeteer.sh ROOM_ID

# Check if room ID is provided
if [ -z "$1" ]; then
  echo "Error: Room ID is required"
  echo "Usage: ./run_puppeteer.sh ROOM_ID [OUTPUT_DIR]"
  echo "Example: ./run_puppeteer.sh ROOM_ID ./custom_output"
  echo ""
  echo "Use python get_rooms.py para listar os IDs disponíveis na tabela rooms do Supabase."
  exit 1
fi

ROOM_ID=$1
OUTPUT_DIR=${2:-"./output"}
SCREENSHOT_DIR=${3:-"./screenshots"}

# Ensure the output and screenshot directories exist
mkdir -p "$OUTPUT_DIR"
mkdir -p "$SCREENSHOT_DIR"

# No Replit, vamos definir o caminho do Chrome/Chromium se existir
if [ -f "/nix/store/zi4f80l169xlmivz8vja8wlphq74qqk0-chromium-125.0.6422.141/bin/chromium" ]; then
  export PUPPETEER_EXECUTABLE_PATH="/nix/store/zi4f80l169xlmivz8vja8wlphq74qqk0-chromium-125.0.6422.141/bin/chromium"
  echo "Using system Chromium at: $PUPPETEER_EXECUTABLE_PATH"
elif command -v chromium &> /dev/null; then
  export PUPPETEER_EXECUTABLE_PATH=$(which chromium)
  echo "Using system Chromium at: $PUPPETEER_EXECUTABLE_PATH"
else
  echo "No system Chromium found, using Puppeteer's built-in Chromium."
fi

# Run the scraper
echo "Running Airbnb Puppeteer scraper for room ID: $ROOM_ID"
echo "Output directory: $OUTPUT_DIR"
echo "Screenshot directory: $SCREENSHOT_DIR"

# Adicionar mais flags de depuração para ajudar na resolução de problemas
DEBUG_PUPPETEER=true node puppeteer_scraper.js --room-id="$ROOM_ID" --output-dir="$OUTPUT_DIR" --screenshot-dir="$SCREENSHOT_DIR"

exit_code=$?
if [ $exit_code -eq 0 ]; then
  echo "Puppeteer scraper completed successfully!"
else
  echo "Puppeteer scraper failed with exit code: $exit_code"
fi

exit $exit_code