# Schemas Pydantic com validações e ajustes

from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional

# ========= User Schemas =========

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    # Removido is_admin daqui para segurança

class UserResponse(UserBase):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True # Alterado de orm_mode

# ========= Movie Schemas =========

class MovieBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    photo: Optional[HttpUrl] = None # Validar como URL
    duration: Optional[int] = Field(None, ge=0) # Duração em minutos, não negativa
    release_year: Optional[int] = Field(None, ge=1888) # Ano mínimo razoável
    description: Optional[str] = None
    banner_url: Optional[HttpUrl] = None # Validar como URL
    director: Optional[str] = Field(None, max_length=100)
    genre: Optional[str] = Field(None, max_length=50)

class MovieCreate(MovieBase):
    pass

class MovieUpdate(BaseModel): # Schema específico para PATCH
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    photo: Optional[HttpUrl] = None
    duration: Optional[int] = Field(None, ge=0)
    release_year: Optional[int] = Field(None, ge=1888)
    description: Optional[str] = None
    banner_url: Optional[HttpUrl] = None
    director: Optional[str] = Field(None, max_length=100)
    genre: Optional[str] = Field(None, max_length=50)

class MovieResponse(MovieBase):
    id: int

    class Config:
        from_attributes = True

# ========= Comment Schemas =========

class CommentBase(BaseModel):
    text: str = Field(..., min_length=1)

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    movie_id: int
    user_id: int
    user: UserResponse # Incluir dados do usuário (opcional, mas útil)

    class Config:
        from_attributes = True

# ========= Token Schema =========

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None



# ========= Password Reset Schemas =========

class PasswordResetRequest(BaseModel):
    username: str = Field(..., description="Nome de usuário para solicitar a redefinição de senha")

class PasswordReset(BaseModel):
    token: str = Field(..., description="Token recebido para redefinição de senha")
    new_password: str = Field(..., min_length=8, description="Nova senha desejada")

