# Models ajustados com relacionamentos, constraints e campos para reset de senha

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from ..database import Base # Import relativo corrigido
from typing import Optional
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    
    # Campos para Reset de Senha
    reset_password_token: Optional[str] = Column(String(255), unique=True, index=True, nullable=True)
    reset_password_token_expires_at: Optional[datetime.datetime] = Column(DateTime(timezone=True), nullable=True)

    # Relacionamento com Comment
    # Usar string para evitar import circular se Comment importar User também
    comments = relationship("Comment", back_populates="user")