from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.movie import Movie
from app.schemas.movie import MovieCreate, MovieResponse
from app.dependencies.security import get_admin_user
from app.models.user import User

router = APIRouter(tags=["Movies"])

@router.post("/", response_model=MovieResponse)
def create_movie(
    movie: MovieCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    db_movie = Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

@router.get("/", response_model=list[MovieResponse])
def read_movies(
    skip: int = 0,
    limit: int = 100,
    title: str = Query(None),
    director: str = Query(None),
    genre: str = Query(None),
    year: int = Query(None),
    min_year: int = Query(None),
    max_year: int = Query(None),
    db: Session = Depends(get_db)):

    query = db.query(Movie)
    
    # Filtros
    if title:
        query = query.filter(Movie.name.ilike(f"%{title}%"))
    if director:
        query = query.filter(Movie.director.ilike(f"%{director}%"))
    if genre:
        query = query.filter(Movie.genre.ilike(f"%{genre}%"))
    if year:
        query = query.filter(Movie.release_year == year)
    if min_year:
        query = query.filter(Movie.release_year >= min_year)
    if max_year:
        query = query.filter(Movie.release_year <= max_year)
    
    return query.order_by(Movie.release_year.desc()).offset(skip).limit(limit).all()

@router.get("/{movie_id}", response_model=MovieResponse)
def read_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).get(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    return movie

@router.put("/{movie_id}", response_model=MovieResponse)
def update_movie(
    movie_id: int,
    movie_data: MovieCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)):
    db_movie = db.query(Movie).get(movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    
    for key, value in movie_data.dict().items():
        setattr(db_movie, key, value)
    
    db.commit()
    db.refresh(db_movie)
    return db_movie

@router.delete("/{movie_id}")
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)):
    
    movie = db.query(Movie).get(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    
    db.delete(movie)
    db.commit()
    return {"message": "Filme deletado com sucesso"}