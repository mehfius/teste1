#!/usr/bin/env python3
"""
Script para criar a tabela de logs no Supabase diretamente
"""

import os
import sys
from supabase import create_client

def create_logs_table():
    """
    Cria a tabela logs no Supabase se ela não existir usando métodos diretos
    """
    # Verificar se as variáveis de ambiente necessárias estão disponíveis
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
    
    # Verificar se a tabela existe
    try:
        # Tentar buscar um registro da tabela
        supabase.table('logs').select('id').limit(1).execute()
        print("✅ Tabela logs já existe")
        return True
    except Exception as e:
        print(f"Tabela logs não encontrada ou erro: {str(e)}")
        print("Tentaremos criar a tabela...")
    
    # Já que não conseguimos usar o exec_sql, vamos dar instruções para criar manualmente
    print("\n==============================================================")
    print("IMPORTANTE: A tabela 'logs' precisa ser criada manualmente.")
    print("==============================================================")
    print("Por favor, acesse o Editor SQL do Supabase e execute o seguinte SQL:\n")
    
    sql = """
-- Verificar se a extensão uuid-ossp está ativada, necessária para gerar UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Criação da tabela logs se não existir
CREATE TABLE IF NOT EXISTS logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_time FLOAT NOT NULL,  -- Tempo de execução em segundos
    rooms_ids INTEGER[] NOT NULL,  -- Array de IDs dos quartos processados
    success_count INTEGER NOT NULL,  -- Número de quartos processados com sucesso
    total_count INTEGER NOT NULL,  -- Número total de quartos processados
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Comentários para documentação
COMMENT ON TABLE logs IS 'Registros de execução do scraper do Airbnb';
COMMENT ON COLUMN logs.service_time IS 'Tempo total de execução em segundos';
COMMENT ON COLUMN logs.rooms_ids IS 'Array com os IDs de todos os quartos verificados';
COMMENT ON COLUMN logs.success_count IS 'Quantidade de quartos processados com sucesso';
COMMENT ON COLUMN logs.total_count IS 'Quantidade total de quartos processados';
"""
    
    print(sql)
    print("\n==============================================================")
    print("Após criar a tabela, tente executar novamente o batch_scraper.sh")
    print("==============================================================")
    
    return False

if __name__ == "__main__":
    print("Verificando tabela de logs no Supabase...")
    create_logs_table()