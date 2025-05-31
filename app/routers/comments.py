# Roteador para Comentários (Ajustado)

from fastapi import APIRouter, Depends, HTTPException, status, Path, Body
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.comment import Comment
from ..models.movie import Movie # Para verificar se o filme existe
from ..models.user import User # Para dependência de usuário logado
from ..schemas import CommentCreate, CommentResponse # Importar do __init__.py dos schemas
from ..dependencies.security import get_current_user # Dependência para usuário logado

router = APIRouter(
    prefix="/movies/{movie_id}/comments", # Aninhar comentários sob filmes
    tags=["Comments"],
    responses={
        404: {"description": "Filme ou Comentário não encontrado"},
        403: {"description": "Permissão negada"}
    }
)

# Função auxiliar para verificar se o filme existe
def get_movie_or_404(movie_id: int, db: Session = Depends(get_db)) -> Movie:
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Filme com ID {movie_id} não encontrado")
    return movie

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    movie_id: int = Path(..., description="ID do filme ao qual adicionar o comentário"),
    comment: CommentCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    movie: Movie = Depends(get_movie_or_404) # Garante que o filme existe
):
    """Cria um novo comentário para um filme específico (requer autenticação)."""
    db_comment = Comment(**comment.dict(), user_id=current_user.id, movie_id=movie_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    # Carregar relacionamento para a resposta (se definido no schema)
    db.refresh(db_comment.user) 
    return db_comment

@router.get("/", response_model=List[CommentResponse])
def read_comments_for_movie(
    movie_id: int = Path(..., description="ID do filme para listar os comentários"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    movie: Movie = Depends(get_movie_or_404) # Garante que o filme existe
):
    """Lista todos os comentários para um filme específico."""
    comments = db.query(Comment).filter(Comment.movie_id == movie_id).order_by(Comment.id.desc()).offset(skip).limit(limit).all()
    # Carregar relacionamentos para a resposta (se definido no schema)
    for c in comments:
        db.refresh(c.user)
    return comments

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    movie_id: int = Path(..., description="ID do filme ao qual o comentário pertence"),
    comment_id: int = Path(..., description="ID do comentário a ser deletado"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deleta um comentário (requer ser o autor ou admin)."""
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.movie_id == movie_id).first()
    
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comentário não encontrado neste filme")
    
    # Verifica permissão: ou é o dono do comentário ou é admin
    if comment.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão negada para deletar este comentário")
    
    db.delete(comment)
    db.commit()
    return None

