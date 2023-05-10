from pydantic import BaseSettings


class TortoiseSettings(BaseSettings):
    db_url: str = "sqlite://./main_db.sqlite3"


class Settings(TortoiseSettings):
    pass


settings = Settings()
