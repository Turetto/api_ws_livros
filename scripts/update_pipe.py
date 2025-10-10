import sys
import os
import subprocess

# Adicionar o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Criando função para orquestrar atualização do pipeline
def run_pipeline():
    """
    Executa o pipeline completo: scraping e depois população do banco.
    """
    python_executable = sys.executable
    try:
        print("\n--- INICIANDO PIPELINE DE ATUALIZAÇÃO DE DADOS ---")

        # 1. Executa o Web Scraper 
        print("\n[PASSO 1/2] Executando o Web Scraper (Isso pode demorar)...")        
        subprocess.run([python_executable, "-m", "scripts.webscraper"], check=True)
        print("[PASSO 1/2] Web Scraper concluído com sucesso.")
        
        # 2. Executa a Carga no Banco 
        print("\n[PASSO 2/2] Executando a carga no banco de dados...")
        subprocess.run([python_executable, "-m", "scripts.popular_db"], check=True)
        print("[PASSO 2/2] Carga no banco de dados concluída com sucesso.")
        
        print("\n--- PIPELINE FINALIZADO COM SUCESSO ---")
        
    except Exception as e:
        print(f"\n ERRO NO PIPELINE: {e} ")

if __name__ == "__main__":
    run_pipeline()