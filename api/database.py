import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#habilitando o uso do postgre para utilizar o deploy no render

# Define a URL de conexão para o banco de dados SQLite e PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL', "sqlite:///./data/livraria.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Criar o motor do banco de dados.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}) 


# Criar uma sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar base de referência para o SQL
Base_tabela = declarative_base()