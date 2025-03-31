#!/usr/bin/env python3
"""
Script para obter todos os room_ids da tabela rooms no Supabase.
Uso: python get_rooms.py
"""

import os
import sys
from supabase import create_client

def get_all_room_ids():
    """
    Obtém todos os room_ids da tabela 'rooms' no Supabase.
    
    Returns:
        list: Lista de room_ids encontrados
    """
    # Verificar se as variáveis de ambiente necessárias estão disponíveis
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("Erro: As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY são necessárias", file=sys.stderr)
        sys.exit(1)
    
    # Criar cliente Supabase
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("Cliente Supabase inicializado com sucesso")
    except Exception as e:
        print(f"Erro ao conectar ao Supabase: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Consultar todos os room_ids
        response = supabase.table('rooms').select('room_id').execute()
        
        # Verificar se houve erro
        if hasattr(response, 'error') and response.error:
            print(f"Erro ao consultar o Supabase: {response.error}", file=sys.stderr)
            sys.exit(1)
        
        # Extrair os room_ids
        rooms_data = response.data if hasattr(response, 'data') else []
        room_ids = [str(room['room_id']) for room in rooms_data]
        
        print(f"Encontrados {len(room_ids)} room_ids na tabela 'rooms'")
        return room_ids
        
    except Exception as e:
        print(f"Falha ao buscar room_ids: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    """Função principal"""
    room_ids = get_all_room_ids()
    
    # Imprimir os room_ids, um por linha (para facilitar o processamento com shell scripts)
    for room_id in room_ids:
        print(room_id)

if __name__ == "__main__":
    main()