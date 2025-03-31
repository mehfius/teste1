import { parse, path, fs } from "./deps.ts";
import { AirbnbScraper } from "./scraper.ts";
import { createFilename, ensureOutputDir, validateRoomId, printUsage } from "./utils.ts";

/**
 * Main function to run the Airbnb HTML scraper
 */
async function main(): Promise<void> {
  // Parse command line arguments
  const args = parse(Deno.args, {
    string: ["room-id", "output-dir"],
    boolean: ["help"],
    default: {
      "output-dir": "./output",
    },
  });

  // Show help if requested
  if (args.help) {
    printUsage();
    Deno.exit(0);
  }

  // Validate the room ID is provided
  const roomId = args["room-id"];
  if (!roomId) {
    console.error("Error: Room ID is required");
    printUsage();
    Deno.exit(1);
  }

  // Validate that the room ID is valid
  if (!validateRoomId(roomId)) {
    console.error("Error: Room ID must be a numeric string");
    Deno.exit(1);
  }

  // Get the output directory
  const outputDir = args["output-dir"];

  try {
    // Ensure the output directory exists
    await ensureOutputDir(outputDir);

    // Initialize the scraper
    const scraper = new AirbnbScraper({
      timeout: 60000, // 1 minute timeout
      retries: 3,
      retryDelay: 3000, // 3 seconds between retries
    });

    // Scrape the room HTML
    console.log(`Starting to scrape HTML for room ID: ${roomId}`);
    const htmlContent = await scraper.scrapeRoom(roomId);

    // Create a filename with timestamp
    const filename = createFilename(roomId);
    const filePath = path.join(outputDir, filename);

    // Save the HTML content to a file
    await Deno.writeTextFile(filePath, htmlContent);
    
    console.log(`HTML content saved to: ${filePath}`);
    console.log(`File size: ${(htmlContent.length / 1024).toFixed(2)} KB`);
    
  } catch (error) {
    console.error(`Error: ${error.message}`);
    Deno.exit(1);
  }
}

// Run the main function
if (import.meta.main) {
  main();
}
