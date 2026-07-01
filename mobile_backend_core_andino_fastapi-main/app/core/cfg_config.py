from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Ya no necesitamos DATABASE_URL porque usamos Firestore
    SECRET_KEY: str = "BancoRipley2026_FuerzaVentas_JWT_Seguro"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    PORT: int = 8003

    class Config:
        env_file = ".env"

settings = Settings()