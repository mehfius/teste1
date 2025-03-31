// Supabase Updater em Deno
// Substitui a funcionalidade do supabase_updater.py

import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.3";

interface UpdateResult {
  success: boolean;
  action?: string;
  error?: string;
  warning?: string;
}

export class SupabaseUpdater {
  private supabase: any;
  private supabaseUrl: string;
  private supabaseKey: string;

  /**
   * Inicializa a conexão com o Supabase
   */
  constructor() {
    // Verificar se as variáveis de ambiente necessárias estão disponíveis
    this.supabaseUrl = Deno.env.get("SUPABASE_URL") || "";
    this.supabaseKey = Deno.env.get("SUPABASE_KEY") || "";

    if (!this.supabaseUrl || !this.supabaseKey) {
      throw new Error("As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY são necessárias");
    }

    // Criar cliente Supabase
    try {
      this.supabase = createClient(this.supabaseUrl, this.supabaseKey);
      console.log("Cliente Supabase inicializado com sucesso (Deno)");

      // Verificar se a tabela logs existe
      this._ensureLogsTableExists();
    } catch (e) {
      console.error(`Erro ao conectar ao Supabase: ${e.message}`);
      throw e;
    }
  }

  /**
   * Verifica se a tabela logs existe
   */
  private async _ensureLogsTableExists(): Promise<boolean> {
    try {
      // Verificar se tabela existe consultando por um registro
      await this.supabase.from('logs').select('id').limit(1);
      return true;
    } catch (e) {
      console.error(`Tabela 'logs' pode não existir: ${e.message}`);
      console.log("Consulte as instruções para criar a tabela logs no arquivo create_logs_table.sql");
      return false;
    }
  }

  /**
   * Obtém todos os room_ids da tabela 'rooms'
   * @returns Array de room_ids
   */
  async getAllRoomIds(): Promise<string[]> {
    try {
      const { data, error } = await this.supabase
        .from('rooms')
        .select('room_id');

      if (error) {
        console.error(`Erro ao consultar room_ids: ${error.message}`);
        return [];
      }

      if (!data || data.length === 0) {
        console.log("Nenhum room_id encontrado na tabela rooms");
        return [];
      }

      return data.map(item => item.room_id.toString());
    } catch (e) {
      console.error(`Erro ao obter room_ids: ${e.message}`);
      return [];
    }
  }

  /**
   * Atualiza o título (label) de um quarto no Supabase.
   * @param roomId ID do quarto/anúncio do Airbnb
   * @param label Título do anúncio
   * @returns Resultado da operação
   */
  async updateRoomLabel(roomId: string, label: string): Promise<UpdateResult> {
    if (!roomId || !label) {
      return { success: false, error: "room_id e label são obrigatórios" };
    }

    try {
      // Primeiro verificar se o quarto já existe
      const exists = await this.roomExists(roomId);

      let result;
      let action;

      if (exists) {
        console.log(`Atualizando quarto existente ${roomId} com título: '${label}'`);
        // Atualizar quarto existente
        result = await this.supabase
          .from('rooms')
          .update({ label })
          .eq('room_id', roomId);
        action = "atualizado";
      } else {
        console.log(`Inserindo novo quarto ${roomId} com título: '${label}'`);
        // Inserir novo quarto
        result = await this.supabase
          .from('rooms')
          .insert({ room_id: roomId, label });
        action = "inserido";
      }

      // Verificar se houve erro
      if (result.error) {
        console.error(`Erro ao ${action} no Supabase: ${result.error.message}`);
        return { success: false, error: result.error.message };
      }

      console.log(`✅ Quarto ${roomId} ${action} com sucesso no Supabase (Deno)`);
      return { success: true, action };
    } catch (e) {
      console.error(`❌ Falha ao atualizar o quarto ${roomId}: ${e.message}`);
      return { success: false, error: e.message };
    }
  }

