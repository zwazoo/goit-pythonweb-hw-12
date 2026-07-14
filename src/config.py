from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    db_name: str
    db_user: str
    db_password: str
    db_domain: str
    db_port: int = 5432

    hash_algorithm: str = "HS256"
    hash_secret: str

    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int = 2525
    mail_server: str = "sandbox.smtp.mailtrap.io"

    pgadmin_email: str
    pgadmin_password: str


settings = Settings()
