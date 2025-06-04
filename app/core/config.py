from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # API Settings
    api_title: str = "Pokemon API"
    api_version: str = "0.1.0"
    api_description: str = "FastAPI Pokemon API with CI/CD"
    
    # Database Settings
    database_url: str = "postgresql://user:pass@localhost/dbname"
    database_echo: bool = False

    # Testing
    testing: bool = False
    test_database_url: Optional[str] = None
    
    # External APIs
    pokemon_api_base_url: str = "https://pokeapi.co/api/v2"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    @property
    def sync_database_url(self) -> str:
        """Convert async database URL to sync for Alembic"""
        if self.testing and self.test_database_url:
            return self.test_database_url.replace("postgresql+asyncpg://", "postgresql://")
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")


settings = Settings()