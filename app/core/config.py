from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    application_secret_key: str

    class Config:
        env_file = ".env"
        
        fields = {
            "postgres_password": {'exclude': True},
            "postgres_user": {'exclude': True},
            "postgres_db": {'exclude': True},
        }
        
settings = Settings()