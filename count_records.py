#!/usr/bin/env python3
"""
Script para contar o número de registros nas tabelas do Supabase
"""

import os
import sys
from supabase import create_client

def count_table_records(table_name):
    """
    Conta o número de registros em uma tabela do Supabase
    
    Args:
        table_name: Nome da tabela
        
    Returns:
        int: Número de registros
    """
    # Verificar variáveis de ambiente
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Erro: As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY são necessárias")
        sys.exit(1)
    
    # Criar cliente Supabase
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Cliente Supabase inicializado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao conectar ao Supabase: {str(e)}")
        sys.exit(1)
    
    # Contar registros
    try:
        # Obter contagem total
        response = supabase.table(table_name).select('*', count='exact').execute()
        
        # Verificar se houve erro
        if hasattr(response, 'error') and response.error:
            print(f"❌ Erro ao consultar tabela {table_name}: {response.error}")
            return 0
        
        # Obter contagem
        count = response.count if hasattr(response, 'count') else len(response.data)
        
        return count
    except Exception as e:
        print(f"❌ Erro ao contar registros: {str(e)}")
        return 0

def main():
    """Função principal"""
    # Verificar se tabela foi especificada
    if len(sys.argv) < 2:
        print("Uso: python count_records.py NOME_DA_TABELA")
        print("Exemplo: python count_records.py rooms")
        sys.exit(1)
    
    table_name = sys.argv[1]
    
    # Contar registros
    count = count_table_records(table_name)
    
    print(f"\n===== ESTATÍSTICAS DA TABELA {table_name.upper()} =====")
    print(f"Total de registros: {count}")
    print("=======================================\n")
    
    # Mostrar alguns registros para verificação
    if count > 0:
        try:
            supabase_url = os.environ.get('SUPABASE_URL')
            supabase_key = os.environ.get('SUPABASE_KEY')
            supabase = create_client(supabase_url, supabase_key)
            
            # Obter os 5 primeiros registros
            response = supabase.table(table_name).select('*').limit(5).execute()
            
            print(f"Primeiros registros da tabela {table_name}:")
            for i, record in enumerate(response.data, 1):
                print(f"{i}. {record}")
        except Exception as e:
            print(f"Erro ao buscar exemplos: {str(e)}")

if __name__ == "__main__":
    main()