"""
LLM manager for MindPy.

Manages LLM providers and provides a unified interface for AI interactions.
"""

from typing import Optional, Dict, List
from mindpy.llm.provider import LLMProvider, LLMResponse, LLMMessage, MessageRole
from mindpy.llm.openai_provider import OpenAIProvider
from mindpy.llm.anthropic_provider import AnthropicProvider
from mindpy.llm.gemini_provider import GeminiProvider
from mindpy.llm.ollama_provider import OllamaProvider
from mindpy.logging import get_logger


class LLMManager:
    """
    Manages LLM providers and AI interactions.
    
    Provides a unified interface for using different LLM providers.
    """
    
    def __init__(self):
        """Initialize the LLM manager."""
        self._providers: Dict[str, LLMProvider] = {}
        self._default_provider: Optional[str] = None
        self._logger = get_logger(__name__)
    
    def register_provider(self, name: str, provider: LLMProvider) -> None:
        """
        Register an LLM provider.
        
        Args:
            name: Provider name
            provider: LLM provider instance
        """
        self._providers[name] = provider
        self._logger.info(f"Registered LLM provider: {name}")
    
    def unregister_provider(self, name: str) -> bool:
        """
        Unregister an LLM provider.
        
        Args:
            name: Provider name
            
        Returns:
            True if unregistered
        """
        if name in self._providers:
            del self._providers[name]
            self._logger.info(f"Unregistered LLM provider: {name}")
            return True
        return False
    
    def get_provider(self, name: Optional[str] = None) -> Optional[LLMProvider]:
        """
        Get an LLM provider by name.
        
        Args:
            name: Provider name (uses default if None)
            
        Returns:
            LLM provider or None
        """
        if name is None:
            name = self._default_provider
        return self._providers.get(name)
    
    def set_default_provider(self, name: str) -> bool:
        """
        Set the default provider.
        
        Args:
            name: Provider name
            
        Returns:
            True if successful
        """
        if name in self._providers:
            self._default_provider = name
            return True
        return False
    
    async def generate(
        self,
        messages: List[LLMMessage],
        provider: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response using an LLM provider.
        
        Args:
            messages: List of conversation messages
            provider: Provider name (uses default if None)
            **kwargs: Additional parameters
            
        Returns:
            LLM response
        """
        llm_provider = self.get_provider(provider)
        if not llm_provider:
            raise ValueError(f"Provider not found: {provider}")
        
        return await llm_provider.generate(messages, **kwargs)
    
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        provider: Optional[str] = None,
        **kwargs
    ):
        """
        Generate a streaming response using an LLM provider.
        
        Args:
            messages: List of conversation messages
            provider: Provider name (uses default if None)
            **kwargs: Additional parameters
            
        Yields:
            Chunks of the response
        """
        llm_provider = self.get_provider(provider)
        if not llm_provider:
            raise ValueError(f"Provider not found: {provider}")
        
        if not llm_provider.supports_streaming():
            raise ValueError(f"Provider does not support streaming: {provider}")
        
        async for chunk in llm_provider.generate_stream(messages, **kwargs):
            yield chunk
    
    def setup_openai(
        self,
        api_key: str,
        model: str = "gpt-4",
        **kwargs
    ) -> None:
        """
        Setup OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model name
            **kwargs: Additional parameters
        """
        provider = OpenAIProvider(
            api_key=api_key,
            model=model,
            **kwargs
        )
        self.register_provider("openai", provider)
        if self._default_provider is None:
            self.set_default_provider("openai")
    
    def setup_anthropic(
        self,
        api_key: str,
        model: str = "claude-3-opus-20240229",
        **kwargs
    ) -> None:
        """
        Setup Anthropic provider.
        
        Args:
            api_key: Anthropic API key
            model: Model name
            **kwargs: Additional parameters
        """
        provider = AnthropicProvider(
            api_key=api_key,
            model=model,
            **kwargs
        )
        self.register_provider("anthropic", provider)
        if self._default_provider is None:
            self.set_default_provider("anthropic")
    
    def setup_gemini(
        self,
        api_key: str,
        model: str = "gemini-pro",
        **kwargs
    ) -> None:
        """
        Setup Gemini provider.
        
        Args:
            api_key: Google API key
            model: Model name
            **kwargs: Additional parameters
        """
        provider = GeminiProvider(
            api_key=api_key,
            model=model,
            **kwargs
        )
        self.register_provider("gemini", provider)
        if self._default_provider is None:
            self.set_default_provider("gemini")
    
    def setup_ollama(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama2",
        **kwargs
    ) -> None:
        """
        Setup Ollama provider.
        
        Args:
            base_url: Ollama base URL
            model: Model name
            **kwargs: Additional parameters
        """
        provider = OllamaProvider(
            base_url=base_url,
            model=model,
            **kwargs
        )
        self.register_provider("ollama", provider)
        if self._default_provider is None:
            self.set_default_provider("ollama")
    
    def get_providers(self) -> List[str]:
        """Get list of registered provider names."""
        return list(self._providers.keys())
    
    def has_provider(self, name: str) -> bool:
        """Check if a provider is registered."""
        return name in self._providers
    
    def __repr__(self) -> str:
        return f"LLMManager(providers={len(self._providers)}, default={self._default_provider})"
