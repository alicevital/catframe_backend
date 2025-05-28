from pydantic import BaseModel

class CommentCreate(BaseModel):
    text: str

class CommentResponse(CommentCreate):
    id: int
    user_id: int
    movie_id: int

    class Config:
        orm_mode = True