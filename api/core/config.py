from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str
    DEBUG: bool = False
    VERSION: str = "0.1.0"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    DATABASE_URL: str

    class Config:
        env_file = ".env"  # Indica onde buscar as variáveis

# Instância única para ser usada no projeto
settings = Settings()
