import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.3";

/**
 * Script para verificar o status da conexão com o Supabase
 * e exibir informações sobre as tabelas rooms e logs.
 */
async function main() {
  console.log("Verificando conexão com o Supabase...");
  
  // Verificar variáveis de ambiente
  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const supabaseKey = Deno.env.get("SUPABASE_KEY");
  
  if (!supabaseUrl || !supabaseKey) {
    console.error("❌ Erro: SUPABASE_URL e SUPABASE_KEY são necessários.");
    console.log("Por favor, defina as variáveis de ambiente SUPABASE_URL e SUPABASE_KEY.");
    Deno.exit(1);
  }
  
  console.log("✅ Variáveis de ambiente encontradas.");
  
  try {
    // Inicializar cliente do Supabase
    const supabase = createClient(supabaseUrl, supabaseKey);
    console.log("✅ Cliente Supabase inicializado.");
    
    // Verificar conexão com a tabela rooms
    console.log("\n📊 Verificando tabela 'rooms'...");
    const { data: rooms, error: roomsError } = await supabase
      .from("rooms")
      .select("room_id, label")
      .limit(10);
    
    if (roomsError) {
      console.error(`❌ Erro ao acessar a tabela 'rooms': ${roomsError.message}`);
      console.log("ℹ️ A tabela 'rooms' deve existir previamente no banco de dados.");
    } else {
      console.log(`✅ Tabela 'rooms' acessada com sucesso.`);
      console.log(`📈 Total de quartos encontrados: ${rooms.length}`);
      
      if (rooms.length > 0) {
        console.log("\n🏠 Primeiros 10 quartos:");
        rooms.forEach((room, index) => {
          console.log(`  ${index + 1}. ID: ${room.room_id}, Título: ${room.label || "(sem título)"}`);
        });
      }
    }
    
    // Verificar conexão com a tabela logs
    console.log("\n📊 Verificando tabela 'logs'...");
    const { data: logs, error: logsError } = await supabase
      .from("logs")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(5);
    
    if (logsError) {
      console.error(`❌ Erro ao acessar a tabela 'logs': ${logsError.message}`);
      console.log("ℹ️ A tabela 'logs' deve existir previamente no banco de dados.");
    } else {
      console.log(`✅ Tabela 'logs' acessada com sucesso.`);
      
      if (logs && logs.length > 0) {
        console.log(`📈 Últimas ${logs.length} execuções registradas:`);
        logs.forEach((log, index) => {
          const date = new Date(log.created_at).toLocaleString();
          console.log(`  ${index + 1}. Data: ${date}`);
          console.log(`     Tempo de execução: ${log.service_time} segundos`);
          console.log(`     Processados: ${log.success_count}/${log.total_count} quartos`);
          console.log(`     IDs: ${log.room_ids.join(", ")}`);
        });
      } else {
        console.log("ℹ️ Nenhum log de execução encontrado.");
      }
    }
    
    console.log("\n✅ Verificação do Supabase concluída!");
    
  } catch (error) {
    console.error(`❌ Erro ao conectar ao Supabase: ${error.message}`);
    Deno.exit(1);
  }
}

// Executar apenas quando chamado diretamente
if (import.meta.main) {
  await main();
}