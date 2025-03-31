#!/usr/bin/env python3
"""
Script para criar a tabela de logs no Supabase usando SQL
"""

import os
import sys
from supabase import create_client

def create_logs_table():
    """
    Cria a tabela logs no Supabase
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
    
    # Primeiro, vamos tentar recriar a tabela com um novo nome
    # e com a coluna correta 'room_ids' (sem o 's' final)
    try:
        # Consultar tabela atual para verificar se existe
        try:
            response = supabase.table('logs').select('*').limit(1).execute()
            table_exists = True
            print("Tabela logs existe, vamos recriá-la")
        except:
            table_exists = False
            print("Tabela logs não existe, vamos criá-la")
        
        # Se a tabela existe, tentar inserir com o nome correto da coluna
        if table_exists:
            try:
                # Tentar inserir um log com coluna 'room_ids'
                data = {
                    'service_time': 0.1,
                    'room_ids': [123],
                    'success_count': 1,
                    'total_count': 1
                }
                result = supabase.table('logs').insert(data).execute()
                print("✅ Teste de inserção com 'room_ids' bem-sucedido")
                print("A tabela já possui a coluna room_ids")
                
                # Remover o registro de teste
                try:
                    if result.data and len(result.data) > 0:
                        record_id = result.data[0]['id']
                        supabase.table('logs').delete().eq('id', record_id).execute()
                        print("Registro de teste removido")
                except Exception as e:
                    print(f"Erro ao remover registro de teste: {str(e)}")
                
                return True
            except Exception as e:
                err_str = str(e)
                print(f"❌ Erro ao inserir com room_ids: {err_str}")
                
                # Se o erro não for relacionado a colunas inexistentes, retornar
                if "Could not find the" not in err_str or "column" not in err_str:
                    print("Erro não relacionado à estrutura da tabela")
                    return False
                
                # Caso contrário, vamos tentar com rooms_ids
                try:
                    # Tentar inserir um log com coluna 'rooms_ids'
                    data = {
                        'service_time': 0.1,
                        'rooms_ids': [123],
                        'success_count': 1,
                        'total_count': 1
                    }
                    result = supabase.table('logs').insert(data).execute()
                    print("✅ Teste de inserção com 'rooms_ids' bem-sucedido")
                    print("A tabela já possui a coluna rooms_ids")
                    
                    # Atualizar o supabase_updater.py para usar 'rooms_ids'
                    update_log_execution_function('rooms_ids')
                    
                    # Remover o registro de teste
                    try:
                        if result.data and len(result.data) > 0:
                            record_id = result.data[0]['id']
                            supabase.table('logs').delete().eq('id', record_id).execute()
                            print("Registro de teste removido")
                    except Exception as e:
                        print(f"Erro ao remover registro de teste: {str(e)}")
                    
                    return True
                except Exception as e:
                    err_str = str(e)
                    print(f"❌ Erro ao inserir com rooms_ids: {err_str}")
                    
                    # Se nenhuma das colunas funcionar, precisamos recriar a tabela
                    print("Ambas as tentativas falharam, vamos recriar a tabela")
        
        # Remover a tabela se existir
        if table_exists:
            print("⚠️ Removendo a tabela logs existente...")
            # Não podemos fazer DROP via API, então instruções para usuário
            print("\n==============================================================")
            print("IMPORTANTE: A tabela 'logs' parece estar com problemas.")
            print("==============================================================")
            print("Por favor, acesse o Editor SQL do Supabase e execute o seguinte SQL:\n")
            
            sql_drop = """
DROP TABLE IF EXISTS logs;
"""
            print(sql_drop)
            
            # Perguntar ao usuário se executou o comando
            user_input = input("Você executou o comando DROP TABLE no Supabase? (s/n): ")
            if user_input.lower() not in ['s', 'sim', 'y', 'yes']:
                print("Operação cancelada pelo usuário")
                return False
        
        # Criar a tabela com a coluna 'room_ids' (sem o 's' final)
        print("Criando tabela com o nome de coluna correto room_ids (sem 's')...")
        
        # Instruções para o usuário para criar a tabela manualmente
        print("\n==============================================================")
        print("IMPORTANTE: Execute o seguinte SQL no Editor SQL do Supabase:")
        print("==============================================================")
        
        sql_create = """
-- Verificar se a extensão uuid-ossp está ativada, necessária para gerar UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Criação da tabela logs se não existir
CREATE TABLE IF NOT EXISTS logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_time FLOAT NOT NULL,  -- Tempo de execução em segundos
    room_ids INTEGER[] NOT NULL,  -- Array de IDs dos quartos processados (sem o 's' final)
    success_count INTEGER NOT NULL,  -- Número de quartos processados com sucesso
    total_count INTEGER NOT NULL,  -- Número total de quartos processados
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Comentários para documentação
COMMENT ON TABLE logs IS 'Registros de execução do scraper do Airbnb';
COMMENT ON COLUMN logs.service_time IS 'Tempo total de execução em segundos';
COMMENT ON COLUMN logs.room_ids IS 'Array com os IDs de todos os quartos verificados';
COMMENT ON COLUMN logs.success_count IS 'Quantidade de quartos processados com sucesso';
COMMENT ON COLUMN logs.total_count IS 'Quantidade total de quartos processados';
"""
        
        print(sql_create)
        print("\n==============================================================")
        
        # Perguntar ao usuário se executou o comando
        user_input = input("Você executou o comando CREATE TABLE no Supabase? (s/n): ")
        if user_input.lower() not in ['s', 'sim', 'y', 'yes']:
            print("Operação cancelada pelo usuário")
            return False
        
        # Atualizar o supabase_updater.py para usar o nome correto da coluna
        update_log_execution_function('room_ids')
        
        print("✅ Tabela logs recriada com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao recriar tabela logs: {str(e)}")
        return False

def update_log_execution_function(column_name):
    """
    Atualiza a função log_execution no arquivo supabase_updater.py
    para usar o nome correto da coluna
    
    Args:
        column_name: Nome correto da coluna (room_ids ou rooms_ids)
    """
    print(f"Atualizando supabase_updater.py para usar a coluna '{column_name}'...")
    
    try:
        # Ler o arquivo
        with open('supabase_updater.py', 'r') as file:
            content = file.read()
        
        # Substituir o nome da coluna na função log_execution
        if column_name == 'room_ids':
            # Se precisamos mudar para room_ids (sem o 's' final)
            if '"rooms_ids"' in content:
                content = content.replace('"rooms_ids"', '"room_ids"')
            elif "'rooms_ids'" in content:
                content = content.replace("'rooms_ids'", "'room_ids'")
            elif "rooms_ids:" in content:
                content = content.replace("rooms_ids:", "room_ids:")
        else:
            # Se precisamos mudar para rooms_ids (com o 's' final)
            if '"room_ids"' in content:
                content = content.replace('"room_ids"', '"rooms_ids"')
            elif "'room_ids'" in content:
                content = content.replace("'room_ids'", "'rooms_ids'")
            elif "room_ids:" in content:
                content = content.replace("room_ids:", "rooms_ids:")
        
        # Escrever o arquivo atualizado
        with open('supabase_updater.py', 'w') as file:
            file.write(content)
        
        print(f"✅ Arquivo supabase_updater.py atualizado para usar {column_name}")
    except Exception as e:
        print(f"❌ Erro ao atualizar supabase_updater.py: {str(e)}")

if __name__ == "__main__":
    print("Iniciando criação/correção da tabela logs...")
    create_logs_table()