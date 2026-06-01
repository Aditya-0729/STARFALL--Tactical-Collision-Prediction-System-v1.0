from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://starfall:starfall_secret@localhost:5432/starfall"
    nasa_api_key: str = "DEMO_KEY"
    celestrak_base_url: str = "https://celestrak.org"
    tle_gp_url: str = "https://celestrak.org/pub/TLE/active.txt"
    secret_key: str = "dev_secret_key"
    environment: str = "development"

    # Space-Track credentials (optional)
    spacetrack_user: str = ""
    spacetrack_pass: str = ""

    # Ingestion intervals (seconds)
    tle_ingest_interval: int = 3600
    neo_ingest_interval: int = 86400
    propagation_interval: int = 60
    ai_prediction_interval: int = 300

    class Config:
        env_file = ".env"
        extra = "ignore"        # ← this line ignores any extra fields in .env


settings = Settings()