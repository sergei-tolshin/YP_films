from pathlib import Path

from pydantic import BaseModel, BaseSettings

ENV_PREFIX = "AUTH_"
BASE_DIR = Path(__file__).parent.absolute()


class TestRedisSettings(BaseModel):
    host: str
    port: int


class TestPostgresSettings(BaseModel):
    host: str
    port: int
    database: str = "testdb"
    user: str
    password: str


class TestAuthSettings(BaseModel):
    host: str
    port: int
    prefix: str = "api"
    version: str = "v1"

    @property
    def root_url(self) -> str:
        return f"http://{self.host}:{self.port}/{self.prefix}"

    @property
    def service_url(self) -> str:
        return f"{self.root_url}/{self.version}"


class TestSettings(BaseSettings):
    redis_test: TestRedisSettings
    postgres_test: TestPostgresSettings
    auth_test: TestAuthSettings

    class Config:
        env_nested_delimiter = "__"
        env_prefix = ENV_PREFIX
        env_file = str(BASE_DIR) + "/.env"
        env_file_encoding = "utf-8"


settings = TestSettings()
