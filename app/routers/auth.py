# Roteador de Autenticação e Criação de Usuário (Ajustado)

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

# Ajustar imports para serem relativos dentro do pacote 'app'
from ..database import get_db
from ..models.user import User
from ..schemas import UserCreate, UserResponse, Token # Importar do __init__.py dos schemas
from ..dependencies.security import (
    get_current_user,
    create_access_token,
    verify_password,
    get_password_hash
)
from ..config import settings # Importar configurações

router = APIRouter(tags=["Authentication"])

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Faz login do usuário e retorna um token JWT."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"}, # Padrão para 401
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registra um novo usuário comum (não admin)."""
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Nome de usuário já registrado"
        )
        
    hashed_password = get_password_hash(user.password)
    # Cria usuário sempre como não admin (is_admin=False por padrão no modelo)
    new_user = User(
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Opcional: Rota para obter informações do usuário logado
@router.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Retorna os dados do usuário atualmente autenticado."""
    return current_user

