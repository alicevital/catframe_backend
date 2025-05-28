from app.database import SessionLocal
from app.models.user import User
from app.dependencies.security import get_password_hash

def create_admin():
    db = SessionLocal()
    admin = User(
        username="admin",
        hashed_password=get_password_hash("senhaadmin"),
        is_admin=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print("Admin criado:", admin.username)

if __name__ == "__main__":
    create_admin()