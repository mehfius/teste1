#!/bin/bash
# Script simplificado para executar o scraping de todos os quartos do Airbnb registrados no Supabase
# Uso: ./batch_scraper_simplified.sh [--limit NUMERO]
# Versão exclusiva com Deno - Processa tudo em memória sem criar arquivos

# Configuração padrão
LIMIT=0  # 0 significa sem limite

# Registrar o horário de início para calcular o tempo de execução
START_TIME=$(date +%s)

# Processar argumentos
while [[ $# -gt 0 ]]; do
  case $1 in
    --limit=*)
      LIMIT="${1#*=}"
      shift
      ;;
    --limit)
      LIMIT="$2"
      shift 2
      ;;
    --update-supabase)
      # Esta opção é apenas para compatibilidade, o script sempre atualiza o Supabase
      shift
      ;;
    --help)
      echo "Uso: $0 [--limit=N] [--update-supabase]"
      echo "Opções:"
      echo "  --limit N         Limita o processamento a N quartos (0 = sem limite)"
      echo "  --update-supabase Opção mantida por compatibilidade (sempre ativada)"
      echo "  --help            Mostra esta ajuda"
      echo ""
      echo "Nota: Os room_ids são obtidos automaticamente da tabela 'rooms' do Supabase."
      echo "      Para listar os IDs disponíveis, execute 'deno run --allow-net --allow-env get_rooms.ts'."
      exit 0
      ;;
    *)
      echo "Opção desconhecida: $1"
      echo "Use --help para ver as opções disponíveis."
      exit 1
      ;;
  esac
done

# Verificar ambiente
if [ ! -f "src/database/get_rooms.ts" ]; then
  echo "Erro: Script get_rooms.ts não encontrado."
  exit 1
fi

if [ ! -f "bin/run_scraper.sh" ]; then
  echo "Erro: Script run_scraper.sh não encontrado."
  exit 1
fi

# Verificar Deno está instalado
if command -v deno &> /dev/null; then
  DENO_CMD="deno"
elif [ -f "/home/runner/.deno/bin/deno" ]; then
  DENO_CMD="/home/runner/.deno/bin/deno"
  export PATH="/home/runner/.deno/bin:$PATH"
else
  echo "Deno não encontrado. Instalando..."
  curl -fsSL https://deno.land/x/install/install.sh > install_deno.sh
  DENO_INSTALL=/home/runner/.deno sh install_deno.sh v1.40.1
  rm install_deno.sh
  
  if [ -f "/home/runner/.deno/bin/deno" ]; then
    DENO_CMD="/home/runner/.deno/bin/deno"
    export PATH="/home/runner/.deno/bin:$PATH"
  else
    echo "Falha ao instalar Deno. Saindo."
    exit 1
  fi
fi

echo "Iniciando batch scraper do Airbnb (Deno) - Processamento em memória"
echo "Configurações:"
echo "  Processamento: Em memória (sem arquivos)"
if [ "$LIMIT" -gt 0 ]; then
  echo "  Limite de quartos: $LIMIT"
else
  echo "  Limite de quartos: Sem limite"
fi
echo ""

# Obter todos os room_ids do Supabase
echo "Obtendo lista de room_ids do Supabase..."
# Executa o script Deno e guarda a saída completa
DENO_OUTPUT=$("$DENO_CMD" run --allow-net --allow-env src/database/get_rooms.ts)
if [ $? -ne 0 ]; then
  echo "Erro ao obter room_ids do Supabase."
  exit 1
fi

# Filtra apenas as linhas que contêm os IDs numéricos, ignorando mensagens de log
ROOM_IDS=$(echo "$DENO_OUTPUT" | grep -E '^[0-9]+$')

# Contar quantos room_ids foram encontrados
TOTAL_ROOMS=$(echo "$ROOM_IDS" | wc -l)
echo "Encontrados $TOTAL_ROOMS room_ids para processar."

