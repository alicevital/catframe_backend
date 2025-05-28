from sqlalchemy import Column, Integer, String, Text
from database import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    photo = Column(String)
    duration = Column(String)
    release_year = Column(Integer)
    description = Column(Text)
    banner_url = Column(String)
    director = Column(String)
    genre = Column(String)