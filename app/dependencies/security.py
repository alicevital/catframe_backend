# Funções de Segurança e Dependências (Ajustado com Reset de Senha)

import secrets # Para gerar tokens seguros
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Ajustar imports para serem relativos dentro do pacote 'app'
from ..database import get_db
from ..models.user import User
from ..schemas import TokenData # Importar do __init__.py dos schemas
from ..config import settings # Importar configurações centralizadas

# Contexto para hashing de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema OAuth2 para obter o token do header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token") # Ajustar tokenUrl para a rota correta

# --- Funções de Senha ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash armazenado."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera o hash bcrypt para uma senha."""
    return pwd_context.hash(password)

# --- Funções de Token JWT (Acesso) ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um novo token JWT de acesso."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Usa o tempo de expiração padrão das configurações
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# --- Funções de Token (Reset de Senha) ---

def create_password_reset_token(username: str) -> str:
    """
Gera um token seguro e aleatório para reset de senha.
    Poderia usar JWT também, mas um token aleatório simples armazenado no DB é comum.
    """
    # Gera um token seguro de 32 bytes em formato URL-safe
    return secrets.token_urlsafe(32)

# A validação do token será feita diretamente no endpoint de reset,
# comparando o token fornecido com o armazenado no DB e verificando a expiração.

# --- Dependências FastAPI ---

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Dependência para obter o usuário atual a partir do token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependência que verifica se o usuário atual é um administrador."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    return current_user

