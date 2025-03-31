import { ensureDir, path } from "./deps.ts";

/**
 * Creates a formatted filename based on room ID and timestamp
 * @param roomId The Airbnb room ID
 * @returns A string representing the filename for the saved HTML
 */
export function createFilename(roomId: string): string {
  const now = new Date();
  const timestamp = now.toISOString().replace(/:/g, "-").replace(/\..+/, "");
  return `airbnb_${roomId}_${timestamp}.html`;
}

/**
 * Ensures that the output directory exists
 * @param outputDir The directory to ensure exists
 */
export async function ensureOutputDir(outputDir: string): Promise<void> {
  try {
    await ensureDir(outputDir);
  } catch (error) {
    throw new Error(`Failed to create output directory: ${error.message}`);
  }
}

/**
 * Formats a room ID into a full Airbnb URL
 * @param roomId The Airbnb room ID
 * @returns A formatted URL for the room
 */
export function formatUrl(roomId: string): string {
  return `https://www.airbnb.com.br/rooms/${roomId}`;
}

/**
 * Validates that the room ID is a string of numeric characters
 * @param roomId The room ID to validate
 * @returns True if valid, false otherwise
 */
export function validateRoomId(roomId: string): boolean {
  return /^\d+$/.test(roomId);
}

/**
 * Prints usage information for the script
 */
export function printUsage(): void {
  console.log("Usage: deno run --allow-net --allow-read --allow-write main.ts --room-id=ROOM_ID [--output-dir=./output]");
  console.log("\nOptions:");
  console.log("  --room-id     The Airbnb room ID (required)");
  console.log("  --output-dir  Directory to store HTML files (default: ./output)");
  console.log("  --help        Show this help message");
  console.log("\nExample:");
  console.log("  deno run --allow-net --allow-read --allow-write main.ts --room-id=756587219584104742");
}
