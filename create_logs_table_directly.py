#!/usr/bin/env python3
"""
Script para criar a tabela de logs no Supabase usando SQL direto
"""

import os
import sys
import requests
import base64

def create_logs_table_directly():
    """
    Cria a tabela logs diretamente no Supabase usando requisições REST
    """
    # Verificar variáveis de ambiente
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Erro: As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY são necessárias")
        sys.exit(1)
    
    print("Verificando se a tabela 'logs' já existe...")
    
    # Remove trailing slash if present
    if supabase_url.endswith('/'):
        supabase_url = supabase_url[:-1]
    
    # Headers para a requisição
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # SQL para criar tabela logs
    sql = """
-- Verificar se a extensão uuid-ossp está ativada, necessária para gerar UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Remover tabela logs se já existir para recriar com a estrutura correta
DROP TABLE IF EXISTS logs;

-- Criação da tabela logs
CREATE TABLE logs (
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
    
    try:
        # Fazer a requisição para executar o SQL
        response = requests.post(
            f"{supabase_url}/rest/v1/",
            headers=headers,
            params={'q': sql}
        )
        
        # Verificar se houve erro
        if response.status_code >= 400:
            print(f"❌ Erro ao criar tabela: {response.status_code} - {response.text}")
            
            # Tentar usando o endpoint rpc
            print("Tentando método alternativo...")
            
            # Endpoint para executar SQL raw
            sql_endpoint = f"{supabase_url}/rest/v1/rpc/cria_tabela_logs"
            
            # Payload com o SQL
            payload = {
                "sql": sql
            }
            
            # Fazer a requisição
            response = requests.post(sql_endpoint, headers=headers, json=payload)
            
            if response.status_code >= 400:
                print(f"❌ Segunda tentativa falhou: {response.status_code} - {response.text}")
                
                # Tente uma terceira abordagem usando a técnica de "Stored Procedure"
                print("Tentando terceira abordagem via função SQL...")
                
                # Primeiro criamos uma função SQL que executa o DDL
                create_function_sql = """
CREATE OR REPLACE FUNCTION cria_tabela_logs()
RETURNS void AS $$
BEGIN
    -- Verificar se a extensão uuid-ossp está ativada
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Remover tabela logs se já existir
    DROP TABLE IF EXISTS logs;
    
    -- Criar tabela logs
    CREATE TABLE logs (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        service_time FLOAT NOT NULL,
        room_ids INTEGER[] NOT NULL,
        success_count INTEGER NOT NULL,
        total_count INTEGER NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Comentários
    COMMENT ON TABLE logs IS 'Registros de execução do scraper do Airbnb';
    COMMENT ON COLUMN logs.service_time IS 'Tempo total de execução em segundos';
    COMMENT ON COLUMN logs.room_ids IS 'Array com os IDs de todos os quartos verificados';
    COMMENT ON COLUMN logs.success_count IS 'Quantidade de quartos processados com sucesso';
    COMMENT ON COLUMN logs.total_count IS 'Quantidade total de quartos processados';
END;
$$ LANGUAGE plpgsql;
"""
                
                # Fazer requisição para criar a função
                function_response = requests.post(
                    f"{supabase_url}/rest/v1/",
                    headers=headers,
                    params={'q': create_function_sql}
                )
                
                if function_response.status_code >= 400:
                    print(f"❌ Falha ao criar função: {function_response.status_code} - {function_response.text}")
                    
                    # Gerar um script SQL para o usuário executar manualmente
                    print("\n==============================================================")
                    print("IMPORTANTE: EXECUTE O SEGUINTE SQL NO EDITOR SQL DO SUPABASE")
                    print("==============================================================")
                    print(sql)
                    print("==============================================================")
                    return False
                
                # Agora chamamos a função
                call_function_sql = "SELECT cria_tabela_logs();"
                execute_response = requests.post(
                    f"{supabase_url}/rest/v1/",
                    headers=headers,
                    params={'q': call_function_sql}
                )
                
                if execute_response.status_code >= 400:
                    print(f"❌ Falha ao executar função: {execute_response.status_code} - {execute_response.text}")
                    
                    # Gerar um script SQL para o usuário executar manualmente
                    print("\n==============================================================")
                    print("IMPORTANTE: EXECUTE O SEGUINTE SQL NO EDITOR SQL DO SUPABASE")
                    print("==============================================================")
                    print(sql)
                    print("==============================================================")
                    return False
                
                print("✅ Tabela logs criada com sucesso (via função SQL)")
                return True
                
            else:
                print("✅ Tabela logs criada com sucesso (segunda tentativa)")
                return True
        else:
            print("✅ Tabela logs criada com sucesso")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar tabela logs: {str(e)}")
        
        # Gerar um script SQL para o usuário executar manualmente
        print("\n==============================================================")
        print("IMPORTANTE: EXECUTE O SEGUINTE SQL NO EDITOR SQL DO SUPABASE")
        print("==============================================================")
        print(sql)
        print("==============================================================")
        return False

if __name__ == "__main__":
    print("Criando tabela logs diretamente via API...")
    result = create_logs_table_directly()
    if result:
        print("Operação concluída com sucesso")
        sys.exit(0)
    else:
        print("Falha na operação, por favor execute o SQL manualmente como indicado acima")
        sys.exit(1)