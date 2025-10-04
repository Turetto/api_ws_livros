import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.modelo import Livro, modelo_base

DATABASE_URL = "sqlite:///./data/livraria.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Criar Sessão 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def popular_banco_de_dados():
    """
    Lê os dados do arquivo livros.csv e os insere na tabela 'livros'
    no banco de dados 'livraria'
    """
    print("Iniciando a população do banco de dados...")
       
    db = SessionLocal()
    
    try:    
        with open('data/livros.csv', mode='r', encoding='utf-8') as file:            
            reader = csv.DictReader(file)
            
            livros_para_adicionar = []
            for row in reader:                
                livro_obj = Livro(
                    titulo=row['titulo'],
                    preco=float(row['preco']),
                    avaliacao=row['avaliacao'],
                    disponibilidade=row['disponibilidade'],
                    url_imagem=row['url_imagem']
                )
                livros_para_adicionar.append(livro_obj)
                        
            db.add_all(livros_para_adicionar)     
            db.commit()            
            
            total_livros = db.query(Livro).count()
            print(f"Banco de dados populado com sucesso! Total de livros: {total_livros}")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")        
        db.rollback()
    finally:        
        db.close()
        print("Sessão fechada.")

if __name__ == "__main__":
    popular_banco_de_dados()