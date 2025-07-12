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
    sms_sender: str
    sms_api_key: str
    sms_callback_url: str = "https://sharquniversity.amocrm.ru/api/v4/leads/callback"

    amo_crm_base_url: str = "https://sharquniversity.amocrm.ru/api/v4"
    amo_crm_token: str

    passport_data_base_url: str
    passport_data_username: str
    passport_data_password: str

    # Documentation authentication
    docs_username: str = "admin"
    docs_password: str = "admin123"

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def connection_string(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def amo_crm_config(self):
        return {
            "base_url": self.amo_crm_base_url,
            "token": self.amo_crm_token,
            "first_create_pipline_id": 9646446,
            "first_create_status_id": 76961026,
            "lead_accepted_pipline_id": 9646446,
            "lead_accepted_status_id": 76961538,
            "lead_rejected_pipline_id": 9646446,
            "lead_rejected_status_id": 76961610,
        }


settings = Settings()
