import os
import pytest
from unittest.mock import patch
from src.core.config import DatabaseConfig, AppConfig


class TestDatabaseConfig:
    def test_default_values(self):
        config = DatabaseConfig()
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.database == "myapp"
        assert config.username == "user"
        assert config.password == "password"
    
    def test_custom_values(self):
        config = DatabaseConfig(
            host="remote-host",
            port=3306,
            database="testdb",
            username="testuser",
            password="testpass"
        )
        assert config.host == "remote-host"
        assert config.port == 3306
        assert config.database == "testdb"
        assert config.username == "testuser"
        assert config.password == "testpass"
    
    @patch.dict(os.environ, {
        'DB_HOST': 'env-host',
        'DB_PORT': '8080',
        'DB_NAME': 'env-db',
        'DB_USER': 'env-user',
        'DB_PASSWORD': 'env-pass'
    })
    def test_from_env_with_all_vars(self):
        config = DatabaseConfig.from_env()
        assert config.host == "env-host"
        assert config.port == 8080
        assert config.database == "env-db"
        assert config.username == "env-user"
        assert config.password == "env-pass"
    
    @patch.dict(os.environ, {'DB_HOST': 'partial-host'}, clear=True)
    def test_from_env_partial_vars(self):
        config = DatabaseConfig.from_env()
        assert config.host == "partial-host"
        assert config.port == 5432
        assert config.database == "myapp"
        assert config.username == "user"
        assert config.password == "password"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_no_vars(self):
        config = DatabaseConfig.from_env()
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.database == "myapp"
        assert config.username == "user"
        assert config.password == "password"


class TestAppConfig:
    def test_default_values(self):
        config = AppConfig()
        assert config.debug is False
        assert config.secret_key == "dev-secret-key"
        assert isinstance(config.database, DatabaseConfig)
    
    def test_custom_values(self):
        db_config = DatabaseConfig(host="custom-host")
        config = AppConfig(
            debug=True,
            secret_key="custom-key",
            database=db_config
        )
        assert config.debug is True
        assert config.secret_key == "custom-key"
        assert config.database.host == "custom-host"
    
    @patch.dict(os.environ, {
        'DEBUG': 'true',
        'SECRET_KEY': 'env-secret',
        'DB_HOST': 'env-db-host'
    })
    def test_from_env_with_vars(self):
        config = AppConfig.from_env()
        assert config.debug is True
        assert config.secret_key == "env-secret"
        assert config.database.host == "env-db-host"
    
    @patch.dict(os.environ, {'DEBUG': 'false'}, clear=True)
    def test_from_env_debug_false(self):
        config = AppConfig.from_env()
        assert config.debug is False
    
    @patch.dict(os.environ, {'DEBUG': 'TRUE'}, clear=True)
    def test_from_env_debug_case_insensitive(self):
        config = AppConfig.from_env()
        assert config.debug is True
    
    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_no_vars(self):
        config = AppConfig.from_env()
        assert config.debug is False
        assert config.secret_key == "dev-secret-key"
        assert isinstance(config.database, DatabaseConfig)
