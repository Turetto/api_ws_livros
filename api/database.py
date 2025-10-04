from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define a URL de conexão para o banco de dados SQLite.
DATABASE_URL = "sqlite:///./data/livraria.db"

# Criar o motor do banco de dados.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Criar uma sessão.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar base de referência para o SQL
Base_tabela = declarative_base()