  /**
   * Verifica se um quarto existe na tabela rooms
   * @param roomId ID do quarto/anúncio do Airbnb
   * @returns True se o quarto existir
   */
  async roomExists(roomId: string): Promise<boolean> {
    try {
      const { data, error } = await this.supabase
        .from('rooms')
        .select('room_id')
        .eq('room_id', roomId);

      if (error) {
        console.error(`Erro ao verificar quarto: ${error.message}`);
        return false;
      }

      return data && data.length > 0;
    } catch (e) {
      console.error(`Falha ao verificar quarto ${roomId}: ${e.message}`);
      return false;
    }
  }

  /**
   * Registra uma execução do scraper na tabela logs
   * @param serviceTime Tempo de execução em segundos
   * @param roomIds Lista de IDs dos quartos processados
   * @param successCount Número de quartos processados com sucesso
   * @param totalCount Número total de quartos processados
   * @returns Resultado da operação
   */
  async logExecution(
    serviceTime: number,
    roomIds: number[],
    successCount: number,
    totalCount: number
  ): Promise<UpdateResult> {
    try {
      console.log(`Registrando log de execução no Supabase:`);
      console.log(`  Tempo de execução: ${serviceTime.toFixed(2)} segundos`);
      console.log(`  Quartos processados: ${roomIds.length}`);
      const successRate = totalCount > 0 ? (successCount / totalCount * 100).toFixed(1) : "0.0";
      console.log(`  Taxa de sucesso: ${successCount}/${totalCount} (${successRate}%)`);

      // Verificar se podemos fazer log (a tabela pode não existir)
      try {
        // Inserir registro no log
        const { error } = await this.supabase
          .from('logs')
          .insert({
            service_time: serviceTime,
            room_ids: roomIds, // Usando room_ids (sem o 's' no final)
            success_count: successCount,
            total_count: totalCount
          });

        if (error) {
          console.error(`Erro ao registrar log no Supabase: ${error.message}`);
          console.log("A tabela 'logs' pode não existir ou ter uma estrutura diferente.");
          console.log("Execute o SQL em create_logs_table.sql para criar a tabela corretamente.");
          // Continuar o script, mesmo com erro no log
          return { success: true, warning: "Erro ao registrar log, mas o processamento foi concluído" };
        }

        console.log(`✅ Log de execução registrado com sucesso no Supabase`);
        return { success: true };
      } catch (logError) {
        console.error(`⚠️ Falha ao registrar log, mas o processamento foi concluído: ${logError.message}`);
        return { success: true, warning: logError.message };
      }
    } catch (e) {
      console.error(`❌ Falha ao registrar log: ${e.message}`);
      // Continuar o script, mesmo com erro no log
      return { success: true, warning: e.message };
    }
  }
}

/**
 * Função para atualizar o título a partir da linha de comando
 * Uso: deno run --allow-net --allow-env supabase_updater.ts ROOM_ID "Título do anúncio"
 */
async function updateFromCommandLine(): Promise<void> {
  const args = Deno.args;
  
  if (args.length < 2) {
    console.log("Uso: deno run --allow-net --allow-env supabase_updater.ts ROOM_ID 'Título do anúncio'");
    Deno.exit(1);
  }

  const roomId = args[0];
  const label = args[1];

  try {
    const updater = new SupabaseUpdater();
    const result = await updater.updateRoomLabel(roomId, label);

    if (result.success) {
      console.log(`Título atualizado com sucesso para o quarto ${roomId}`);
      Deno.exit(0);
    } else {
      console.error(`Falha ao atualizar o título: ${result.error || 'Erro desconhecido'}`);
      Deno.exit(1);
    }
  } catch (e) {
    console.error(`Erro ao executar a atualização: ${e.message}`);
    Deno.exit(1);
  }
}

// Se executado diretamente, chamar a função de atualização
if (import.meta.main) {
  updateFromCommandLine();
}