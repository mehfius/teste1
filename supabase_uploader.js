const { createClient } = require('@supabase/supabase-js');

/**
 * Classe para gerenciar uploads para o Supabase
 * Esta classe se conecta ao Supabase e atualiza a tabela "rooms"
 * com o título (label) extraído dos anúncios do Airbnb
 */
class SupabaseUploader {
  /**
   * Construtor
   */
  constructor() {
    // Verificar se as variáveis de ambiente necessárias estão definidas
    if (!process.env.SUPABASE_URL || !process.env.SUPABASE_KEY) {
      throw new Error('As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY são obrigatórias.');
    }

    // Criar cliente Supabase
    this.supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_KEY
    );

    console.log('Cliente Supabase inicializado com sucesso.');
  }

  /**
   * Atualiza a tabela "rooms" no Supabase com o título do anúncio
   * 
   * @param {string} roomId - ID do quarto/anúncio do Airbnb
   * @param {string} label - Título do anúncio extraído
   * @returns {Promise<Object>} - Resultado da operação
   */
  async updateRoomLabel(roomId, label) {
    if (!roomId || !label) {
      throw new Error('roomId e label são obrigatórios para a atualização.');
    }

    try {
      console.log(`Atualizando quarto ${roomId} com título: "${label}"`);
      
      // Realizar o upsert (inserir se não existir, atualizar se existir)
      const { data, error } = await this.supabase
        .from('rooms')
        .upsert(
          { room_id: roomId, label: label },
          { onConflict: 'room_id', returning: 'minimal' }
        );

      if (error) {
        console.error('Erro ao atualizar o Supabase:', error);
        throw error;
      }

      console.log(`Quarto ${roomId} atualizado com sucesso no Supabase.`);
      return { success: true, roomId, label };
    } catch (error) {
      console.error(`Falha ao atualizar o quarto ${roomId}:`, error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Verifica se um quarto/anúncio já existe na tabela
   * 
   * @param {string} roomId - ID do quarto/anúncio do Airbnb
   * @returns {Promise<boolean>} - true se o quarto existir
   */
  async roomExists(roomId) {
    try {
      const { data, error } = await this.supabase
        .from('rooms')
        .select('room_id')
        .eq('room_id', roomId)
        .single();

      if (error && error.code !== 'PGRST116') {
        console.error('Erro ao verificar quarto:', error);
        throw error;
      }

      return !!data;
    } catch (error) {
      console.error(`Falha ao verificar quarto ${roomId}:`, error.message);
      return false;
    }
  }
}

module.exports = { SupabaseUploader };