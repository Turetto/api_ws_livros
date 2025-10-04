from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from api.database import Base_tabela

# Definição do modelo da tabela do SQL
class Livro(Base_tabela):
    """
    Esta classe representa a tabela 'livros' no banco de dados.
    Cada atributo da classe corresponde a uma coluna na tabela.
    """
    
    __tablename__ = 'livros'

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False, index=True)
    preco = Column(Float, nullable=False)
    avaliacao = Column(String(50))
    disponibilidade = Column(String(100))
    url_imagem = Column(String(500))

    def __repr__(self):
        return f"<Livro(id={self.id}, titulo='{self.titulo}')>"
    
    def __str__(self):
        return f"Título: {self.titulo}, Preço: £{self.preco:.2f}"

