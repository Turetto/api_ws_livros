import sys
import os
from werkzeug.security import generate_password_hash 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.database import SessionLocal
from api.modelo import Usuario

def criar_usuario_admin():
    """
    Cria um usuário administrador lendo as credenciais das variáveis de ambiente.
    Este script é NÃO-INTERATIVO, ideal para rodar em servidores.
    """
    print("--- Tentando criar usuário Admin a partir de Variáveis de Ambiente ---")
    
    # 1. Lê o username e a senha das variáveis de ambiente
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

    # 2. Valida se as variáveis foram definidas no ambiente (ex: Heroku Config Vars)
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        print("Erro: As variáveis de ambiente ADMIN_USERNAME e ADMIN_PASSWORD devem ser definidas.")
        return

    db = SessionLocal()
    try:
        # 3. Verifica se o usuário já existe para evitar duplicatas
        usuario_existente = db.query(Usuario).filter_by(username=ADMIN_USERNAME).first()
        if usuario_existente:
            print(f"Usuário '{ADMIN_USERNAME}' já existe. Nenhuma ação foi tomada.")
            return

        # 4. Gera o hash da senha (prática segura)
        hashed_password = generate_password_hash(ADMIN_PASSWORD)
        
        # 5. Cria o novo usuário com os dados do ambiente
        novo_admin = Usuario(username=ADMIN_USERNAME, password=hashed_password)
        db.add(novo_admin)
        db.commit()
        
        print(f"Usuário admin '{ADMIN_USERNAME}' criado com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro durante a criação do admin: {e}")
        db.rollback()
    finally:
        # Garante que a sessão com o banco de dados seja fechada
        db.close()

if __name__ == "__main__":
    criar_usuario_admin()