# Airbnb HTML Scraper

A Deno application that scrapes and saves HTML content from Airbnb listings.

## Features

- Extract and save HTML content from Airbnb listings
- Accept room_id as a parameter
- Process URLs like https://www.airbnb.com.br/rooms/756587219584104742
- Store the full HTML content
- Simple command line interface
- Error handling with retries
- No browser dependencies (uses fetch API)

## Prerequisites

- [Deno](https://deno.land/) installed
- Internet connection
- Properly configured permissions for network and file system access

## Installation

No installation is needed beyond having Deno installed.

## Usage

You can run the application in two ways:

### 1. Using the Shell Script (Recommended)

```bash
./run_scraper.sh ROOM_ID [OUTPUT_DIR]
```

### 2. Using Deno Directly

```bash
deno run --allow-net --allow-read --allow-write --allow-env main.ts --room-id=ROOM_ID [--output-dir=./output]
```

## Examples

Using the shell script:
```bash
./run_scraper.sh 756587219584104742
```

Using a custom output directory:
```bash
./run_scraper.sh 756587219584104742 ./custom_output
```

Using Deno directly:
```bash
deno run --allow-net --allow-read --allow-write --allow-env main.ts --room-id=756587219584104742
```

This will save the HTML content from the Airbnb listing to the specified output directory (default: ./output).

## How It Works

The application uses the native fetch API to download the HTML content from Airbnb listings. It includes:

- Realistic user-agent headers to mimic a browser
- Retry logic to handle network issues
- Customizable timeout settings
- Automatic creation of the output directory
- Timestamped filenames for easy tracking
