# Roteador para Filmes (Ajustado)

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

# Ajustar imports para serem relativos dentro do pacote 'app'
from ..database import get_db
from ..models.movie import Movie
from ..models.user import User # Para dependência de admin
from ..schemas import MovieCreate, MovieResponse, MovieUpdate # Importar do __init__.py dos schemas
from ..dependencies.security import get_admin_user # Dependência para verificar admin

router = APIRouter(
    prefix="/movies", # Definir prefixo aqui
    tags=["Movies"], # Manter tags
    responses={404: {"description": "Filme não encontrado"}} # Resposta padrão 404
)

@router.post("/", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
def create_movie(
    movie: MovieCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user) # Apenas admin pode criar
):
    """Cria um novo filme no catálogo (requer privilégios de admin)."""
    db_movie = Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

@router.get("/", response_model=List[MovieResponse])
def read_movies(
    skip: int = 0,
    limit: int = 100,
    title: Optional[str] = Query(None, description="Filtrar por título (case-insensitive)"),
    director: Optional[str] = Query(None, description="Filtrar por diretor (case-insensitive)"),
    genre: Optional[str] = Query(None, description="Filtrar por gênero (case-insensitive)"),
    min_year: Optional[int] = Query(None, description="Filtrar por ano de lançamento mínimo"),
    max_year: Optional[int] = Query(None, description="Filtrar por ano de lançamento máximo"),
    db: Session = Depends(get_db)
):
    """Lista filmes com filtros e paginação."""
    query = db.query(Movie)
    
    # Filtros (usando ilike para case-insensitive onde aplicável)
    if title:
        query = query.filter(Movie.name.ilike(f"%{title}%"))
    if director:
        query = query.filter(Movie.director.ilike(f"%{director}%"))
    if genre:
        query = query.filter(Movie.genre.ilike(f"%{genre}%"))
    if min_year:
        query = query.filter(Movie.release_year >= min_year)
    if max_year:
        query = query.filter(Movie.release_year <= max_year)
    
    # Ordenação (ex: por ano de lançamento descendente)
    movies = query.order_by(Movie.release_year.desc(), Movie.name).offset(skip).limit(limit).all()
    return movies

@router.get("/{movie_id}", response_model=MovieResponse)
def read_movie(movie_id: int, db: Session = Depends(get_db)):
    """Obtém os detalhes de um filme específico pelo ID."""
    movie = db.query(Movie).filter(Movie.id == movie_id).first() # Usar filter().first() é mais explícito
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filme não encontrado")
    return movie

@router.put("/{movie_id}", response_model=MovieResponse)
def update_movie(
    movie_id: int,
    movie_data: MovieCreate, # PUT geralmente espera o objeto completo
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user) # Apenas admin pode atualizar
):
    """Atualiza completamente um filme existente (requer privilégios de admin)."""
    db_movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filme não encontrado")
    
    # Atualiza todos os campos com base nos dados recebidos
    for key, value in movie_data.dict().items():
        setattr(db_movie, key, value)
    
    db.commit()
    db.refresh(db_movie)
    return db_movie

@router.patch("/{movie_id}", response_model=MovieResponse)
def partial_update_movie(
    movie_id: int,
    movie_data: MovieUpdate, # Usar schema de Update para PATCH
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user) # Apenas admin pode atualizar
):
    """Atualiza parcialmente um filme existente (requer privilégios de admin)."""
    db_movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filme não encontrado")

    # Atualiza apenas os campos fornecidos (não None)
    update_data = movie_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_movie, key, value)

    db.commit()
    db.refresh(db_movie)
    return db_movie


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user) # Apenas admin pode deletar
):
    """Deleta um filme do catálogo (requer privilégios de admin)."""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filme não encontrado")
    
    db.delete(movie)
    db.commit()
    # Retorna 204 No Content, sem corpo na resposta
    return None

