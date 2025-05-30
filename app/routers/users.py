# Roteador para Usuários (Ajustado)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Ajustar imports para serem relativos dentro do pacote 'app'
from ..database import get_db
from ..models.user import User
from ..schemas import UserResponse # Importar do __init__.py dos schemas
from ..dependencies.security import get_admin_user # Dependência para verificar admin

router = APIRouter(
    prefix="/users", # Definir prefixo aqui
    tags=["Users"], # Manter tags
    responses={403: {"description": "Permissão negada"}} # Resposta padrão 403
)

@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user) # Apenas admin pode listar usuários
):
    """Lista todos os usuários registrados (requer privilégios de admin)."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user) # Apenas admin pode ver outros usuários por ID
):
    """Obtém os detalhes de um usuário específico pelo ID (requer privilégios de admin)."""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return user

# Adicionar funcionalidade para promover/rebaixar admin (opcional, mas útil)
@router.patch("/{user_id}/admin", response_model=UserResponse)
def toggle_admin_status(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user) # Apenas admin pode alterar status de admin
):
    """Alterna o status de administrador de um usuário (requer privilégios de admin)."""
    user_to_modify = db.query(User).filter(User.id == user_id).first()
    if user_to_modify is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    
    # Impede que um admin remova seu próprio status de admin por esta rota
    if user_to_modify.id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é possível alterar o próprio status de administrador por esta rota.")

    user_to_modify.is_admin = not user_to_modify.is_admin
    db.commit()
    db.refresh(user_to_modify)
    return user_to_modify