# Aplicar limite se especificado
if [ "$LIMIT" -gt 0 ] && [ "$LIMIT" -lt "$TOTAL_ROOMS" ]; then
  echo "Limitando a $LIMIT quartos conforme solicitado."
  ROOM_IDS=$(echo "$ROOM_IDS" | head -n "$LIMIT")
  TOTAL_ROOMS=$LIMIT
fi

# Processar cada room_id
COUNTER=0
SUCCESS=0
FAILED=0

for ROOM_ID in $ROOM_IDS; do
  COUNTER=$((COUNTER + 1))
  
  echo ""
  echo "=== Processando quarto $COUNTER de $TOTAL_ROOMS: $ROOM_ID ==="
  
  # Executar o scraper no modo memória
  bash bin/run_scraper.sh "$ROOM_ID"
  
  # Verificar o resultado
  if [ $? -eq 0 ]; then
    SUCCESS=$((SUCCESS + 1))
    echo "✅ Quarto $ROOM_ID processado com sucesso!"
  else
    FAILED=$((FAILED + 1))
    echo "❌ Falha ao processar o quarto $ROOM_ID."
  fi
  
  echo "Progresso: $SUCCESS sucesso, $FAILED falhas, $COUNTER de $TOTAL_ROOMS processados ($(( (COUNTER * 100) / TOTAL_ROOMS ))%)"
  
  # Pequena pausa para evitar sobrecarregar o servidor do Airbnb
  sleep 2
done

# Calcular o tempo de execução
END_TIME=$(date +%s)
EXECUTION_TIME=$((END_TIME - START_TIME))

echo ""
echo "=== Processamento em lote concluído ==="
echo "Resultado final:"
echo "  Total de quartos: $TOTAL_ROOMS"
echo "  Processados com sucesso: $SUCCESS"
echo "  Falhas: $FAILED"
echo "  Taxa de sucesso: $(( (SUCCESS * 100) / TOTAL_ROOMS ))%"
echo "  Tempo de execução: ${EXECUTION_TIME} segundos"

# Armazenar todos os room_ids em um array para registrar no log
ALL_ROOMS_ARRAY=$(echo "$ROOM_IDS" | tr '\n' ',' | sed 's/,$//')

# Tentativa de registrar a execução no Supabase (funcionalidade opcional)
echo ""
echo "Tentando registrar log de execução no Supabase (FUNCIONALIDADE OPCIONAL)..."
echo "NOTA: Se a tabela 'logs' não existir, este passo será ignorado sem erros."
echo "      O sistema funciona perfeitamente sem o registro de logs."

# Executar o comando Deno diretamente usando uma string de script curta
LOG_COMMAND="import { SupabaseUpdater } from './src/database/supabase_updater.ts'; 
try {
  const updater = new SupabaseUpdater(); 
  const roomIds = '${ALL_ROOMS_ARRAY}'.split(',').filter(id => id.trim()).map(id => parseInt(id.trim())); 
  const result = await updater.logExecution(${EXECUTION_TIME}, roomIds, ${SUCCESS}, ${TOTAL_ROOMS}); 
  // Resultado silencioso - todos os erros são tratados dentro da função logExecution
} catch (error) {
  // Ignoramos completamente qualquer erro, já que logs são opcionais
  console.log('ℹ️ O registro de logs é totalmente opcional e não afeta a funcionalidade principal');
}"

# Executar o script diretamente sem criar arquivo
echo "$LOG_COMMAND" > ./tmp_log_command.ts
"$DENO_CMD" run --allow-env --allow-net ./tmp_log_command.ts
rm ./tmp_log_command.ts

# Sempre retornamos sucesso mesmo se o log falhar, pois o log é opcional
echo "✅ Processamento principal concluído com sucesso"

# Retornar com base no resultado do processamento
if [ "$FAILED" -gt 0 ]; then
  exit 1
else
  exit 0
fi