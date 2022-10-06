from pydantic import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    database_url: str

    mail_username: str
    mail_password: str
    mail_port: int
    mail_server: str
    mail_tls: bool
    mail_ssl: bool
    mail_from: str
    mail_to: str

    aws_region_: str
    s3_bucket_name: str
    aws_access_key_id_: str
    aws_secret_access_key_: str

    csrf_secret_key: str
    csrf_cookie_samesite: str
    csrf_httponly: bool
    csrf_cookie_secure: bool

    origin_0: str
    environment: str

    # supertokens
    api_auth_url: str
    app_url: str
    connection_uri: str
    api_key: str
    cookie_secure: bool
    cookie_domain: str
    cookie_same_site: str

    google_client_id: str
    google_client_secret: str

    email_verification: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
