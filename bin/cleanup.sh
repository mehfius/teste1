#!/bin/bash
# Script para limpar todos os arquivos temporários do projeto
# Mantém apenas os arquivos necessários e remove todos os arquivos temporários de saída

echo "Limpando diretórios e arquivos temporários..."

# Remover arquivos HTML capturados
echo "Removendo arquivos HTML da pasta output..."
rm -rf ./output/*.html 2>/dev/null

# Remover arquivos JSON e TXT extraídos
echo "Removendo arquivos extraídos da pasta extracted..."
rm -rf ./extracted/*.json ./extracted/*.txt 2>/dev/null

# Remover arquivos temporários do Docker
echo "Removendo arquivos temporários do Docker..."
rm -rf ./docker_output/* 2>/dev/null

# Remover screenshots
echo "Removendo screenshots..."
rm -rf ./screenshots/* 2>/dev/null

# Remover relatórios de comparação
echo "Removendo relatórios de comparação..."
rm -rf ./comparison_reports/* 2>/dev/null

# Remover restos de Python se existirem
echo "Removendo resíduos de Python..."
find . -name "__pycache__" -type d | xargs rm -rf 2>/dev/null
find . -name "*.pyc" -type f -delete 2>/dev/null
find . -name "*.pyo" -type f -delete 2>/dev/null
find . -name "*.pyd" -type f -delete 2>/dev/null

echo "✅ Limpeza concluída!"
echo ""
echo "Os seguintes diretórios foram mantidos vazios com arquivos .gitkeep:"
echo " - ./output/"
echo " - ./extracted/"
echo " - ./docker_output/"
echo " - ./screenshots/"
echo " - ./comparison_reports/"

# Garantir que os diretórios existam e tenham um arquivo .gitkeep
mkdir -p ./output ./extracted ./docker_output ./screenshots ./comparison_reports

# Criar arquivos .gitkeep nos diretórios para garantir que sejam incluídos no git
for dir in ./output ./extracted ./docker_output ./screenshots ./comparison_reports; do
  touch "$dir/.gitkeep"
done

echo ""
echo "O processo está pronto para novas execuções."