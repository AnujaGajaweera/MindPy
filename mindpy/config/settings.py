"""
Pydantic settings for MindPy configuration.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class BotSettings(BaseModel):
    """Bot-specific settings."""
    
    host: str = "localhost"
    port: int = 25565
    username: str = "MindPyBot"
    password: Optional[str] = None
    auth: str = "offline"  # offline, microsoft, mojang
    version: Optional[str] = None  # Auto-detect if None


class LoggingSettings(BaseModel):
    """Logging configuration settings."""
    
    level: str = "INFO"
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    rotation: str = "10 MB"
    retention: str = "30 days"
    console: bool = True
    file: Optional[str] = None
    json: bool = False


class AISettings(BaseModel):
    """AI and LLM configuration settings."""
    
    provider: str = "openai"
    model: str = "gpt-4"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 30


class MemorySettings(BaseModel):
    """Memory system settings."""
    
    working_memory_size: int = 10
    short_term_memory_size: int = 100
    long_term_memory_enabled: bool = True
    persistence_enabled: bool = True
    persistence_path: str = "data/memory"


class PluginSettings(BaseModel):
    """Plugin system settings."""
    
    plugin_paths: List[str] = Field(default_factory=lambda: ["plugins"])
    auto_discover: bool = True
    enabled_plugins: List[str] = Field(default_factory=list)
    disabled_plugins: List[str] = Field(default_factory=list)


class NavigationSettings(BaseModel):
    """Navigation and pathfinding settings."""
    
    pathfinding_timeout: int = 30
    max_path_length: int = 1000
    allow_dangerous_paths: bool = False
    break_blocks: bool = False
    place_blocks: bool = False


class Settings(BaseSettings):
    """
    Main settings class for MindPy.
    
    Uses pydantic-settings for environment variable support.
    """
    
    bot: BotSettings = Field(default_factory=BotSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    ai: AISettings = Field(default_factory=AISettings)
    memory: MemorySettings = Field(default_factory=MemorySettings)
    plugins: PluginSettings = Field(default_factory=PluginSettings)
    navigation: NavigationSettings = Field(default_factory=NavigationSettings)
    
    class Config:
        env_prefix = "MINDPY_"
        env_nested_delimiter = "__"
        case_sensitive = False
