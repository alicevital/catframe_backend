# Roteador de Autenticação e Criação de Usuário (Ajustado com Reset de Senha)

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone # Adicionado datetime e timezone

# Ajustar imports para serem relativos dentro do pacote 'app'
from ..database import get_db
from ..models.user import User
# Importar schemas necessários, incluindo os novos PasswordResetRequest e PasswordReset
from ..schemas import UserCreate, UserResponse, Token, PasswordResetRequest, PasswordReset
from ..dependencies.security import (
    get_current_user,
    create_access_token,
    verify_password,
    get_password_hash,
    create_password_reset_token # Função para gerar token de reset
)
from ..config import settings # Importar configurações

router = APIRouter(
    prefix="/auth", # Definir prefixo aqui para todas as rotas de autenticação
    tags=["Authentication"]
)

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

# --- Rotas de Recuperação de Senha --- 

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def request_password_recovery(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Inicia o processo de recuperação de senha para um usuário (pelo username).
    Gera um token de reset e (em um cenário real) o enviaria por email.
    Retorna uma mensagem genérica por segurança, mas inclui o token para teste.
    """
    user = db.query(User).filter(User.username == payload.username).first()

    # Resposta genérica para não revelar se o usuário existe
    success_message = {"message": "Se um usuário com esse nome existir, um token de recuperação foi gerado e (em produção) seria enviado por email."}

    if user:
        # Gerar token e definir expiração (ex: 1 hora)
        token = create_password_reset_token(payload.username)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        # Salvar token e expiração no usuário
        user.reset_password_token = token
        user.reset_password_token_expires_at = expires_at
        db.commit()

        # !! IMPORTANTE !!
        # Em produção, aqui você enviaria o 'token' por email para o usuário.
        # NÃO retorne o token na resposta da API em produção.
        # Para fins de teste/demonstração, vamos incluir o token na resposta.
        # Remova isso antes de ir para produção!
        success_message["reset_token_for_testing"] = token # APENAS PARA TESTE

    return success_message

@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(payload: PasswordReset, db: Session = Depends(get_db)):
    """
    Redefine a senha do usuário usando o token de recuperação.
    """
    # Encontrar usuário pelo token
    user = db.query(User).filter(User.reset_password_token == payload.token).first()

    # Verificar se o token é válido e não expirou
    if not user or user.reset_password_token_expires_at is None or user.reset_password_token_expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado"
        )

    # Redefinir a senha
    user.hashed_password = get_password_hash(payload.new_password)
    
    # Limpar o token de reset para que não possa ser reutilizado
    user.reset_password_token = None
    user.reset_password_token_expires_at = None
    
    db.commit()

    return {"message": "Senha redefinida com sucesso."}

# --- Fim das Rotas de Recuperação de Senha ---

# Opcional: Rota para obter informações do usuário logado
@router.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Retorna os dados do usuário atualmente autenticado."""
    return current_user