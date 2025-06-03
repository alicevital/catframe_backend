from fastapi import FastAPI

# @ Ajustar imports para serem relativos dentro do pacote 'app'
from .database import engine, Base
from .routers import auth, movies, users, comments
from .config import settings # Importar configurações

# Criar tabelas no banco de dados (se não existirem)
# Em produção, considere usar Alembic para migrações
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para gerenciamento de catálogo de filmes com autenticação e permissões.",
    version="1.1.0", 
    docs_url="/docs",
    redoc_url="/redoc"
)

# Incluir roteadores
app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(users.router) 
app.include_router(comments.router)

@app.get("/", tags=["Teste"])
def read_root():
    """Endpoint raiz para verificar se a API está online."""
    return {"message": f"Bem-vindo à {settings.PROJECT_NAME}! Acesse /docs para a documentação."}

# Remover o bloco if __name__ == "__main__":
# A execução deve ser feita via uvicorn: uvicorn app.main:app --reload

