from pathlib import Path

from pydantic import BaseModel, BaseSettings

ENV_PREFIX = "RTEST_"
BASE_DIR = Path(__file__).parent.absolute()


class TestRedisSettings(BaseModel):
    host: str
    port: int


class TestElasticSettings(BaseModel):
    host: str
    port: int


class TestRestSettings(BaseModel):
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


# see test-variables in docker-compose-test.yml
class TestSettings(BaseSettings):
    redis: TestRedisSettings
    elastic: TestElasticSettings
    rest: TestRestSettings

    class Config:
        env_nested_delimiter = "__"
        env_prefix = ENV_PREFIX
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = TestSettings()
