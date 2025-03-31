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
   * Atualiza a tabela "rooms" no Supabase com o título do anúncio.
   * Se o quarto não existir, ele é inserido.
   * Se já existir, é atualizado.
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
      // Primeiro verificar se o quarto já existe
      const exists = await this.roomExists(roomId);
      let result;
      let action;
      
      if (exists) {
        console.log(`Atualizando quarto existente ${roomId} com título: "${label}"`);
        // Atualizar quarto existente
        result = await this.supabase
          .from('rooms')
          .update({ label: label })
          .eq('room_id', roomId);
        action = "atualizado";
      } else {
        console.log(`Inserindo novo quarto ${roomId} com título: "${label}"`);
        // Inserir novo quarto
        result = await this.supabase
          .from('rooms')
          .insert({ room_id: roomId, label: label });
        action = "inserido";
      }

      const { error } = result;
      if (error) {
        console.error(`Erro ao ${action} no Supabase:`, error);
        throw error;
      }

      console.log(`Quarto ${roomId} ${action} com sucesso no Supabase.`);
      return { success: true, roomId, label, action };
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