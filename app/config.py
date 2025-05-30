# Configurações da Aplicação usando Pydantic BaseSettings

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env, se existir
load_dotenv()

class Settings(BaseSettings):
    # Configurações do Banco de Dados
    # Use DATABASE_URL=sqlite:///./filmes_prod.db para produção SQLite
    # ou DATABASE_URL=postgresql://user:password@host:port/dbname para PostgreSQL
    DATABASE_URL: str = "sqlite:///./filmes_dev.db" # Default para dev

    # Configurações JWT
    SECRET_KEY: str = "seu_super_segredo_aqui_troque_isso"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Tokens expiram em 30 minutos

    # Configurações Adicionais (opcional)
    PROJECT_NAME: str = "CatFrame API"
    API_V1_STR: str = "/api/v1" # Prefixo para versionamento futuro

    class Config:
        # Permite carregar de um arquivo .env
        env_file = ".env"
        env_file_encoding = 'utf-8'
        # case_sensitive = True # Descomente se suas variáveis de ambiente diferenciam maiúsculas/minúsculas

# Instância única das configurações para ser importada em outros módulos
settings = Settings()

