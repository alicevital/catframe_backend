from pydantic import BaseModel

class MovieCreate(BaseModel):
    name: str
    photo: str
    duration: str
    release_year: int
    description: str
    banner_url: str
    director: str
    genre: str

class MovieResponse(MovieCreate):
    id: int

    class Config:
        orm_mode = True