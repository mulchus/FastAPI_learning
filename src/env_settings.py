from pydantic import BaseModel, Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


SETTINGS_MODEL_CONFIG = SettingsConfigDict(
    env_nested_delimiter='__',
    # Use case_sensitive=False to workaround pydantic_settings bug leading to traceback on env params parsing.
    case_sensitive=False,
    validate_default=True,
    extra="forbid",
    use_attribute_docstrings=True,
)


class RollbarEnvSettings(BaseModel):
    """Settings for send logs to rollbar."""

    TOKEN: str = ''
    ENVIRONMENT: str = Field(
        default='unidentified',
        examples=['FAPI_loc', 'FAPI_dev', 'FAPI_prod'],
    )
    """Settings of rollbar for all apps in development, staging and production environments.
    Сan't be mandatory, because it requires the mandatory use of a rollbar on the local.
    """


class AppEnvSettings(BaseSettings):
    """Settings for FastAPI app."""

    POSTGRES_DSN: PostgresDsn

    ROLLBAR: RollbarEnvSettings | None = None

    FASTAPI_DEBUG: bool = False
    """Should be disabled in production environment."""

    model_config = SETTINGS_MODEL_CONFIG
