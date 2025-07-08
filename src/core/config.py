from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    access_token_expire_minutes: int = 30
    access_secret_key: str
    algorithm: str = "HS256"

    sms_base_url: str = "https://notify.eskiz.uz/api"
    sms_sender: str = "boxa.devops@gmail.com"
    sms_api_key: str = "I93z0JAfwlHH0cbjlfeWPaWsvi0CqDpBzFE2uSEs"
    sms_callback_url: str = "http://localhost:8000/api/sms/callback"

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def connection_string(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
