from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    name: str
    version: str
    environment: str


class SecurityConfig(BaseModel):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int


class DatabaseConfig(BaseModel):
    host: str
    port: str
    user: str
    password: str
    name: str


class CacheConfig(BaseModel):
    host: str
    port: str


class EnvConfig(BaseSettings):
    app_name: str = 'Learnify.edu'
    app_version: str = '1.0.0'
    environment: str = 'local'

    api_port: str = '8000'

    secret_key: str = 'e8a8b273b3104c3d9b4c0274bb85a1102e3b8a1c3df4209bb9274092b7c11d04'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 1

    postgres_host: str = 'database'
    postgres_port: str = '5432'
    postgres_user: str = 'postgres_admin'
    postgres_password: str = 'Pas5w0Rd'
    postgres_db: str = 'learnify_edu'

    redis_host: str = 'cache'
    redis_port: str = '6379'

    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )


env_config = EnvConfig()


def get_app_config() -> AppConfig:
    return AppConfig(
        name=env_config.app_name,
        version=env_config.app_version,
        environment=env_config.environment,
    )


def get_security_config() -> SecurityConfig:
    return SecurityConfig(
        secret_key=env_config.secret_key,
        algorithm=env_config.algorithm,
        access_token_expire_minutes=env_config.access_token_expire_minutes,
        refresh_token_expire_days=env_config.refresh_token_expire_days,
    )


def get_database_config() -> DatabaseConfig:
    return DatabaseConfig(
        host=env_config.postgres_host,
        port=env_config.postgres_port,
        user=env_config.postgres_user,
        password=env_config.postgres_password,
        name=env_config.postgres_db,
    )


db_config = get_database_config()


def get_database_url() -> str:
    return f'postgresql://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.name}'


def get_cache_config() -> CacheConfig:
    return CacheConfig(host=env_config.redis_host, port=env_config.redis_port)
