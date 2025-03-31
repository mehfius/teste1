// Airbnb Text Extractor em Deno
// Substituição para o text_extractor.py

import { parse } from "https://deno.land/std@0.192.0/flags/mod.ts";
import * as path from "https://deno.land/std@0.192.0/path/mod.ts";
import { ensureDir } from "https://deno.land/std@0.192.0/fs/ensure_dir.ts";
import { SupabaseUpdater } from "./supabase_updater.ts";

interface ExtractionResult {
  roomId: string;
  timestamp: string;
  content: string;
  metadata: {
    title?: string;
    price?: string;
    rating?: string;
    reviews?: string;
    location?: string;
    features?: {
      rooms?: string;
      bathrooms?: string;
      guests?: string;
    };
    originalFilename?: string;
  };
}

/**
 * Classe para extrair e organizar o conteúdo textual de páginas HTML do Airbnb.
 */
class AirbnbTextExtractor {
  /**
   * Inicializa o extrator.
   */
  constructor() {
    console.log("Inicializando extrator de texto do Airbnb em Deno");
  }

  /**
   * Extrai o conteúdo textual de um arquivo HTML do Airbnb.
   * @param htmlFilePath Caminho para o arquivo HTML
   * @returns Objeto com o conteúdo extraído e metadados
   */
  async extractFromFile(htmlFilePath: string): Promise<ExtractionResult | null> {
    try {
      console.log(`Processando: ${htmlFilePath}`);
      
      // Ler o arquivo HTML
      const htmlContent = await Deno.readTextFile(htmlFilePath);
      if (!htmlContent || htmlContent.trim().length === 0) {
        console.error(`Arquivo vazio ou inválido: ${htmlFilePath}`);
        return null;
      }
      
      // Obter o nome do arquivo
      const filename = path.basename(htmlFilePath);
      
      // Extrair ID do quarto e timestamp do nome do arquivo
      const { roomId, timestamp } = this._extractInfoFromFilename(filename);
      if (!roomId) {
        console.error(`Não foi possível extrair o ID do quarto do nome do arquivo: ${filename}`);
        return null;
      }
      
      console.log(`Extraindo dados para o quarto ID: ${roomId}, timestamp: ${timestamp}`);

      // Extrair o conteúdo relevante do HTML usando expressões regulares básicas
      // Nota: Isto é uma simplificação, idealmente usaríamos um parser HTML completo
      const title = this._extractTitle(htmlContent);
      const price = this._extractPrice(htmlContent);
      const { rating, reviews } = this._extractReviews(htmlContent);
      const location = this._extractLocation(htmlContent);
      const features = this._extractFeatures(htmlContent);
      
      // Criar o objeto de resultado
      const result: ExtractionResult = {
        roomId,
        timestamp,
        content: this._extractMainContent(htmlContent),
        metadata: {
          title,
          price,
          rating,
          reviews,
          location,
          features,
          originalFilename: filename
        }
      };
      
      console.log(`✅ Extração concluída para o quarto ${roomId}`);
      if (title) console.log(`   Título: ${title}`);
      if (price) console.log(`   Preço: ${price}`);
      
      return result;
    } catch (error) {
      console.error(`Erro ao processar o arquivo ${htmlFilePath}: ${error.message}`);
      return null;
    }
  }

