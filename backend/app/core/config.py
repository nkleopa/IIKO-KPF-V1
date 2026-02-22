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

ROSTOV_BRANCHES: dict[str, str] = {
    "e3c72a11-a0fa-437b-824d-02ee8b920fe6": "СХ Ростов-на-Дону Пушкинская",
    "ab90d20e-4f77-4477-ba09-bd4fc77d4980": "СХ Ростов-на-Дону ТРЦ Галерея «Парк»",
    "b297248a-7ffe-479e-9e36-2741ae64425f": "СХ Ростов-на-Дону Большая Садовая",
    "103fd784-f3b5-40f9-93f4-100fe87bfd0a": "СХ Шахты Шевченко",
}
