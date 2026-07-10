"""
Tests for the configuration system.
"""

import pytest
import tempfile
import os
from mindpy.config import Config


class TestConfig:
    """Test cases for Config class."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
bot:
  username: TestBot
  host: localhost
  port: 25565

logging:
  level: INFO
  file: logs/mindpy.log
""")
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)
    
    @pytest.mark.unit
    def test_config_creation(self):
        """Test creating a config object."""
        config = Config()
        assert config is not None
    
    @pytest.mark.unit
    def test_config_load_yaml(self, temp_config_file):
        """Test loading config from YAML file."""
        config = Config(temp_config_file)
        assert config.get("bot.username") == "TestBot"
        assert config.get("bot.host") == "localhost"
        assert config.get("bot.port") == 25565
    
    @pytest.mark.unit
    def test_config_get(self):
        """Test getting config values."""
        config = Config()
        config.set("test.key", "value")
        assert config.get("test.key") == "value"
    
    @pytest.mark.unit
    def test_config_get_default(self):
        """Test getting config value with default."""
        config = Config()
        assert config.get("nonexistent.key", "default") == "default"
    
    @pytest.mark.unit
    def test_config_set(self):
        """Test setting config values."""
        config = Config()
        config.set("test.key", "value")
        assert config.get("test.key") == "value"
    
    @pytest.mark.unit
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = Config()
        config.set("test.key", "value")
        config_dict = config.to_dict()
        assert config_dict["test"]["key"] == "value"
    
    @pytest.mark.unit
    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "bot": {
                "username": "TestBot",
                "host": "localhost"
            }
        }
        config = Config()
        config.from_dict(config_dict)
        assert config.get("bot.username") == "TestBot"
