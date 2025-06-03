from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base 

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), index=True, nullable=False) # Adicionado limite e nullable
    photo = Column(String(700)) # Aumentado limite para URL
    duration = Column(Integer) # Alterado para Integer (minutos)
    release_year = Column(Integer, index=True) # Adicionado index
    description = Column(Text)
    banner_url = Column(String(700)) # Aumentado limite para URL
    director = Column(String(100), index=True) # Adicionado limite e index
    genre = Column(String(50), index=True) # Adicionado limite e index

    # Relacionamento com Comment
    comments = relationship("Comment", back_populates="movie")

