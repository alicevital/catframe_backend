from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentResponse
from app.dependencies.security import get_current_user

router = APIRouter(tags=["Comments"])

@router.post("/", response_model=CommentResponse)
def create_comment(
    comment: CommentCreate,
    movie_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db_comment = Comment(**comment.dict(), user_id=user.id, movie_id=movie_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/{movie_id}", response_model=list[CommentResponse])
def get_comments(
    movie_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(Comment).filter(Comment.movie_id == movie_id).offset(skip).limit(limit).all()

@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    comment = db.query(Comment).get(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    
    if comment.user_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    db.delete(comment)
    db.commit()
    return {"message": "Comentário deletado"}