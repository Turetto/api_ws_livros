from api.database import engine, Base_tabela
from api.modelo import Livro

def criar_banco_de_dados():
    """
    Função que cria a tabela definida como 'livros'.
    """

    print("Criando tabela no banco de dados...")    
    Base_tabela.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso.")

if __name__ == "__main__":    
    criar_banco_de_dados()