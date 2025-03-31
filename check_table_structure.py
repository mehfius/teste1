#!/usr/bin/env python3
"""
Script para verificar a estrutura de uma tabela no Supabase
"""

import os
import sys
from supabase import create_client

def check_table_structure(table_name):
    """
    Verifica a estrutura de uma tabela no Supabase
    
    Args:
        table_name: Nome da tabela
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
    
    # Como não podemos obter metadados diretamente, vamos tentar inferir a estrutura
    # consultando um registro
    try:
        # Buscar um registro
        print(f"Consultando um registro da tabela {table_name}...")
        response = supabase.table(table_name).select('*').limit(1).execute()
        
        # Verificar se houve erro
        if hasattr(response, 'error') and response.error:
            print(f"❌ Erro ao consultar tabela {table_name}: {response.error}")
            return
        
        # Se não há dados, não podemos inferir a estrutura
        if not response.data:
            print(f"⚠️ A tabela {table_name} está vazia, não é possível inferir a estrutura")
            
            # Como não temos dados, vamos tentar criar um registro
            print("Tentando inserir um registro de teste...")
            
            # Criando um registro genérico com campos prováveis
            if table_name == 'logs':
                test_data = {
                    'service_time': 0.1,
                    'rooms_ids': [],  # Nome que estamos usando no código
                    'room_ids': [],   # Nome alternativo que pode estar no banco
                    'success_count': 0,
                    'total_count': 0
                }
            elif table_name == 'rooms':
                test_data = {
                    'room_id': '999999999',
                    'label': 'Registro de teste'
                }
            else:
                test_data = {}
            
            # Inserir registro
            try:
                result = supabase.table(table_name).insert(test_data).execute()
                print(f"Registro de teste inserido com sucesso em {table_name}")
                
                # Imprimir detalhes do registro
                print(f"Detalhes do registro inserido:")
                print(result.data)
                
                # Excluir o registro
                if result.data and len(result.data) > 0:
                    id_field = 'id'  # Campo ID padrão
                    if id_field in result.data[0]:
                        test_id = result.data[0][id_field]
                        supabase.table(table_name).delete().eq(id_field, test_id).execute()
                        print(f"Registro de teste excluído com sucesso")
            except Exception as e:
                err_str = str(e)
                print(f"❌ Erro ao inserir registro de teste: {err_str}")
                
                # Analisar o erro para obter informações sobre a estrutura
                if "Could not find the" in err_str and "column" in err_str:
                    print("\n⚠️ Erro de coluna não encontrada. Isso pode indicar problemas com os nomes das colunas.")
                    
                # Se falhar com rooms_ids, tentar com room_ids (sem o 's')
                if "rooms_ids" in err_str and table_name == 'logs':
                    print("\nTentando com 'room_ids' (sem o 's' final)...")
                    try:
                        test_data = {
                            'service_time': 0.1,
                            'room_ids': [123],
                            'success_count': 0,
                            'total_count': 0
                        }
                        result = supabase.table(table_name).insert(test_data).execute()
                        print(f"✅ Registro de teste inserido com sucesso usando 'room_ids'")
                        print(f"Detalhes do registro inserido:")
                        print(result.data)
                        
                        # Excluir o registro
                        if result.data and len(result.data) > 0:
                            id_field = 'id'  # Campo ID padrão
                            if id_field in result.data[0]:
                                test_id = result.data[0][id_field]
                                supabase.table(table_name).delete().eq(id_field, test_id).execute()
                                print(f"Registro de teste excluído com sucesso")
                    except Exception as e2:
                        print(f"❌ Erro ao inserir com 'room_ids': {str(e2)}")
            
            return
        
        # Obter a estrutura a partir dos dados
        record = response.data[0]
        
        print(f"\n===== ESTRUTURA DA TABELA {table_name.upper()} =====")
        print(f"Colunas encontradas:")
        
        for col_name, value in record.items():
            col_type = type(value).__name__ if value is not None else "desconhecido"
            print(f"  {col_name}: {col_type} = {value}")
        
        print("=======================================\n")
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {str(e)}")

def main():
    """Função principal"""
    # Verificar se tabela foi especificada
    if len(sys.argv) < 2:
        print("Uso: python check_table_structure.py NOME_DA_TABELA")
        print("Exemplo: python check_table_structure.py logs")
        sys.exit(1)
    
    table_name = sys.argv[1]
    
    # Verificar estrutura
    check_table_structure(table_name)

if __name__ == "__main__":
    main()