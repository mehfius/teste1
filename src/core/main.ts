import { parse } from "../utils/deps.ts";
import { AirbnbScraper } from "./scraper.ts";
import { formatUrl, validateRoomId, printUsage } from "../utils/utils.ts";
import { SupabaseUpdater } from "../database/supabase_updater.ts";

// Deno já está disponível globalmente, não precisa importar

interface MemoryHTMLContent {
  roomId: string;
  timestamp: string;
  htmlContent: string;
}

// Armazenamento em memória para os dados HTML
const htmlContentStorage: MemoryHTMLContent[] = [];

/**
 * Extrai o título do anúncio do HTML
 */
function extractTitle(html: string): string | undefined {
  const titleMatch = html.match(/<title>([^<]+)<\/title>/);
  if (titleMatch && titleMatch.length > 1) {
    return titleMatch[1].replace(" - Airbnb", "").trim();
  }
  
  // Padrão alternativo para títulos do Airbnb
  const h1Match = html.match(/<h1[^>]*>([^<]+)<\/h1>/);
  if (h1Match && h1Match.length > 1) {
    return h1Match[1].trim();
  }
  
  return undefined;
}

/**
 * Main function to run the Airbnb HTML scraper
 * Versão em memória - não salva arquivos em disco
 */
async function main(): Promise<void> {
  // Parse command line arguments
  const args = parse(Deno.args, {
    string: ["room-id"],
    boolean: ["help", "memory-only", "update-supabase"],
    default: {
      "memory-only": true,
      "update-supabase": true
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

  try {
    // Initialize the scraper
    const scraper = new AirbnbScraper({
      timeout: 60000, // 1 minute timeout
      retries: 3,
      retryDelay: 3000, // 3 seconds between retries
    });

    // Scrape the room HTML
    console.log(`Starting to scrape room ID: ${roomId}`);
    console.log(`Fetching URL: ${formatUrl(roomId)}`);
    const htmlContent = await scraper.scrapeRoom(roomId);

    // Gerar timestamp
    const timestamp = new Date().toISOString().replace(/:/g, "-").replace(/\..+/, "");
    
    // Armazenar o HTML em memória
    htmlContentStorage.push({
      roomId,
      timestamp,
      htmlContent
    });
    
    console.log(`HTML content fetched (length: ${htmlContent.length} characters)`);
    console.log(`File size: ${(htmlContent.length / 1024).toFixed(2)} KB`);
    
    // Atualizar Supabase diretamente sem salvar arquivos
    if (args["update-supabase"]) {
      try {
        const title = extractTitle(htmlContent);
        if (title) {
          console.log(`Extracted title: ${title}`);
          
          // Atualizar o Supabase com o título extraído
          const updater = new SupabaseUpdater();
          const updateResult = await updater.updateRoomLabel(roomId, title);
          
          if (updateResult.success) {
            console.log(`✅ Room ${roomId} successfully updated in Supabase with title: '${title}'`);
          } else {
            console.error(`❌ Failed to update room ${roomId} in Supabase: ${updateResult.error || 'Unknown error'}`);
          }
        } else {
          console.warn(`⚠️ No title extracted for room ${roomId}`);
        }
      } catch (error) {
        console.error(`Error updating Supabase: ${error.message}`);
      }
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    Deno.exit(1);
  }
}

// Run the main function
if (import.meta.main) {
  main();
}
