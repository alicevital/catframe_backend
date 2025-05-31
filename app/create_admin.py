from app.models.user import User
from app.models.movie import Movie
from app.models.comment import Comment

# Importar o necessário para a sessão e hashing
from app.database import SessionLocal, engine, Base
from app.dependencies.security import get_password_hash
from app.config import settings 

def create_admin():
    # Opcional: Criar tabelas se não existirem (útil para execução isolada)
    # Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Verificar se o admin já existe
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("Usuário 'admin' já existe.")
            return

        # Criar o admin
        admin_password = "admin"
        admin = User(
            username="admin",
            hashed_password=get_password_hash(admin_password),
            is_admin=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Usuário administrador 'admin' criado com sucesso. Lembre-se de alterar a senha padrão ('{admin_password}')!")
    except Exception as e:
        print(f"Erro ao criar administrador: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Tentando criar usuário administrador...")
    create_admin()

