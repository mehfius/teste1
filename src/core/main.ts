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
/**
 * Extrai o título do anúncio do HTML
 * Melhorado para funcionar com a nova estrutura do Airbnb
 * @param html Conteúdo HTML da página
 * @returns Título extraído ou undefined
 */
function extractTitle(html: string): string | undefined {
  // Estratégia 1: Buscar em meta tags (mais confiável)
  const metaDescriptionMatch = html.match(/<meta name="description" content="([^"]+)"/i);
  if (metaDescriptionMatch && metaDescriptionMatch.length > 1) {
    const description = metaDescriptionMatch[1];
    // As descrições do Airbnb geralmente começam com o título do anúncio
    const parts = description.split(" - ");
    if (parts.length > 1) {
      return parts[0].trim();
    }
    return description.split(".")[0].trim(); // Primeira frase
  }
  
  // Estratégia 2: Meta título original dinâmico (OG tags)
  const ogTitleMatch = html.match(/<meta property="og:title" content="([^"]+)"/i);
  if (ogTitleMatch && ogTitleMatch.length > 1) {
    return ogTitleMatch[1].replace(" - Airbnb", "").trim();
  }
  
  // Estratégia 3: Título da página (menos confiável, título genérico)
  const titleMatch = html.match(/<title>([^<]+)<\/title>/i);
  if (titleMatch && titleMatch.length > 1) {
    const title = titleMatch[1];
    // Verificar se não é o título genérico do Airbnb
    if (!title.startsWith("Airbnb: aluguéis por temporada")) {
      return title.replace(" - Airbnb", "").trim();
    }
  }
  
  // Estratégia 4: H1 da página (tenta encontrar o título principal)
  const h1Match = html.match(/<h1[^>]*>(.*?)<\/h1>/is);
  if (h1Match && h1Match.length > 1) {
    // Remove qualquer tag HTML interna ao h1
    return h1Match[1].replace(/<[^>]*>/g, "").trim();
  }
  
  // Estratégia 5: Buscar a tag específica do Airbnb com o título
  const airbnbTitleMatch = html.match(/<div data-section-id="TITLE_DEFAULT"[^>]*>(.*?)<\/div>/is);
  if (airbnbTitleMatch && airbnbTitleMatch.length > 1) {
    // Remove qualquer tag HTML interna
    return airbnbTitleMatch[1].replace(/<[^>]*>/g, "").trim();
  }
  
  // Estratégia 6: Última tentativa - buscar classe específica do Airbnb
  const specificClassMatch = html.match(/<div class="_1xxgv6q[^>]*>(.*?)<\/div>/is);
  if (specificClassMatch && specificClassMatch.length > 1) {
    return specificClassMatch[1].replace(/<[^>]*>/g, "").trim();
  }
  
  return "Título não encontrado"; // Retorna um valor padrão em vez de undefined
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
        // Adicionar depuração para extração do título
        console.log(`Analisando o HTML para extração de título...`);
            
        // Verificar se o conteúdo contém meta tags
        const hasMeta = htmlContent.includes("<meta name=\"description\"");
        const hasOg = htmlContent.includes("<meta property=\"og:title\"");
        console.log(`HTML contém meta description: ${hasMeta}`);
        console.log(`HTML contém og:title: ${hasOg}`);
        
        // Procurar especificamente trechos importantes do HTML
        const firstChars = htmlContent.substring(0, 500);
        console.log(`Primeiros 500 caracteres: ${firstChars.replace(/[\n\r]+/g, ' ')}`);
            
        // Extrair título
        const title = extractTitle(htmlContent);
        if (title) {
          console.log(`Extracted title: ${title}`);
          
          // Atualizar o Supabase com o título extraído
          const updater = new SupabaseUpdater();
          
          // Verifica se o título é válido (não genérico)
          if (title === "Título não encontrado") {
            console.warn(`⚠️ O título não pôde ser extraído corretamente para o quarto ${roomId}`);
            console.log("Usando título alternativo para não perder o processamento");
            
            // Gerar um título alternativo para não perder o trabalho
            const altTitle = `Quarto Airbnb ${roomId} - Atualizado em ${new Date().toISOString().split('T')[0]}`;
            const updateResult = await updater.updateRoomLabel(roomId, altTitle);
            
            if (updateResult.success) {
              console.log(`✅ Room ${roomId} updated with alternative title: '${altTitle}'`);
            } else {
              console.error(`❌ Failed to update room ${roomId}: ${updateResult.error || 'Unknown error'}`);
            }
          } else {
            // Título normal encontrado
            const updateResult = await updater.updateRoomLabel(roomId, title);
            
            if (updateResult.success) {
              console.log(`✅ Room ${roomId} successfully updated in Supabase with title: '${title}'`);
            } else {
              console.error(`❌ Failed to update room ${roomId}: ${updateResult.error || 'Unknown error'}`);
            }
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
