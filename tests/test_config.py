import os
import pytest
from unittest.mock import patch

from src.core.config import DatabaseConfig, AppConfig, config


class TestDatabaseConfig:
    def test_default_values(self):
        db_config = DatabaseConfig()
        assert db_config.host == "localhost"
        assert db_config.port == 5432
        assert db_config.database == "myapp"
        assert db_config.username == "user"
        assert db_config.password == "password"
    
    def test_custom_values(self):
        db_config = DatabaseConfig(
            host="custom-host",
            port=3306,
            database="custom-db",
            username="custom-user",
            password="custom-pass"
        )
        assert db_config.host == "custom-host"
        assert db_config.port == 3306
        assert db_config.database == "custom-db"
        assert db_config.username == "custom-user"
        assert db_config.password == "custom-pass"
    
    @patch.dict(os.environ, {
        'DB_HOST': 'env-host',
        'DB_PORT': '3306',
        'DB_NAME': 'env-db',
        'DB_USER': 'env-user',
        'DB_PASSWORD': 'env-pass'
    })
    def test_from_env_with_all_vars(self):
        db_config = DatabaseConfig.from_env()
        assert db_config.host == "env-host"
        assert db_config.port == 3306
        assert db_config.database == "env-db"
        assert db_config.username == "env-user"
        assert db_config.password == "env-pass"
    
    @patch.dict(os.environ, {'DB_HOST': 'partial-host'}, clear=True)
    def test_from_env_partial_vars(self):
        db_config = DatabaseConfig.from_env()
        assert db_config.host == "partial-host"
        assert db_config.port == 5432
        assert db_config.database == "myapp"
        assert db_config.username == "user"
        assert db_config.password == "password"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_no_vars(self):
        db_config = DatabaseConfig.from_env()
        assert db_config.host == "localhost"
        assert db_config.port == 5432
        assert db_config.database == "myapp"
        assert db_config.username == "user"
        assert db_config.password == "password"


class TestAppConfig:
    def test_default_values(self):
        app_config = AppConfig()
        assert app_config.debug is False
        assert app_config.secret_key == "dev-secret-key"
        assert isinstance(app_config.database, DatabaseConfig)
    
    def test_custom_values(self):
        custom_db = DatabaseConfig(host="custom")
        app_config = AppConfig(
            debug=True,
            secret_key="custom-secret",
            database=custom_db
        )
        assert app_config.debug is True
        assert app_config.secret_key == "custom-secret"
        assert app_config.database is custom_db
    
    @patch.dict(os.environ, {
        'DEBUG': 'true',
        'SECRET_KEY': 'env-secret',
        'DB_HOST': 'env-db-host'
    })
    def test_from_env_with_vars(self):
        app_config = AppConfig.from_env()
        assert app_config.debug is True
        assert app_config.secret_key == "env-secret"
        assert app_config.database.host == "env-db-host"
    
    @patch.dict(os.environ, {'DEBUG': 'false'}, clear=True)
    def test_from_env_debug_false(self):
        app_config = AppConfig.from_env()
        assert app_config.debug is False
    
    @patch.dict(os.environ, {'DEBUG': 'TRUE'}, clear=True)
    def test_from_env_debug_case_insensitive(self):
        app_config = AppConfig.from_env()
        assert app_config.debug is True
    
    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_no_vars(self):
        app_config = AppConfig.from_env()
        assert app_config.debug is False
        assert app_config.secret_key == "dev-secret-key"
        assert isinstance(app_config.database, DatabaseConfig)


class TestGlobalConfig:
    def test_config_is_app_config_instance(self):
        assert isinstance(config, AppConfig)
