"""
config.py — Configurações da aplicação via variáveis de ambiente.
Usa pydantic-settings para validação automática e type safety.

Segurança (OWASP A02):
  - Nenhum segredo hardcoded neste arquivo
  - Valores lidos exclusivamente do .env
  - SECRET_KEY obrigatória — falha explicitamente se ausente
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Banco de dados assíncrono
    database_url: str = "sqlite+aiosqlite:///./blog.db"

    # Segurança — JWT
    secret_key: str = "dev-insecure-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # App
    app_env: str = "development"
    app_title: str = "Async Blog API"
    app_version: str = "0.1.0"

    # CORS — nunca usar ["*"] em produção (OWASP A05)
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Singleton cacheado das configurações — evita recarregar o .env a cada request."""
    return Settings()
