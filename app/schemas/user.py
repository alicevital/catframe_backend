from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False

class UserResponse(BaseModel):
    username: str
    is_admin: bool

    class Config:
        orm_mode = True