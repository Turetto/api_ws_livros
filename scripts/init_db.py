from sqlalchemy import create_engine
from api.modelo import modelo_base # Importar o modelo da tabela do arquivo modelo.py

# Configuração do Banco de Dados
DATABASE_URL = "sqlite:///./data/livraria.db"

# Criar o motor do banco de dados
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def criar_banco_de_dados():
    """
    Função que cria a tabela definida como 'livros'.
    """

    print("Criando tabela no banco de dados...")    
    modelo_base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso.")

if __name__ == "__main__":    
    criar_banco_de_dados()