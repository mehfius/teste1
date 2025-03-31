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