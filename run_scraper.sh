#!/bin/bash
# Run Airbnb Scraper with provided room ID
# Example usage: ./run_scraper.sh 756587219584104742

# Check if room ID is provided
if [ -z "$1" ]; then
  echo "Error: Room ID is required"
  echo "Usage: ./run_scraper.sh ROOM_ID [OUTPUT_DIR]"
  echo "Example: ./run_scraper.sh 756587219584104742 ./custom_output"
  exit 1
fi

ROOM_ID=$1
OUTPUT_DIR=${2:-"./output"}

# Export Deno to path
export PATH="/home/runner/.deno/bin:$PATH"

# Run the scraper
echo "Running Airbnb scraper for room ID: $ROOM_ID"
echo "Output directory: $OUTPUT_DIR"

deno run --allow-net --allow-read --allow-write --allow-env main.ts --room-id=$ROOM_ID --output-dir=$OUTPUT_DIR

exit_code=$?
if [ $exit_code -eq 0 ]; then
  echo "Scraper completed successfully!"
else
  echo "Scraper failed with exit code: $exit_code"
fi

exit $exit_code