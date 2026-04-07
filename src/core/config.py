from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    database: str = "myapp"
    username: str = "user"
    password: str = "password"
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        return cls(
            host=os.getenv('DB_HOST', cls.host),
            port=int(os.getenv('DB_PORT', str(cls.port))),
            database=os.getenv('DB_NAME', cls.database),
            username=os.getenv('DB_USER', cls.username),
            password=os.getenv('DB_PASSWORD', cls.password)
        )


@dataclass
class AppConfig:
    debug: bool = False
    secret_key: str = "dev-secret-key"
    database: DatabaseConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig.from_env()
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        return cls(
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            secret_key=os.getenv('SECRET_KEY', cls.secret_key),
            database=DatabaseConfig.from_env()
        )


config = AppConfig.from_env()
