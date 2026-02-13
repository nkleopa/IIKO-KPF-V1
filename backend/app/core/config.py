from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    IIKO_HOST: str
    IIKO_LOGIN: str
    IIKO_PASSWORD: str

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/iiko_kpf"

    IIKO_DEPARTMENT_ID: str = "2fddc97b-9d0a-4afb-9940-5c551782519c"
    IIKO_DEPARTMENT_NAME: str = "СХ Воронеж 20-летия Октября"

    SYNC_HOUR: int = 3
    SYNC_MINUTE: int = 0

    @property
    def IIKO_BASE_URL(self) -> str:
        host = self.IIKO_HOST.rstrip("/")
        if not host.startswith("http"):
            host = f"https://{host}"
        return host

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