  /**
   * Processa todos os arquivos HTML em um diretório.
   * @param inputDir Diretório com arquivos HTML
   * @param outputDir Diretório para salvar os arquivos de saída
   * @param format Formato de saída ('json', 'text', 'both')
   * @param updateSupabase Se deve atualizar os títulos no Supabase
   * @returns Número de arquivos processados com sucesso
   */
  async processDirectory(
    inputDir: string, 
    outputDir: string, 
    format: string = "both",
    updateSupabase: boolean = false
  ): Promise<number> {
    try {
      // Garantir que o diretório de saída existe
      await ensureDir(outputDir);
      
      // Listar todos os arquivos HTML no diretório de entrada
      const files = [];
      for await (const entry of Deno.readDir(inputDir)) {
        if (entry.isFile && entry.name.endsWith(".html")) {
          files.push(entry.name);
        }
      }
      
      if (files.length === 0) {
        console.log(`Nenhum arquivo HTML encontrado em ${inputDir}`);
        return 0;
      }
      
      console.log(`Encontrados ${files.length} arquivos HTML para processar`);
      
      // Inicializar o atualizador Supabase se necessário
      let updater: SupabaseUpdater | null = null;
      if (updateSupabase) {
        try {
          updater = new SupabaseUpdater();
          console.log("Cliente Supabase inicializado para atualizações de títulos");
        } catch (error) {
          console.error(`Erro ao inicializar cliente Supabase: ${error.message}`);
          console.log("Continuando sem atualizar o Supabase");
        }
      }
      
      // Processar cada arquivo
      let successCount = 0;
      
      for (const filename of files) {
        const filePath = path.join(inputDir, filename);
        const result = await this.extractFromFile(filePath);
        
        if (result) {
          // Salvar o resultado no formato especificado
          if (format === "json" || format === "both") {
            const jsonPath = path.join(outputDir, `airbnb_${result.roomId}_${result.timestamp}.json`);
            await Deno.writeTextFile(jsonPath, JSON.stringify(result, null, 2));
            console.log(`JSON salvo: ${jsonPath}`);
          }
          
          if (format === "text" || format === "both") {
            const textPath = path.join(outputDir, `airbnb_${result.roomId}_${result.timestamp}.txt`);
            await Deno.writeTextFile(textPath, result.content);
            console.log(`Texto salvo: ${textPath}`);
          }
          
          // Atualizar o Supabase se necessário
          if (updateSupabase && updater && result.metadata.title) {
            try {
              const updateResult = await updater.updateRoomLabel(result.roomId, result.metadata.title);
              console.log(`Supabase ${updateResult.success ? 'atualizado' : 'falhou'} para o quarto ${result.roomId}`);
            } catch (error) {
              console.error(`Erro ao atualizar Supabase para quarto ${result.roomId}: ${error.message}`);
            }
          }
          
          successCount++;
        }
      }
      
      console.log(`✅ Processamento concluído. ${successCount} de ${files.length} arquivos processados com sucesso.`);
      return successCount;
    } catch (error) {
      console.error(`Erro ao processar diretório: ${error.message}`);
      return 0;
    }
  }

  /**
   * Extrai o conteúdo principal do HTML
   * @param html Conteúdo HTML
   * @returns Texto extraído
   */
  private _extractMainContent(html: string): string {
    // Remover tags de script e style
    let content = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, ' ');
    content = content.replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, ' ');
    
    // Remover todas as tags HTML mantendo o texto
    content = content.replace(/<[^>]+>/g, ' ');
    
    // Normalizar espaços em branco
    content = content.replace(/\s+/g, ' ').trim();
    
    // Nota: isso é uma simplificação básica. Uma versão mais avançada
    // faria uma análise semântica para extrair apenas as partes importantes.
    
    return content;
  }

  /**
   * Extrai informações do nome do arquivo
   * @param filename Nome do arquivo
   * @returns Objeto com roomId e timestamp
   */
  private _extractInfoFromFilename(filename: string): { roomId: string; timestamp: string } {
    // Formato esperado: airbnb_ROOMID_TIMESTAMP.html
    const match = filename.match(/airbnb_(\d+)_(.+)\.html$/);
    
    if (match && match.length >= 3) {
      return {
        roomId: match[1],
        timestamp: match[2]
      };
    }
    
    return { roomId: "", timestamp: "" };
  }

  /**
   * Extrai o título do anúncio
   * @param html Conteúdo HTML
   * @returns Título extraído ou undefined
   */
  private _extractTitle(html: string): string | undefined {
    // Primeira tentativa: meta tag de título
    const metaTitleMatch = html.match(/<meta\s+property="og:title"\s+content="([^"]+)"/i);
    if (metaTitleMatch && metaTitleMatch[1]) {
      return metaTitleMatch[1].trim();
    }
    
    // Segunda tentativa: tag h1
    const h1Match = html.match(/<h1[^>]*>([^<]+)<\/h1>/i);
    if (h1Match && h1Match[1]) {
      return h1Match[1].trim();
    }
    
    // Terceira tentativa: padrão de dados JSON embutido
    const jsonMatch = html.match(/"title":"([^"]+)"/);
    if (jsonMatch && jsonMatch[1]) {
      return jsonMatch[1].trim();
    }
    
    return undefined;
  }

  /**
   * Extrai o preço do anúncio
   * @param html Conteúdo HTML
   * @returns Preço extraído ou undefined
   */
  private _extractPrice(html: string): string | undefined {
    // Buscar por padrões comuns de preço no HTML
    const priceMatch = html.match(/"priceString":"([^"]+)"/);
    if (priceMatch && priceMatch[1]) {
      return priceMatch[1].trim();
    }
    
    // Alternativas
    const altPriceMatch = html.match(/R\$\s*[\d.]+/);
    if (altPriceMatch) {
      return altPriceMatch[0].trim();
    }
    
    return undefined;
  }

  /**
   * Extrai a avaliação e quantidade de reviews
   * @param html Conteúdo HTML
   * @returns Objeto com rating e reviews
   */
  private _extractReviews(html: string): { rating?: string; reviews?: string } {
    const result: { rating?: string; reviews?: string } = {};
    
    // Buscar avaliação
    const ratingMatch = html.match(/"starRating":([0-9.]+)/);
    if (ratingMatch && ratingMatch[1]) {
      result.rating = ratingMatch[1].trim();
    }
    
    // Buscar número de reviews
    const reviewsMatch = html.match(/"reviewCount":([0-9]+)/);
    if (reviewsMatch && reviewsMatch[1]) {
      result.reviews = reviewsMatch[1].trim();
    }
    
    return result;
  }

  /**
   * Extrai a localização do anúncio
   * @param html Conteúdo HTML
   * @returns Localização extraída ou undefined
   */
  private _extractLocation(html: string): string | undefined {
    // Buscar localização na meta tag
    const locationMatch = html.match(/<meta\s+property="og:location"\s+content="([^"]+)"/i);
    if (locationMatch && locationMatch[1]) {
      return locationMatch[1].trim();
    }
    
    // Alternativa: buscar no JSON embutido
    const jsonLocationMatch = html.match(/"location":\s*{[^}]*"city":"([^"]+)"/);
    if (jsonLocationMatch && jsonLocationMatch[1]) {
      return jsonLocationMatch[1].trim();
    }
    
    return undefined;
  }

  /**
   * Extrai características do imóvel (quartos, banheiros, etc.)
   * @param html Conteúdo HTML
   * @returns Objeto com características
   */
  private _extractFeatures(html: string): { rooms?: string; bathrooms?: string; guests?: string } {
    const features: { rooms?: string; bathrooms?: string; guests?: string } = {};
    
    // Quartos
    const roomsMatch = html.match(/"bedrooms":([0-9]+)/);
    if (roomsMatch && roomsMatch[1]) {
      features.rooms = roomsMatch[1].trim();
    }
    
    // Banheiros
    const bathroomsMatch = html.match(/"bathrooms":([0-9.]+)/);
    if (bathroomsMatch && bathroomsMatch[1]) {
      features.bathrooms = bathroomsMatch[1].trim();
    }
    
    // Hóspedes
    const guestsMatch = html.match(/"personCapacity":([0-9]+)/);
    if (guestsMatch && guestsMatch[1]) {
      features.guests = guestsMatch[1].trim();
    }
    
    return features;
  }
}

