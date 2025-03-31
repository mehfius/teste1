#!/bin/bash
# Script para executar o scraping de todos os quartos do Airbnb registrados no Supabase
# Uso: ./batch_scraper.sh [--limit NUMERO] [--extract] [--update-supabase]

# Diretórios padrão
OUTPUT_DIR="./output"
EXTRACT=false
UPDATE_SUPABASE=false
COMPARE=false
COMPARE_FORMAT="html"
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
    --output-dir=*)
      OUTPUT_DIR="${1#*=}"
      shift
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --extract)
      EXTRACT=true
      shift
      ;;
    --update-supabase)
      UPDATE_SUPABASE=true
      EXTRACT=true  # Extração é necessária para atualizar o Supabase
      shift
      ;;
    --compare)
      COMPARE=true
      shift
      ;;
    --compare-format=*)
      COMPARE=true
      COMPARE_FORMAT="${1#*=}"
      shift
      ;;
    --compare-format)
      COMPARE=true
      COMPARE_FORMAT="$2"
      shift 2
      ;;
    --help)
      echo "Uso: $0 [--limit=N] [--output-dir=DIR] [--extract] [--update-supabase] [--compare] [--compare-format=FORMAT]"
      echo "Opções:"
      echo "  --limit N          Limita o processamento a N quartos (0 = sem limite)"
      echo "  --output-dir DIR   Diretório para salvar os arquivos HTML (padrão: ./output)"
      echo "  --extract          Extrai o texto dos arquivos HTML"
      echo "  --update-supabase  Atualiza os títulos no Supabase (implica --extract)"
      echo "  --compare          Compara diferentes versões de scrapes e gera relatório"
      echo "  --compare-format F Formato do relatório: json, txt, html (padrão: html)"
      echo "  --help             Mostra esta ajuda"
      echo ""
      echo "Nota: Os room_ids são obtidos automaticamente da tabela 'rooms' do Supabase."
      echo "      Para listar os IDs disponíveis, execute 'python get_rooms.py'."
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
if [ ! -f "./get_rooms.py" ]; then
  echo "Erro: Script get_rooms.py não encontrado."
  exit 1
fi

if [ ! -f "./run_scraper.sh" ]; then
  echo "Erro: Script run_scraper.sh não encontrado."
  exit 1
fi

echo "Iniciando batch scraper do Airbnb"
echo "Configurações:"
echo "  Diretório de saída: $OUTPUT_DIR"
echo "  Extração de texto: $([ "$EXTRACT" = true ] && echo "Ativada" || echo "Desativada")"
echo "  Atualização do Supabase: $([ "$UPDATE_SUPABASE" = true ] && echo "Ativada" || echo "Desativada")"
echo "  Comparação de scrapes: $([ "$COMPARE" = true ] && echo "Ativada (formato: $COMPARE_FORMAT)" || echo "Desativada")"
if [ "$LIMIT" -gt 0 ]; then
  echo "  Limite de quartos: $LIMIT"
else
  echo "  Limite de quartos: Sem limite"
fi
echo ""

# Obter todos os room_ids do Supabase
echo "Obtendo lista de room_ids do Supabase..."
# Executa o script Python e guarda a saída completa
PYTHON_OUTPUT=$(python get_rooms.py)
if [ $? -ne 0 ]; then
  echo "Erro ao obter room_ids do Supabase."
  exit 1
fi

# Filtra apenas as linhas que contêm os IDs numéricos, ignorando mensagens de log
ROOM_IDS=$(echo "$PYTHON_OUTPUT" | grep -E '^[0-9]+$')

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
  
  # Determinar a ação com base nas flags
  if [ "$UPDATE_SUPABASE" = true ]; then
    ACTION="extract-supabase"
  elif [ "$EXTRACT" = true ]; then
    ACTION="extract"
  else
    ACTION="scrape"
  fi
  
  # Executar o scraper
  ./run_scraper.sh "$ROOM_ID" "$OUTPUT_DIR" "puppeteer" "$ACTION"
  
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

# Registrar a execução no Supabase se a atualização estiver ativada
if [ "$UPDATE_SUPABASE" = true ]; then
  echo ""
  echo "Registrando log de execução no Supabase..."
  
  # Criar um script Python temporário para registrar o log
  cat > register_log.py << EOL
#!/usr/bin/env python3
from supabase_updater import SupabaseUpdater

# Inicializar o atualizador
updater = SupabaseUpdater()

# Converter a string de IDs para uma lista de inteiros
rooms_ids_str = "${ALL_ROOMS_ARRAY}"
rooms_ids = [int(room_id) for room_id in rooms_ids_str.split(',') if room_id.strip()]

print(f"Registrando log para {len(rooms_ids)} quartos processados")
result = updater.log_execution(
    service_time=${EXECUTION_TIME},
    rooms_ids=rooms_ids,
    success_count=${SUCCESS},
    total_count=${TOTAL_ROOMS}
)

if result.get('success'):
    print("✅ Log de execução registrado com sucesso no Supabase")
    exit(0)
else:
    print(f"❌ Falha ao registrar log: {result.get('error', 'Erro desconhecido')}")
    exit(1)
EOL

  # Executar o script
  python register_log.py
  LOG_RESULT=$?
  
  # Remover o script temporário
  rm register_log.py
  
  if [ $LOG_RESULT -eq 0 ]; then
    echo "✅ Log de execução registrado com sucesso"
  else
    echo "❌ Falha ao registrar log de execução"
  fi
fi

# Realizar comparação de scrapes se solicitado
if [ "$COMPARE" = true ]; then
  echo ""
  echo "=== Iniciando comparação de scrapes ==="
  
  # Verificar se o script de comparação existe
  if [ ! -f "./compare_scrapes.py" ]; then
    echo "Erro: Script de comparação (compare_scrapes.py) não encontrado."
    echo "Instale o script para usar a funcionalidade de comparação."
  else
    # Construir o comando de comparação
    COMPARE_CMD="./compare_scrapes.sh --format=$COMPARE_FORMAT"
    
    # Executar a comparação
    echo "Executando comparação com formato $COMPARE_FORMAT..."
    eval $COMPARE_CMD
    
    COMPARE_RESULT=$?
    if [ $COMPARE_RESULT -eq 0 ]; then
      echo "✅ Comparação concluída com sucesso"
    else
      echo "❌ Falha na comparação com código de saída: $COMPARE_RESULT"
    fi
  fi
fi

# Retornar com base no resultado do processamento
if [ "$FAILED" -gt 0 ]; then
  exit 1
else
  exit 0
fi