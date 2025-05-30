# Ponto de Entrada Principal da API (Ajustado)

from fastapi import FastAPI

# Ajustar imports para serem relativos dentro do pacote 'app'
from .database import engine, Base
from .routers import auth, movies, users, comments
from .config import settings # Importar configurações

# Criar tabelas no banco de dados (se não existirem)
# Em produção, considere usar Alembic para migrações
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para gerenciamento de catálogo de filmes com autenticação e permissões.",
    version="1.1.0", # Versão atualizada
    docs_url="/docs",
    redoc_url="/redoc"
)

# Incluir roteadores
app.include_router(auth.router, prefix="/auth") # Movido prefixo para cá
app.include_router(movies.router) # Prefixo já definido no router
app.include_router(users.router) # Prefixo já definido no router
# O router de comments já tem o prefixo /movies/{movie_id}/comments
app.include_router(comments.router)

@app.get("/", tags=["Root"])
def read_root():
    """Endpoint raiz para verificar se a API está online."""
    return {"message": f"Bem-vindo à {settings.PROJECT_NAME}! Acesse /docs para a documentação."}

# Remover o bloco if __name__ == "__main__":
# A execução deve ser feita via uvicorn: uvicorn app.main:app --reload

