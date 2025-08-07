from typing import List
from pydantic import BaseSettings, Field, AnyHttpUrl, SecretStr, validator, root_validator, conint
# Emoji Key: ✅ success | ⚠️ warning | 🔴 error | 🟢 healthy | 🟠 shutdown | 🔑 DI | 🏓 health | 🔍 parse
class Settings(BaseSettings):
    civ_save_parser_version: str = Field(..., env="CIV_SAVE_PARSER_VERSION")
    mongodb_uri: SecretStr = Field(..., env="MONGO_URI")
    mongodb_db_name: str = Field("match_reporter", env="MONGO_DB")
    mongodb_timeout_ms: conint(ge=1000, le=30000) = Field(5000, env="MONGODB_TIMEOUT_MS")
    mongodb_max_pool_size: conint(ge=1, le=500) = Field(100, env="MONGODB_MAX_POOL_SIZE")
    mongodb_min_pool_size: conint(ge=0, le=100) = Field(0, env="MONGODB_MIN_POOL_SIZE")

    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: conint(gt=0, lt=65536) = Field(8000, env="API_PORT")

    allowed_origins: List[AnyHttpUrl] = Field(["http://localhost:3000"], env="ALLOWED_ORIGINS")
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("allowed_origins", pre=True)
    def _split_origins(cls, v):
        if isinstance(v, str):
            return [u.strip() for u in v.split(",") if u.strip()]
        return v

    @root_validator
    def _ensure_mongo_uri_scheme(cls, values):
        uri = values.get("mongodb_uri")
        if uri and not uri.get_secret_value().startswith(("mongodb://", "mongodb+srv://")):
            raise ValueError("MONGO_URI must start with 'mongodb://' or 'mongodb+srv://'")
        return values

settings = Settings()