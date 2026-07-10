"""
Anthropic provider implementation for MindPy.
"""

from typing import List, Optional
import aiohttp

from mindpy.llm.provider import LLMProvider, LLMResponse, LLMMessage, MessageRole
from mindpy.logging import get_logger


class AnthropicProvider(LLMProvider):
    """
    Anthropic API provider.
    
    Implements the LLM provider interface for Anthropic's Claude API.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "claude-3-opus-20240229",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        timeout: int = 30
    ):
        """
        Initialize the Anthropic provider.
        
        Args:
            api_key: Anthropic API key
            base_url: Base URL (defaults to https://api.anthropic.com)
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            timeout: Request timeout
        """
        super().__init__(
            api_key=api_key,
            base_url=base_url or "https://api.anthropic.com",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout
        )
        self._logger = get_logger(__name__)
    
    async def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from Anthropic.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters
            
        Returns:
            LLM response
        """
        if not self.validate_messages(messages):
            raise ValueError("Invalid messages format")
        
        if not self.api_key:
            raise ValueError("API key is required for Anthropic provider")
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Convert messages to Anthropic format
        system_message = None
        anthropic_messages = []
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": anthropic_messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature)
        }
        
        if system_message:
            payload["system"] = system_message
        
        url = f"{self.base_url}/v1/messages"
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API error: {response.status} - {error_text}")
                
                data = await response.json()
        
        return self._parse_response(data)
    
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs
    ):
        """
        Generate a streaming response from Anthropic.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters
            
        Yields:
            Chunks of the response
        """
        if not self.validate_messages(messages):
            raise ValueError("Invalid messages format")
        
        if not self.api_key:
            raise ValueError("API key is required for Anthropic provider")
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Convert messages to Anthropic format
        system_message = None
        anthropic_messages = []
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": anthropic_messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "stream": True
        }
        
        if system_message:
            payload["system"] = system_message
        
        url = f"{self.base_url}/v1/messages"
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API error: {response.status} - {error_text}")
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            import json
                            data = json.loads(data_str)
                            if 'delta' in data and 'text' in data['delta']:
                                yield data['delta']['text']
                        except json.JSONDecodeError:
                            continue
    
    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return True
    
    def supports_function_calling(self) -> bool:
        """Check if function calling is supported."""
        return True
    
    def _parse_response(self, data: dict) -> LLMResponse:
        """
        Parse Anthropic API response.
        
        Args:
            data: Response data
            
        Returns:
            LLM response
        """
        return LLMResponse(
            content=data.get('content', [{}])[0].get('text', ''),
            finish_reason=data.get('stop_reason', 'stop'),
            model=data.get('model', self.model),
            prompt_tokens=data.get('usage', {}).get('input_tokens', 0),
            completion_tokens=data.get('usage', {}).get('output_tokens', 0),
            total_tokens=data.get('usage', {}).get('input_tokens', 0) + data.get('usage', {}).get('output_tokens', 0),
            metadata={}
        )
