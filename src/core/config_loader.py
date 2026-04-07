import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .config import Config, AppConfig, DatabaseConfig, RedisConfig


class ConfigLoader:
    """Loads configuration from various sources with precedence order."""
    
    def __init__(self):
        self._config_cache: Optional[Config] = None
    
    def load_config(self, config_file: Optional[str] = None) -> Config:
        """Load configuration with precedence: env vars > config file > defaults."""
        if self._config_cache is not None:
            return self._config_cache
        
        # Start with defaults
        config_data = self._get_default_config()
        
        # Override with config file if provided
        if config_file:
            file_config = self._load_config_file(config_file)
            config_data = self._merge_configs(config_data, file_config)
        
        # Override with environment variables
        env_config = self._load_env_config()
        config_data = self._merge_configs(config_data, env_config)
        
        # Create config objects
        self._config_cache = self._create_config_objects(config_data)
        return self._config_cache
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration as dictionary."""
        return {
            "app": {
                "debug": False,
                "secret_key": "dev-secret-key",
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 1,
                "log_level": "INFO",
                "cors_origins": ["*"]
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "myapp",
                "username": "user",
                "password": "password",
                "pool_size": 10,
                "max_overflow": 20,
                "pool_timeout": 30,
                "pool_recycle": 3600,
                "echo": False
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "database": 0,
                "password": None,
                "max_connections": 10,
                "socket_timeout": 5,
                "socket_connect_timeout": 5,
                "retry_on_timeout": True
            }
        }
    
    def _load_config_file(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON or YAML file."""
        file_path = Path(config_file)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        with open(file_path, 'r') as f:
            if file_path.suffix.lower() in ['.yml', '.yaml']:
                return yaml.safe_load(f) or {}
            elif file_path.suffix.lower() == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {file_path.suffix}")
    
    def _load_env_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        env_config = {"app": {}, "database": {}, "redis": {}}
        
        # App config from env
        if os.getenv("APP_DEBUG"):
            env_config["app"]["debug"] = os.getenv("APP_DEBUG").lower() == "true"
        if os.getenv("APP_SECRET_KEY"):
            env_config["app"]["secret_key"] = os.getenv("APP_SECRET_KEY")
        if os.getenv("APP_HOST"):
            env_config["app"]["host"] = os.getenv("APP_HOST")
        if os.getenv("APP_PORT"):
            env_config["app"]["port"] = int(os.getenv("APP_PORT"))
        if os.getenv("APP_WORKERS"):
            env_config["app"]["workers"] = int(os.getenv("APP_WORKERS"))
        if os.getenv("APP_LOG_LEVEL"):
            env_config["app"]["log_level"] = os.getenv("APP_LOG_LEVEL")
        
        # Database config from env
        if os.getenv("DB_HOST"):
            env_config["database"]["host"] = os.getenv("DB_HOST")
        if os.getenv("DB_PORT"):
            env_config["database"]["port"] = int(os.getenv("DB_PORT"))
        if os.getenv("DB_NAME"):
            env_config["database"]["database"] = os.getenv("DB_NAME")
        if os.getenv("DB_USER"):
            env_config["database"]["username"] = os.getenv("DB_USER")
        if os.getenv("DB_PASSWORD"):
            env_config["database"]["password"] = os.getenv("DB_PASSWORD")
        
        # Redis config from env
        if os.getenv("REDIS_HOST"):
            env_config["redis"]["host"] = os.getenv("REDIS_HOST")
        if os.getenv("REDIS_PORT"):
            env_config["redis"]["port"] = int(os.getenv("REDIS_PORT"))
        if os.getenv("REDIS_DB"):
            env_config["redis"]["database"] = int(os.getenv("REDIS_DB"))
        if os.getenv("REDIS_PASSWORD"):
            env_config["redis"]["password"] = os.getenv("REDIS_PASSWORD")
        
        return env_config
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _create_config_objects(self, config_data: Dict[str, Any]) -> Config:
        """Create typed config objects from dictionary data."""
        app_config = AppConfig(**config_data.get("app", {}))
        db_config = DatabaseConfig(**config_data.get("database", {}))
        redis_config = RedisConfig(**config_data.get("redis", {}))
        
        return Config(
            app=app_config,
            database=db_config,
            redis=redis_config
        )
    
    def clear_cache(self):
        """Clear the cached configuration."""
        self._config_cache = None


# Global config loader instance
config_loader = ConfigLoader()


def get_config(config_file: Optional[str] = None) -> Config:
    """Get the application configuration."""
    return config_loader.load_config(config_file)
