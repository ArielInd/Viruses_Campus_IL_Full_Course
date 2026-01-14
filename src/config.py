from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    USERNAME: str = Field(alias="CAMPUS_IL_USERNAME")
    PASSWORD: str = Field(alias="CAMPUS_IL_PASSWORD")
    COURSE_URL: str = Field(alias="COURSE_URL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

config = Config()
