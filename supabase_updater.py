#!/usr/bin/env python3
"""
Módulo para atualizar títulos de anúncios do Airbnb no Supabase.
"""

import os
import sys
import time
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
            
            # Verificar se a tabela logs existe
            self._ensure_logs_table_exists()
        except Exception as e:
            print(f"Erro ao conectar ao Supabase: {str(e)}")
            raise
    
    def _ensure_logs_table_exists(self):
        """
        Verifica se a tabela logs existe e cria se necessário
        """
        try:
            # Verificar se tabela existe consultando por um registro
            self.supabase.table('logs').select('id').limit(1).execute()
        except Exception as e:
            print(f"Tabela 'logs' pode não existir: {str(e)}")
            print("Consulte as instruções para criar a tabela logs no arquivo create_logs_table.sql")
    
    def update_room_label(self, room_id, label):
        """
        Atualiza o título (label) de um quarto no Supabase.
        Se o quarto não existir, ele é inserido.
        Se já existir, é atualizado.
        
        Args:
            room_id: ID do quarto/anúncio do Airbnb
            label: Título do anúncio
        
        Returns:
            dict: Resultado da operação
        """
        if not room_id or not label:
            return {"success": False, "error": "room_id e label são obrigatórios"}
        
        try:
            # Primeiro verificar se o quarto já existe
            exists = self.room_exists(room_id)
            
            if exists:
                print(f"Atualizando quarto existente {room_id} com título: '{label}'")
                # Atualizar quarto existente
                result = self.supabase.table('rooms').update(
                    {"label": label}
                ).eq('room_id', room_id).execute()
                action = "atualizado"
            else:
                print(f"Inserindo novo quarto {room_id} com título: '{label}'")
                # Inserir novo quarto
                result = self.supabase.table('rooms').insert(
                    {"room_id": room_id, "label": label}
                ).execute()
                action = "inserido"
            
            # Verificar se houve erro
            if hasattr(result, 'error') and result.error:
                print(f"Erro ao {action} no Supabase: {result.error}")
                return {"success": False, "error": str(result.error)}
            
            print(f"✅ Quarto {room_id} {action} com sucesso no Supabase (Python)")
            return {"success": True, "action": action}
            
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
            
    def log_execution(self, service_time, rooms_ids, success_count, total_count):
        """
        Registra uma execução do scraper na tabela logs
        
        Args:
            service_time: Tempo de execução em segundos
            rooms_ids: Lista de IDs dos quartos processados
            success_count: Número de quartos processados com sucesso
            total_count: Número total de quartos processados
            
        Returns:
            dict: Resultado da operação
        """
        try:
            print(f"Registrando log de execução no Supabase:")
            print(f"  Tempo de execução: {service_time:.2f} segundos")
            print(f"  Quartos processados: {len(rooms_ids)}")
            print(f"  Taxa de sucesso: {success_count}/{total_count} ({(success_count/total_count*100):.1f}%)")
            
            # Inserir registro no log
            result = self.supabase.table('logs').insert({
                "service_time": service_time,
                "room_ids": rooms_ids,  # Usando room_ids (sem o 's' final)
                "success_count": success_count,
                "total_count": total_count
            }).execute()
            
            # Verificar se houve erro
            if hasattr(result, 'error') and result.error:
                print(f"Erro ao registrar log no Supabase: {result.error}")
                return {"success": False, "error": str(result.error)}
            
            print(f"✅ Log de execução registrado com sucesso no Supabase")
            return {"success": True}
            
        except Exception as e:
            print(f"❌ Falha ao registrar log: {str(e)}")
            return {"success": False, "error": str(e)}

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