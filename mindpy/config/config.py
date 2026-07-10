"""
Configuration management for MindPy.

Supports loading from YAML, JSON, TOML, and environment variables.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml
import toml
from dotenv import load_dotenv


class Config:
    """
    Configuration manager for MindPy.
    
    Supports loading configuration from multiple sources with
    environment variable overrides.
    """
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Optional path to configuration file
        """
        self._config: Dict[str, Any] = {}
        self._config_path = Path(config_path) if config_path else None
        self._load_env()
        
        if self._config_path and self._config_path.exists():
            self.load_file(self._config_path)
    
    def _load_env(self) -> None:
        """Load environment variables from .env file if present."""
        load_dotenv()
    
    def load_file(self, path: Union[str, Path]) -> None:
        """
        Load configuration from a file.
        
        Args:
            path: Path to the configuration file
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file does not exist
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        suffix = path.suffix.lower()
        
        if suffix == '.yaml' or suffix == '.yml':
            self._load_yaml(path)
        elif suffix == '.json':
            self._load_json(path)
        elif suffix == '.toml':
            self._load_toml(path)
        else:
            raise ValueError(f"Unsupported configuration format: {suffix}")
    
    def _load_yaml(self, path: Path) -> None:
        """Load configuration from YAML file."""
        with open(path, 'r') as f:
            self._config.update(yaml.safe_load(f) or {})
    
    def _load_json(self, path: Path) -> None:
        """Load configuration from JSON file."""
        import json
        with open(path, 'r') as f:
            self._config.update(json.load(f))
    
    def _load_toml(self, path: Path) -> None:
        """Load configuration from TOML file."""
        with open(path, 'r') as f:
            self._config.update(toml.load(f))
    
    def load_dict(self, config: Dict[str, Any]) -> None:
        """
        Load configuration from a dictionary.
        
        Args:
            config: Configuration dictionary
        """
        self._config.update(config)
    
    def get(
        self,
        key: str,
        default: Any = None,
        env_override: bool = True
    ) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            env_override: Whether to check environment variables
            
        Returns:
            Configuration value
        """
        if env_override:
            env_key = key.upper().replace('.', '_')
            env_value = os.getenv(env_key)
            if env_value is not None:
                return self._parse_env_value(env_value)
        
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def _parse_env_value(self, value: str) -> Any:
        """
        Parse environment variable value to appropriate type.
        
        Args:
            value: String value from environment
            
        Returns:
            Parsed value
        """
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        elif value.lower() == 'none':
            return None
        elif value.isdigit():
            return int(value)
        
        try:
            return float(value)
        except ValueError:
            pass
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.
        
        Args:
            section: Section name
            
        Returns:
            Configuration section dictionary
        """
        return self.get(section, default={})
    
    def save(self, path: Optional[Union[str, Path]] = None) -> None:
        """
        Save configuration to a file.
        
        Args:
            path: Optional path to save to (defaults to loaded path)
        """
        save_path = Path(path) if path else self._config_path
        
        if not save_path:
            raise ValueError("No path specified for saving configuration")
        
        suffix = save_path.suffix.lower()
        
        if suffix == '.yaml' or suffix == '.yml':
            with open(save_path, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False)
        elif suffix == '.json':
            import json
            with open(save_path, 'w') as f:
                json.dump(self._config, f, indent=2)
        elif suffix == '.toml':
            with open(save_path, 'w') as f:
                toml.dump(self._config, f)
        else:
            raise ValueError(f"Unsupported configuration format: {suffix}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as a dictionary."""
        return self._config.copy()
    
    def __getitem__(self, key: str) -> Any:
        """Get configuration value using dictionary syntax."""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set configuration value using dictionary syntax."""
        self.set(key, value)
    
    def __contains__(self, key: str) -> bool:
        """Check if configuration key exists."""
        return self.get(key) is not None
    
    def __repr__(self) -> str:
        return f"Config(path={self._config_path}, keys={len(self._config)})"
