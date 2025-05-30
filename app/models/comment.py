# Models ajustados com relacionamentos e constraints

from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base # Import relativo corrigido
from .user import User # Import para relacionamento
from .movie import Movie # Import para relacionamento

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False) # Adicionado nullable
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relacionamentos
    user = relationship("User", back_populates="comments")
    movie = relationship("Movie", back_populates="comments")

