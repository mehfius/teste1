// Script para obter todos os room_ids da tabela rooms no Supabase.
// Uso: deno run --allow-net --allow-env get_rooms.ts

import { SupabaseUpdater } from "./supabase_updater.ts";

/**
 * Função principal
 */
async function main(): Promise<void> {
  try {
    // Inicializar o atualizador Supabase
    const updater = new SupabaseUpdater();
    
    // Obter todos os room_ids
    console.log("Obtendo room_ids da tabela 'rooms' no Supabase...");
    const roomIds = await updater.getAllRoomIds();
    
    if (roomIds.length === 0) {
      console.log("Nenhum room_id encontrado. A tabela 'rooms' está vazia ou não existe.");
      Deno.exit(1);
    }
    
    console.log(`Encontrados ${roomIds.length} room_ids:`);
    
    // Imprimir cada room_id em uma linha separada para facilitar o processamento por scripts externos
    for (const roomId of roomIds) {
      // Imprimir apenas o ID, sem nenhum texto adicional, para facilitar o processamento em scripts bash
      console.log(roomId);
    }
    
    Deno.exit(0);
  } catch (error) {
    console.error(`Erro ao obter room_ids: ${error.message}`);
    Deno.exit(1);
  }
}

// Executar a função principal
if (import.meta.main) {
  main();
}