/**
 * Função principal do programa
 */
async function main(): Promise<void> {
  // Analisar argumentos da linha de comando
  const args = parse(Deno.args, {
    string: ["input-dir", "output-dir", "format", "input"],
    boolean: ["help", "update-supabase"],
    default: {
      "input-dir": "./output",
      "output-dir": "./extracted",
      "format": "both",
      "update-supabase": false
    }
  });

  // Mostrar ajuda se solicitado
  if (args.help) {
    console.log("Uso: deno run --allow-read --allow-write --allow-env text_extractor.ts [OPÇÕES]");
    console.log("");
    console.log("Opções:");
    console.log("  --input-dir=DIR       Diretório com arquivos HTML (padrão: ./output)");
    console.log("  --output-dir=DIR      Diretório para salvar os resultados (padrão: ./extracted)");
    console.log("  --format=FORMAT       Formato de saída: json, text, both (padrão: both)");
    console.log("  --update-supabase     Atualiza títulos extraídos no Supabase");
    console.log("  --help                Mostra esta ajuda");
    Deno.exit(0);
  }

  // Verificar entrada
  const inputDir = args["input-dir"];
  const outputDir = args["output-dir"];
  const format = args["format"];
  const updateSupabase = args["update-supabase"];

  try {
    console.log(`Iniciando extração de texto do Airbnb (Deno)`);
    console.log(`Diretório de entrada: ${inputDir}`);
    console.log(`Diretório de saída: ${outputDir}`);
    console.log(`Formato: ${format}`);
    console.log(`Atualizar Supabase: ${updateSupabase ? "Sim" : "Não"}`);
    console.log("");

    // Verificar se o diretório de entrada existe
    try {
      const stat = await Deno.stat(inputDir);
      if (!stat.isDirectory) {
        console.error(`Erro: ${inputDir} não é um diretório.`);
        Deno.exit(1);
      }
    } catch (error) {
      console.error(`Erro: Diretório de entrada '${inputDir}' não existe.`);
      Deno.exit(1);
    }

    // Inicializar o extrator e processar o diretório
    const extractor = new AirbnbTextExtractor();
    const processedCount = await extractor.processDirectory(
      inputDir,
      outputDir,
      format,
      updateSupabase
    );

    if (processedCount > 0) {
      console.log(`✅ Extração concluída! ${processedCount} arquivos processados.`);
      Deno.exit(0);
    } else {
      console.error("❌ Nenhum arquivo foi processado com sucesso.");
      Deno.exit(1);
    }
  } catch (error) {
    console.error(`Erro durante a execução: ${error.message}`);
    Deno.exit(1);
  }
}

// Executar a função principal se este arquivo for chamado diretamente
if (import.meta.main) {
  main();
}