import sys
import os
from getpass import getpass
from api.database import SessionLocal
from api.modelo import Usuario

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def criar_usuario_admin():
    print("Criação do Usuário Admin:")
    db = SessionLocal()
    
    try:
        username = input("Digite o nome de usuário do admin: ")
        
        usuario_existente = db.query(Usuario).filter_by(username=username).first()
        if usuario_existente:
            print(f"Erro: O usuário '{username}' já existe.")
            return

        password = getpass("Digite a senha do admin: ")
 
        novo_admin = Usuario(username=username, password=password)       
        db.add(novo_admin)
        db.commit()
        
        print(f"Usuário admin '{username}' criado com sucesso!")
        
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    criar_usuario_admin()