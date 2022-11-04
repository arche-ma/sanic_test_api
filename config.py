from os import getenv

from dotenv import load_dotenv

load_dotenv()


class Config:
    HOST = getenv("HOST", "0.0.0.0")
    PORT = getenv("PORT", 8000)
    SECRET = getenv("SECRET", "my super secret key")
    POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD", "secret_password")
    POSTGRES_HOST = getenv("POSTGRES_HOST", "postgresql")
    POSTGRES_USER = getenv("POSTGRES_USER", "postgres")
    POSTGRES_DB = getenv("POSTGRES_DB", "postgres")
    DB_PORT = getenv("DB_PORT", "5432")

    @property
    def db_url(self):
        return (
            f"postgres://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            "{self.DB_PORT}/{self.POSTGRES_DB}"
        )


config = Config()
