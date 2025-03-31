#!/usr/bin/env python3
"""
Comparador de raspagens (scrapes) do Airbnb

Este script compara diferentes versões de dados extraídos do mesmo anúncio do Airbnb
para detectar mudanças ao longo do tempo, como alterações de preço, disponibilidade,
avaliações e outras características.

Uso:
  python compare_scrapes.py [--room-id=ID] [--output-dir=DIR] [--report-format=FORMAT]
  
Opções:
  --room-id=ID        ID específico de um quarto para comparar (opcional)
  --output-dir=DIR    Diretório onde salvar os relatórios (padrão: ./comparison_reports)
  --report-format=FORMAT  Formato do relatório: json, txt, html (padrão: json)
"""

import os
import sys
import json
import glob
import argparse
import difflib
import datetime
from collections import defaultdict
from typing import Dict, List, Any, Tuple, Optional

class ScrapesComparer:
    """
    Classe para comparar diferentes versões de dados extraídos do Airbnb
    e identificar mudanças relevantes.
    """
    
    def __init__(self, extracted_dir: str = "./extracted", output_dir: str = "./comparison_reports"):
        """
        Inicializa o comparador.
        
        Args:
            extracted_dir: Diretório onde estão os arquivos extraídos
            output_dir: Diretório onde serão salvos os relatórios de comparação
        """
        self.extracted_dir = extracted_dir
        self.output_dir = output_dir
        
        # Garantir que o diretório de saída existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Campos importantes para monitorar mudanças
        self.key_fields = [
            'title',
            'price',
            'rating',
            'reviews_count',
            'location',
            'features'
        ]
        
        # Mapeamento para mensagens amigáveis
        self.field_names = {
            'title': 'Título',
            'price': 'Preço',
            'rating': 'Avaliação',
            'reviews_count': 'Número de avaliações',
            'location': 'Localização',
            'features': 'Características'
        }
    
    def get_all_room_ids(self) -> List[str]:
        """
        Obtém todos os room_ids com arquivos extraídos.
        
        Returns:
            Lista de room_ids únicos encontrados
        """
        # Padrão de nomes de arquivos: airbnb_ROOM_ID_*.json
        json_files = glob.glob(os.path.join(self.extracted_dir, "airbnb_*_*.json"))
        
        # Extrair os room_ids únicos
        room_ids = set()
        for file_path in json_files:
            file_name = os.path.basename(file_path)
            if file_name.startswith("airbnb_") and "_" in file_name:
                parts = file_name.split("_")
                if len(parts) >= 2:
                    room_ids.add(parts[1])
        
        return list(room_ids)
    
    def get_files_for_room(self, room_id: str) -> List[str]:
        """
        Obtém todos os arquivos JSON extraídos para um determinado room_id.
        
        Args:
            room_id: ID do quarto/anúncio do Airbnb
            
        Returns:
            Lista de caminhos de arquivos, ordenados do mais antigo para o mais recente
        """
        pattern = os.path.join(self.extracted_dir, f"airbnb_{room_id}_*.json")
        files = glob.glob(pattern)
        
        # Ordenar por data/hora (contida no nome do arquivo)
        def extract_timestamp(file_path):
            file_name = os.path.basename(file_path)
            parts = file_name.split("_")
            if len(parts) >= 3:
                # O timestamp está no formato 2025-03-31T01-40-57
                timestamp_str = "_".join(parts[2:]).split(".")[0]
                try:
                    # Converter para datetime para ordenação adequada
                    return datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H-%M-%S")
                except ValueError:
                    pass
            return datetime.datetime(1970, 1, 1)  # Fallback para arquivos com formato inesperado
        
        return sorted(files, key=extract_timestamp)
    
    def load_json_data(self, file_path: str) -> Dict[str, Any]:
        """
        Carrega dados JSON de um arquivo.
        
        Args:
            file_path: Caminho para o arquivo JSON
            
        Returns:
            Dicionário com os dados carregados ou dicionário vazio em caso de erro
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Erro ao carregar arquivo {file_path}: {str(e)}", file=sys.stderr)
            return {}
    
    def compare_values(self, old_value: Any, new_value: Any) -> bool:
        """
        Compara dois valores e determina se houve mudança significativa.
        
        Args:
            old_value: Valor anterior
            new_value: Valor atual
            
        Returns:
            True se os valores forem significativamente diferentes
        """
        # Para strings, ignorar diferenças de espaço e capitalização
        if isinstance(old_value, str) and isinstance(new_value, str):
            return old_value.strip().lower() != new_value.strip().lower()
        
        # Para números, considerar pequenas variações (menos de 1%) como não significativas
        if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
            if old_value == 0:
                return new_value != 0
            return abs((new_value - old_value) / old_value) >= 0.01
        
        # Para listas, verificar se o conteúdo mudou
        if isinstance(old_value, list) and isinstance(new_value, list):
            if len(old_value) != len(new_value):
                return True
            
            # Comparar cada elemento
            old_value_sorted = sorted([str(x).strip().lower() for x in old_value])
            new_value_sorted = sorted([str(x).strip().lower() for x in new_value])
            return old_value_sorted != new_value_sorted
        
        # Para outros tipos, comparação direta
        return old_value != new_value
    
    def format_change(self, field: str, old_value: Any, new_value: Any) -> str:
        """
        Formata uma mudança para exibição em relatório.
        
        Args:
            field: Nome do campo
            old_value: Valor anterior
            new_value: Valor atual
            
        Returns:
            String formatada descrevendo a mudança
        """
        field_name = self.field_names.get(field, field)
        
        # Para listas, mostrar o que foi adicionado/removido
        if isinstance(old_value, list) and isinstance(new_value, list):
            old_set = set([str(x).strip().lower() for x in old_value])
            new_set = set([str(x).strip().lower() for x in new_value])
            
            added = new_set - old_set
            removed = old_set - new_set
            
            changes = []
            if added:
                changes.append(f"Adicionado: {', '.join(added)}")
            if removed:
                changes.append(f"Removido: {', '.join(removed)}")
            
            return f"{field_name}: {' | '.join(changes)}"
        
        # Para preços, mostrar variação percentual
        if field == 'price' and isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
            if old_value > 0:
                percentage = ((new_value - old_value) / old_value) * 100
                direction = "aumentou" if percentage > 0 else "diminuiu"
                return f"{field_name}: {old_value} → {new_value} ({direction} {abs(percentage):.1f}%)"
        
        # Para outros campos, mostrar valor anterior e atual
        return f"{field_name}: {old_value} → {new_value}"
    
    def compare_scrapes(self, room_id: str) -> List[Dict[str, Any]]:
        """
        Compara diferentes versões de scrapes para um room_id específico.
        
        Args:
            room_id: ID do quarto/anúncio do Airbnb
            
        Returns:
            Lista de dicionários com as mudanças detectadas
        """
        files = self.get_files_for_room(room_id)
        if len(files) < 2:
            print(f"Não há arquivos suficientes para comparação do room_id {room_id} (mínimo 2 necessários)")
            return []
        
        all_changes = []
        
        # Carregar o dado mais recente para referência
        latest_file = files[-1]
        latest_data = self.load_json_data(latest_file)
        latest_timestamp = self._extract_timestamp_from_filename(os.path.basename(latest_file))
        
        # Comparar com versões anteriores, do mais recente para o mais antigo
        for i in range(len(files) - 2, -1, -1):
            old_file = files[i]
            old_data = self.load_json_data(old_file)
            old_timestamp = self._extract_timestamp_from_filename(os.path.basename(old_file))
            
            # Detectar mudanças
            changes = self._detect_changes(old_data, latest_data)
            
            if changes:
                change_record = {
                    'room_id': room_id,
                    'old_timestamp': old_timestamp,
                    'new_timestamp': latest_timestamp,
                    'changes': changes,
                    'old_file': os.path.basename(old_file),
                    'new_file': os.path.basename(latest_file)
                }
                all_changes.append(change_record)
        
        return all_changes
    
    def _extract_timestamp_from_filename(self, filename: str) -> str:
        """
        Extrai o timestamp do nome do arquivo.
        
        Args:
            filename: Nome do arquivo no formato airbnb_ROOM_ID_TIMESTAMP.json
            
        Returns:
            String com o timestamp ou string vazia se não encontrado
        """
        parts = filename.split("_")
        if len(parts) >= 3:
            timestamp_parts = "_".join(parts[2:]).split(".")[0]
            return timestamp_parts
        return ""
    
    def _detect_changes(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detecta mudanças entre duas versões de dados extraídos.
        
        Args:
            old_data: Dados da versão anterior
            new_data: Dados da versão atual
            
        Returns:
            Lista de dicionários descrevendo as mudanças detectadas
        """
        changes = []
        
        for field in self.key_fields:
            if field in old_data and field in new_data:
                old_value = old_data[field]
                new_value = new_data[field]
                
                if self.compare_values(old_value, new_value):
                    changes.append({
                        'field': field,
                        'old_value': old_value,
                        'new_value': new_value,
                        'formatted': self.format_change(field, old_value, new_value)
                    })
            elif field in new_data and field not in old_data:
                changes.append({
                    'field': field,
                    'old_value': None,
                    'new_value': new_data[field],
                    'formatted': f"{self.field_names.get(field, field)}: Adicionado ({new_data[field]})"
                })
            elif field in old_data and field not in new_data:
                changes.append({
                    'field': field,
                    'old_value': old_data[field],
                    'new_value': None,
                    'formatted': f"{self.field_names.get(field, field)}: Removido ({old_data[field]})"
                })
        
        return changes
    
    def generate_report(self, room_id: Optional[str] = None, format: str = 'json') -> str:
        """
        Gera um relatório de comparação para um ou todos os room_ids.
        
        Args:
            room_id: ID específico ou None para todos
            format: Formato do relatório (json, txt, html)
            
        Returns:
            Caminho para o arquivo de relatório gerado
        """
        if room_id:
            room_ids = [room_id]
        else:
            room_ids = self.get_all_room_ids()
        
        all_changes = {}
        for rid in room_ids:
            changes = self.compare_scrapes(rid)
            if changes:
                all_changes[rid] = changes
        
        # Definir nome do arquivo de saída
        timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        specific = f"_{room_id}" if room_id else ""
        output_file = os.path.join(self.output_dir, f"comparison{specific}_{timestamp}.{format}")
        
        # Gerar relatório no formato solicitado
        if format == 'json':
            self._write_json_report(all_changes, output_file)
        elif format == 'txt':
            self._write_text_report(all_changes, output_file)
        elif format == 'html':
            self._write_html_report(all_changes, output_file)
        else:
            print(f"Formato {format} não suportado. Usando JSON.", file=sys.stderr)
            output_file = output_file.replace(f".{format}", ".json")
            self._write_json_report(all_changes, output_file)
        
        return output_file
    
    def _write_json_report(self, changes: Dict[str, List[Dict[str, Any]]], output_file: str) -> None:
        """
        Escreve o relatório em formato JSON.
        
        Args:
            changes: Dicionário com todas as mudanças detectadas
            output_file: Caminho para o arquivo de saída
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(changes, f, ensure_ascii=False, indent=2)
        
        print(f"Relatório JSON salvo em: {output_file}")
    
    def _write_text_report(self, changes: Dict[str, List[Dict[str, Any]]], output_file: str) -> None:
        """
        Escreve o relatório em formato de texto plano.
        
        Args:
            changes: Dicionário com todas as mudanças detectadas
            output_file: Caminho para o arquivo de saída
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO DE COMPARAÇÃO DE SCRAPES DO AIRBNB\n")
            f.write(f"Gerado em: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if not changes:
                f.write("Nenhuma mudança detectada.\n")
                return
            
            for room_id, room_changes in changes.items():
                f.write(f"=== Room ID: {room_id} ===\n")
                f.write(f"Total de comparações: {len(room_changes)}\n\n")
                
                for i, change_set in enumerate(room_changes, 1):
                    f.write(f"Comparação {i}:\n")
                    f.write(f"Arquivo antigo: {change_set['old_file']}\n")
                    f.write(f"Arquivo novo: {change_set['new_file']}\n")
                    f.write(f"Período: {change_set['old_timestamp']} → {change_set['new_timestamp']}\n")
                    f.write("Mudanças detectadas:\n")
                    
                    for change in change_set['changes']:
                        f.write(f"  - {change['formatted']}\n")
                    
                    f.write("\n")
        
        print(f"Relatório de texto salvo em: {output_file}")
    
    def _write_html_report(self, changes: Dict[str, List[Dict[str, Any]]], output_file: str) -> None:
        """
        Escreve o relatório em formato HTML.
        
        Args:
            changes: Dicionário com todas as mudanças detectadas
            output_file: Caminho para o arquivo de saída
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Comparação de Anúncios do Airbnb</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #FF5A5F; /* Cor do Airbnb */ }
        .room { margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
        .room-header { background-color: #f8f8f8; padding: 10px; margin-bottom: 15px; border-radius: 3px; }
        .comparison { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px dashed #ccc; }
        .changes { margin-left: 20px; }
        .change-item { margin: 5px 0; }
        .price-increase { color: #e74c3c; /* vermelho */ }
        .price-decrease { color: #27ae60; /* verde */ }
        .timestamp { color: #7f8c8d; font-size: 0.9em; }
        .no-changes { color: #7f8c8d; font-style: italic; }
    </style>
</head>
<body>
    <h1>Relatório de Comparação de Anúncios do Airbnb</h1>
    <p>Gerado em: {timestamp}</p>
""".format(timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            if not changes:
                f.write("<p class='no-changes'>Nenhuma mudança detectada.</p>")
                f.write("</body></html>")
                return
            
            for room_id, room_changes in changes.items():
                f.write(f"<div class='room'>\n")
                f.write(f"<div class='room-header'><h2>Room ID: {room_id}</h2>")
                f.write(f"<p>Total de comparações: {len(room_changes)}</p></div>\n")
                
                for i, change_set in enumerate(room_changes, 1):
                    f.write(f"<div class='comparison'>\n")
                    f.write(f"<h3>Comparação {i}</h3>\n")
                    f.write(f"<p>Arquivo antigo: <code>{change_set['old_file']}</code></p>\n")
                    f.write(f"<p>Arquivo novo: <code>{change_set['new_file']}</code></p>\n")
                    f.write(f"<p class='timestamp'>Período: {change_set['old_timestamp']} → {change_set['new_timestamp']}</p>\n")
                    f.write("<h4>Mudanças detectadas:</h4>\n")
                    f.write("<ul class='changes'>\n")
                    
                    for change in change_set['changes']:
                        css_class = ""
                        if change['field'] == 'price':
                            if isinstance(change['old_value'], (int, float)) and isinstance(change['new_value'], (int, float)):
                                if change['new_value'] > change['old_value']:
                                    css_class = "price-increase"
                                elif change['new_value'] < change['old_value']:
                                    css_class = "price-decrease"
                        
                        f.write(f"<li class='change-item {css_class}'>{change['formatted']}</li>\n")
                    
                    f.write("</ul>\n")
                    f.write("</div>\n")
                
                f.write("</div>\n")
            
            f.write("</body></html>")
        
        print(f"Relatório HTML salvo em: {output_file}")

def main():
    """Função principal do script"""
    parser = argparse.ArgumentParser(description='Compara diferentes scrapes do Airbnb para detectar mudanças.')
    parser.add_argument('--room-id', help='ID específico do quarto para comparar')
    parser.add_argument('--extracted-dir', default='./extracted', help='Diretório com arquivos extraídos')
    parser.add_argument('--output-dir', default='./comparison_reports', help='Diretório para salvar relatórios')
    parser.add_argument('--report-format', default='json', choices=['json', 'txt', 'html'], 
                        help='Formato do relatório: json, txt, html')
    
    args = parser.parse_args()
    
    comparer = ScrapesComparer(extracted_dir=args.extracted_dir, output_dir=args.output_dir)
    
    if args.room_id:
        print(f"Comparando scrapes para o room_id: {args.room_id}")
        report_file = comparer.generate_report(room_id=args.room_id, format=args.report_format)
    else:
        print("Comparando scrapes para todos os room_ids disponíveis")
        report_file = comparer.generate_report(format=args.report_format)
    
    print(f"Relatório gerado com sucesso: {report_file}")
    
    # Contar quantas mudanças foram detectadas
    if args.report_format == 'json':
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
                total_rooms = len(report_data)
                total_changes = sum(len(changes) for changes in report_data.values())
                print(f"Detectadas mudanças em {total_rooms} quartos, com um total de {total_changes} comparações.")
        except Exception as e:
            print(f"Erro ao analisar o relatório: {str(e)}", file=sys.stderr)

if __name__ == "__main__":
    main()