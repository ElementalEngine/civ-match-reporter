from typing import List
from pydantic_settings import BaseSettings
from pydantic import (
    Field,
    AnyHttpUrl,
    SecretStr,
    validator,
    root_validator,
    conint,
    confloat,
)

# Emoji Key: ✅ success | ⚠️ warning | 🔴 error | 🟢 healthy | 🟠 shutdown | 🔑 DI | 🏓 health | 🔍 parse
class Settings(BaseSettings):
    # App / Parser
    reporting_backend_version: str = Field(..., env="REPORTING_BACKEND_VERSION")

    # MongoDB
    mongodb_uri: SecretStr = Field(..., env="MONGODB_URI")
    mongodb_db_name: str = Field("match_reporter", env="MONGO_DB_NAME")
    mongodb_timeout_ms: conint(ge=1000, le=30000) = Field(5000, env="MONGODB_TIMEOUT_MS")
    mongodb_max_pool_size: conint(ge=1, le=500) = Field(100, env="MONGODB_MAX_POOL_SIZE")
    mongodb_min_pool_size: conint(ge=0, le=100) = Field(0, env="MONGODB_MIN_POOL_SIZE")

    # API
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: conint(gt=0, lt=65536) = Field(8000, env="API_PORT")

    # CORS 
    allowed_origins: List[AnyHttpUrl] = Field(["http://localhost:3000"], env="ALLOWED_ORIGINS")

    # TrueSkill Environment
    ts_mu: confloat(gt=0) = Field(1250.0, env="TS_MU")
    ts_sigma: confloat(gt=0) = Field(150.0, env="TS_SIGMA")
    ts_beta: confloat(gt=0) = Field(70.0, env="TS_BETA")         
    ts_tau: confloat(ge=0) = Field(1.0, env="TS_TAU")             
    ts_draw_prob: confloat(ge=0, le=1) = Field(0.0, env="TS_DRAW_PROB")

    # Skill Display Parameters
    ts_sigma_free: confloat(ge=0) = Field(90.0, env="TS_SIGMA_FREE")
    ts_teamer_boost: float = Field(1.0, env="TS_TEAMER_BOOST")
    
    civ_save_parser_version: str = Field("0.1", env="CIV_SAVE_PARSER_VERSION")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    # Validators
    @validator("allowed_origins", pre=True)
    def _split_origins(cls, v):
        if isinstance(v, str):
            return [u.strip() for u in v.split(",") if u.strip()]
        return v

    @root_validator(skip_on_failure=True)
    def _ensure_mongo_uri_scheme(cls, values):
        uri = values.get("mongodb_uri")
        if uri and not uri.get_secret_value().startswith(("mongodb://", "mongodb+srv://")):
            raise ValueError("MONGO_URI must start with 'mongodb://' or 'mongodb+srv://'")
        return values

    @root_validator(skip_on_failure=True)
    def _validate_ts_consistency(cls, values):
        mu = values.get("ts_mu")
        sigma = values.get("ts_sigma")
        beta = values.get("ts_beta")

        # Basic sanity checks
        if sigma and mu and sigma >= mu:
            raise ValueError("TS_SIGMA should be much smaller than TS_MU (e.g., MU=1250, SIGMA=150).")
        if beta and sigma and not (0.3 * sigma <= beta <= 0.8 * sigma):
            pass
        return values


settings = Settings()