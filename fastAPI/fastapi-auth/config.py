"""
config.py — Configurações via pydantic-settings.

Aula 1: Como iremos autenticar as nossas rotas (02:39)
Conceito central:
  Antes de implementar qualquer rota protegida, precisamos definir
  o contrato de segurança: qual algoritmo JWT, qual SECRET_KEY,
  qual tempo de expiração. Tudo via .env — nunca hardcoded (OWASP A02).
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Banco
    database_url: str = "sqlite+aiosqlite:///./auth.db"

    # JWT — núcleo da autenticação
    secret_key: str = "dev-key-change-in-production"
    algorithm: str  = "HS256"
    access_token_expire_minutes: int  = 30
    refresh_token_expire_days: int    = 7

    # App
    app_env: str     = "development"
    app_title: str   = "FastAPI Auth"
    app_version: str = "0.1.0"

    # CORS
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
    """Singleton cacheado — evita recarregar .env a cada request."""
    return Settings()
