#!/usr/bin/env python3
"""
Script para testar a função log_execution da classe SupabaseUpdater
"""

from supabase_updater import SupabaseUpdater
import time

def main():
    """Função principal"""
    print("Testando função log_execution...")
    
    # Inicializar o atualizador
    try:
        updater = SupabaseUpdater()
        print("Supabase inicializado com sucesso")
    except Exception as e:
        print(f"Erro ao inicializar Supabase: {str(e)}")
        return
    
    # Simular dados para o log
    service_time = 123.45  # segundos
    rooms_ids = [45592704, 684243789461931776]  # IDs dos quartos processados
    success_count = 2  # Número de quartos processados com sucesso
    total_count = 2  # Número total de quartos processados
    
    print(f"Registrando log com os seguintes dados:")
    print(f"  Tempo de execução: {service_time:.2f} segundos")
    print(f"  Quartos processados: {rooms_ids}")
    print(f"  Taxa de sucesso: {success_count}/{total_count}")
    
    # Registrar o log
    try:
        result = updater.log_execution(
            service_time=service_time,
            rooms_ids=rooms_ids,
            success_count=success_count,
            total_count=total_count
        )
        
        if result.get('success'):
            print("✅ Log registrado com sucesso!")
        else:
            print(f"❌ Falha ao registrar log: {result.get('error', 'Erro desconhecido')}")
    except Exception as e:
        print(f"❌ Exceção ao registrar log: {str(e)}")

if __name__ == "__main__":
    main()