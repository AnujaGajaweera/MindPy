"""
Base LLM provider abstraction for MindPy.

Provides the interface for all LLM providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class MessageRole(Enum):
    """Roles for LLM messages."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class LLMMessage:
    """
    A message in the LLM conversation.
    
    Contains role, content, and optional metadata.
    """
    role: MessageRole
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "role": self.role.value,
            "content": self.content
        }
    
    def __repr__(self) -> str:
        return f"LLMMessage({self.role.value}: {self.content[:50]}...)"


@dataclass
class LLMResponse:
    """
    Response from an LLM provider.
    
    Contains the generated text, metadata, and usage information.
    """
    content: str
    finish_reason: str = "stop"
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def total_cost(self) -> float:
        """Calculate total cost (placeholder)."""
        # TODO: Implement actual cost calculation
        return 0.0
    
    def __repr__(self) -> str:
        return f"LLMResponse({self.content[:50]}..., tokens={self.total_tokens})"


class LLMProvider(ABC):
    """
    Base class for LLM providers.
    
    All LLM providers must implement this interface.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        timeout: int = 30
    ):
        """
        Initialize the LLM provider.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
    
    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLM response
        """
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs
    ):
        """
        Generate a streaming response from the LLM.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Chunks of the response
        """
        pass
    
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Check if the provider supports streaming."""
        pass
    
    @abstractmethod
    def supports_function_calling(self) -> bool:
        """Check if the provider supports function calling."""
        pass
    
    def set_model(self, model: str) -> None:
        """
        Set the model to use.
        
        Args:
            model: Model name
        """
        self.model = model
    
    def set_temperature(self, temperature: float) -> None:
        """
        Set the sampling temperature.
        
        Args:
            temperature: Temperature (0.0 to 2.0)
        """
        self.temperature = max(0.0, min(2.0, temperature))
    
    def set_max_tokens(self, max_tokens: int) -> None:
        """
        Set the maximum tokens to generate.
        
        Args:
            max_tokens: Maximum tokens
        """
        self.max_tokens = max(1, max_tokens)
    
    def validate_messages(self, messages: List[LLMMessage]) -> bool:
        """
        Validate that messages are properly formatted.
        
        Args:
            messages: Messages to validate
            
        Returns:
            True if valid
        """
        if not messages:
            return False
        
        # Check that first message is system or user
        if messages[0].role not in [MessageRole.SYSTEM, MessageRole.USER]:
            return False
        
        return True
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model})"
