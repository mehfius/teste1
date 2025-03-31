#!/usr/bin/env python3
"""
Módulo para atualizar títulos de anúncios do Airbnb no Supabase.
"""

import os
import sys
from supabase import create_client

class SupabaseUpdater:
    """
    Classe para gerenciar a conexão e atualizações no Supabase
    """
    
    def __init__(self):
        """
        Inicializa a conexão com o Supabase
        """
        # Verificar se as variáveis de ambiente necessárias estão disponíveis
        self.supabase_url = os.environ.get('SUPABASE_URL')
        self.supabase_key = os.environ.get('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY são necessárias")
        
        # Criar cliente Supabase
        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            print("Cliente Supabase inicializado com sucesso (Python)")
        except Exception as e:
            print(f"Erro ao conectar ao Supabase: {str(e)}")
            raise
    
    def update_room_label(self, room_id, label):
        """
        Atualiza o título (label) de um quarto no Supabase
        
        Args:
            room_id: ID do quarto/anúncio do Airbnb
            label: Título do anúncio
        
        Returns:
            dict: Resultado da operação
        """
        if not room_id or not label:
            return {"success": False, "error": "room_id e label são obrigatórios"}
        
        try:
            print(f"Atualizando quarto {room_id} com título: '{label}'")
            
            # Upsert - inserir se não existir, atualizar se existir
            result = self.supabase.table('rooms').upsert(
                {"room_id": room_id, "label": label}
            ).execute()
            
            # Verificar se houve erro
            if hasattr(result, 'error') and result.error:
                print(f"Erro ao atualizar o Supabase: {result.error}")
                return {"success": False, "error": str(result.error)}
            
            print(f"✅ Quarto {room_id} atualizado com sucesso no Supabase (Python)")
            return {"success": True}
            
        except Exception as e:
            print(f"❌ Falha ao atualizar o quarto {room_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def room_exists(self, room_id):
        """
        Verifica se um quarto existe na tabela rooms
        
        Args:
            room_id: ID do quarto/anúncio do Airbnb
        
        Returns:
            bool: True se o quarto existir
        """
        try:
            result = self.supabase.table('rooms').select('room_id').eq('room_id', room_id).execute()
            
            # Verificar se houve erro
            if hasattr(result, 'error') and result.error:
                print(f"Erro ao verificar quarto: {result.error}")
                return False
            
            # Verificar se há dados
            data = result.data if hasattr(result, 'data') else []
            
            return len(data) > 0
            
        except Exception as e:
            print(f"Falha ao verificar quarto {room_id}: {str(e)}")
            return False

def update_from_commandline():
    """
    Função para atualizar o título a partir da linha de comando
    Uso: python supabase_updater.py ROOM_ID "Título do anúncio"
    """
    if len(sys.argv) < 3:
        print("Uso: python supabase_updater.py ROOM_ID 'Título do anúncio'")
        sys.exit(1)
    
    room_id = sys.argv[1]
    label = sys.argv[2]
    
    try:
        updater = SupabaseUpdater()
        result = updater.update_room_label(room_id, label)
        
        if result.get('success'):
            print(f"Título atualizado com sucesso para o quarto {room_id}")
            sys.exit(0)
        else:
            print(f"Falha ao atualizar o título: {result.get('error', 'Erro desconhecido')}")
            sys.exit(1)
    except Exception as e:
        print(f"Erro ao executar a atualização: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    update_from_commandline()