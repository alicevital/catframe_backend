from fastapi import FastAPI
from app.routers import auth, movies, users, comments
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Catálogo de Filmes API",
    description="API para gerenciamento de catálogo de filmes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(auth.router, prefix="/auth")
app.include_router(movies.router, prefix="/movies")
app.include_router(users.router, prefix="/users")
app.include_router(comments.router, prefix="/comments")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)