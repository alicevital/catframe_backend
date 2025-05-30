# Models ajustados com relacionamentos e constraints

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database import Base # Import relativo corrigido

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False) # Adicionado limite e nullable
    hashed_password = Column(String(255), nullable=False) # Adicionado limite e nullable
    is_admin = Column(Boolean, default=False)

    # Relacionamento com Comment
    comments = relationship("Comment", back_populates="user")

