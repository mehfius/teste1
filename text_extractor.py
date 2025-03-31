#!/usr/bin/env python3
"""
Airbnb Text Extractor

Este script extrai o conteúdo de texto relevante de arquivos HTML de anúncios do Airbnb
usando a biblioteca trafilatura.

Uso:
  python text_extractor.py --input arquivo.html
  python text_extractor.py --input-dir diretorio_de_entrada --output-dir diretorio_de_saida
"""

import os
import sys
import argparse
import glob
import json
from datetime import datetime
from pathlib import Path
import trafilatura
from bs4 import BeautifulSoup

class AirbnbTextExtractor:
    """
    Classe para extrair e organizar o conteúdo textual de páginas HTML do Airbnb.
    """
    
    def __init__(self):
        """Inicializa o extrator."""
        pass
    
    def extract_from_file(self, html_file_path):
        """
        Extrai o conteúdo textual de um arquivo HTML do Airbnb.
        
        Args:
            html_file_path: Caminho para o arquivo HTML
            
        Returns:
            dict: Dicionário com o conteúdo extraído e metadados
        """
        try:
            # Abrir e ler o arquivo HTML
            with open(html_file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            # Extrair o conteúdo usando trafilatura com configuração otimizada
            text_content = trafilatura.extract(
                html_content,
                include_comments=False,
                include_tables=True,
                no_fallback=False,  # Usar fallback extraction se necessário
                output_format="txt"  # Corrigido: deve ser 'txt' não 'text'
            )
            
            # Se trafilatura falhar em extrair conteúdo significativo, tentar usar BeautifulSoup para uma extração mais simples
            if not text_content or len(text_content.strip()) < 100:
                print(f"Aviso: Trafilatura extraiu pouco conteúdo, usando fallback com BeautifulSoup")
                soup_fallback = BeautifulSoup(html_content, 'html.parser')
                
                # Verificar se é uma página de erro do Airbnb (JavaScript desabilitado)
                js_error_message = soup_fallback.find(string=lambda text: 'não funcionam corretamente sem a habilitação do JavaScript' in str(text) if text else False)
                if js_error_message:
                    print("Detectada mensagem de erro de JavaScript do Airbnb. O site pode estar bloqueando nosso scraper.")
                
                # Remover scripts, estilos e outros elementos não relevantes
                for element in soup_fallback(['script', 'style', 'head', 'meta', 'link']):
                    element.decompose()
                
                # Tentar encontrar o conteúdo principal
                main_content = soup_fallback.find('main')
                if main_content:
                    text_content = main_content.get_text(separator='\n', strip=True)
                else:
                    # Extrair texto de tudo o que restou se não encontrar o conteúdo principal
                    text_content = soup_fallback.get_text(separator='\n', strip=True)
                
                # Limpar texto extraído
                text_content = '\n'.join(line.strip() for line in text_content.splitlines() if line.strip())
            
            # Extrair informações estruturadas com BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Tentar extrair o título da propriedade
            title = self._extract_title(soup)
            
            # Tentar extrair o preço
            price = self._extract_price(soup)
            
            # Tentar extrair avaliações
            rating, review_count = self._extract_reviews(soup)
            
            # Tentar extrair localização
            location = self._extract_location(soup)
            
            # Tentar extrair características (quartos, banheiros, etc.)
            features = self._extract_features(soup)
            
            # Extrair data do arquivo (do nome do arquivo ou do sistema)
            timestamp = self._extract_timestamp_from_filename(html_file_path)
            
            # Organizar os dados
            result = {
                "metadata": {
                    "source_file": os.path.basename(html_file_path),
                    "extraction_date": datetime.now().isoformat(),
                    "timestamp": timestamp,
                },
                "listing": {
                    "title": title,
                    "price": price,
                    "rating": rating,
                    "review_count": review_count,
                    "location": location,
                    "features": features
                },
                "content": text_content
            }
            
            return result
            
        except Exception as e:
            print(f"Erro ao processar o arquivo {html_file_path}: {str(e)}")
            return None
    
    def process_directory(self, input_dir, output_dir):
        """
        Processa todos os arquivos HTML em um diretório.
        
        Args:
            input_dir: Diretório com arquivos HTML
            output_dir: Diretório para salvar os arquivos de saída
        
        Returns:
            int: Número de arquivos processados com sucesso
        """
        # Criar diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Encontrar todos os arquivos HTML no diretório
        html_files = glob.glob(os.path.join(input_dir, "*.html"))
        
        if not html_files:
            print(f"Nenhum arquivo HTML encontrado em {input_dir}")
            return 0
        
        success_count = 0
        
        for html_file in html_files:
            # Extrair ID do quarto do nome do arquivo
            room_id = self._extract_room_id_from_filename(html_file)
            
            # Nome base do arquivo (sem extensão)
            base_name = os.path.splitext(os.path.basename(html_file))[0]
            
            # Processar o arquivo
            result = self.extract_from_file(html_file)
            
            if result:
                # Salvar como JSON
                json_output_path = os.path.join(output_dir, f"{base_name}.json")
                with open(json_output_path, 'w', encoding='utf-8') as json_file:
                    json.dump(result, json_file, ensure_ascii=False, indent=2)
                
                # Salvar conteúdo de texto em arquivo separado
                text_output_path = os.path.join(output_dir, f"{base_name}.txt")
                with open(text_output_path, 'w', encoding='utf-8') as text_file:
                    text_file.write(result["content"] if result["content"] else "")
                
                print(f"Processado: {html_file} -> {json_output_path}")
                success_count += 1
        
        return success_count

    def _extract_title(self, soup):
        """Extrai o título do anúncio."""
        # Tentar diferentes seletores para o título
        title_selectors = [
            'h1[data-testid="listing-title"]',
            'h1._fecoyn4',
            'h1.atm_7l_1kw7nm4',
            'h2.atm_7l_1kw7nm4',
            'h1',  # Fallback genérico: primeiro h1 da página
            'title'  # Fallback último recurso: usar o título da página
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                # Se for o título da página, tentar limpar um pouco
                if selector == 'title' and ' - Airbnb' in title_text:
                    title_text = title_text.split(' - Airbnb')[0].strip()
                return title_text
        
        return None
    
    def _extract_price(self, soup):
        """Extrai o preço do anúncio."""
        # Tentar diferentes seletores para o preço
        price_selectors = [
            'span[data-testid="listing-price"]',
            'span._tyxjp1',
            'span.atm_c8_1n3c8jb'
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                return price_elem.get_text(strip=True)
        
        return None
    
    def _extract_reviews(self, soup):
        """Extrai a avaliação e quantidade de reviews."""
        rating = None
        review_count = None
        
        # Tentar extrair a avaliação
        rating_selectors = [
            'span[data-testid="rating-value"]',
            'span._17p6nbba',
            'span.atm_7l_1kw7nm4 span'
        ]
        
        for selector in rating_selectors:
            rating_elem = soup.select_one(selector)
            if rating_elem:
                try:
                    rating = float(rating_elem.get_text(strip=True).replace(',', '.'))
                    break
                except ValueError:
                    pass
        
        # Tentar extrair o número de avaliações
        review_count_selectors = [
            'span[data-testid="reviews-count"]',
            'span._s65ijh7',
            'button._1qf7wt0z span'
        ]
        
        for selector in review_count_selectors:
            count_elem = soup.select_one(selector)
            if count_elem:
                text = count_elem.get_text(strip=True)
                # Extrair apenas os números
                import re
                numbers = re.findall(r'\d+', text)
                if numbers:
                    try:
                        review_count = int(''.join(numbers))
                        break
                    except ValueError:
                        pass
        
        return rating, review_count
    
    def _extract_location(self, soup):
        """Extrai a localização do anúncio."""
        # Tentar diferentes seletores para a localização
        location_selectors = [
            'span[data-testid="listing-location"]',
            'div._9bezani',
            'div.atm_c8_exq9by5'
        ]
        
        for selector in location_selectors:
            location_elem = soup.select_one(selector)
            if location_elem:
                return location_elem.get_text(strip=True)
        
        return None
    
    def _extract_features(self, soup):
        """Extrai características do imóvel (quartos, banheiros, etc.)."""
        features = {}
        
        # Tentar extrair as características principais
        feature_selectors = [
            'div[data-testid="listing-features"]',
            'div._1dotkqq',
            'div.atm_cs_1pkprkl'
        ]
        
        for selector in feature_selectors:
            feature_container = soup.select_one(selector)
            if feature_container:
                feature_text = feature_container.get_text(strip=True)
                
                # Tenta identificar padrões como "2 quartos", "1 banheiro", etc.
                import re
                rooms = re.search(r'(\d+)\s*quarto', feature_text)
                baths = re.search(r'(\d+)\s*banheiro', feature_text)
                beds = re.search(r'(\d+)\s*cama', feature_text)
                
                if rooms:
                    features['rooms'] = int(rooms.group(1))
                if baths:
                    features['bathrooms'] = int(baths.group(1))
                if beds:
                    features['beds'] = int(beds.group(1))
                
                break
        
        return features
    
    def _extract_timestamp_from_filename(self, filename):
        """Extrai o timestamp do nome do arquivo."""
        # Padrão esperado: airbnb_ROOMID_YYYY-MM-DDTHH-MM-SS.html
        try:
            import re
            match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})', filename)
            if match:
                timestamp_str = match.group(1)
                # Converter para formato ISO 8601
                timestamp_str = timestamp_str.replace('-', ':', 2)
                return timestamp_str
        except Exception:
            pass
        
        # Fallback: usar a data de modificação do arquivo
        return datetime.fromtimestamp(os.path.getmtime(filename)).isoformat()
    
    def _extract_room_id_from_filename(self, filename):
        """Extrai o ID do quarto do nome do arquivo."""
        # Padrão esperado: airbnb_ROOMID_YYYY-MM-DDTHH-MM-SS.html
        try:
            import re
            match = re.search(r'airbnb_(\d+)_', os.path.basename(filename))
            if match:
                return match.group(1)
        except Exception:
            pass
        
        return None

def main():
    """Função principal do programa."""
    parser = argparse.ArgumentParser(description='Extrai conteúdo de texto de arquivos HTML do Airbnb.')
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--input', help='Caminho para um arquivo HTML específico')
    input_group.add_argument('--input-dir', help='Diretório contendo arquivos HTML para processar')
    
    parser.add_argument('--output-dir', default='./extracted', help='Diretório para salvar os arquivos de saída')
    parser.add_argument('--format', choices=['json', 'text', 'both'], default='both', 
                       help='Formato de saída (json, text ou both)')
    
    args = parser.parse_args()
    
    extractor = AirbnbTextExtractor()
    
    if args.input:
        # Processar um único arquivo
        result = extractor.extract_from_file(args.input)
        
        if not result:
            print(f"Falha ao processar o arquivo {args.input}")
            return 1
        
        # Criar diretório de saída se não existir
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Nome base do arquivo (sem extensão)
        base_name = os.path.splitext(os.path.basename(args.input))[0]
        
        # Salvar resultado
        if args.format in ['json', 'both']:
            json_output_path = os.path.join(args.output_dir, f"{base_name}.json")
            with open(json_output_path, 'w', encoding='utf-8') as json_file:
                json.dump(result, json_file, ensure_ascii=False, indent=2)
            print(f"Arquivo JSON salvo em: {json_output_path}")
        
        if args.format in ['text', 'both']:
            text_output_path = os.path.join(args.output_dir, f"{base_name}.txt")
            with open(text_output_path, 'w', encoding='utf-8') as text_file:
                text_file.write(result["content"] if result["content"] else "")
            print(f"Arquivo de texto salvo em: {text_output_path}")
    
    else:
        # Processar um diretório
        count = extractor.process_directory(args.input_dir, args.output_dir)
        print(f"Processados {count} arquivos HTML de {args.input_dir} para {args.output_dir}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())