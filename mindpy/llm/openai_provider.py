"""
OpenAI provider implementation for MindPy.
"""

from typing import List, Optional
import aiohttp

from mindpy.llm.provider import LLMProvider, LLMResponse, LLMMessage, MessageRole
from mindpy.logging import get_logger


class OpenAIProvider(LLMProvider):
    """
    OpenAI API provider.
    
    Implements the LLM provider interface for OpenAI's API.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        timeout: int = 30
    ):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            base_url: Base URL (defaults to https://api.openai.com/v1)
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            timeout: Request timeout
        """
        super().__init__(
            api_key=api_key,
            base_url=base_url or "https://api.openai.com/v1",
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
        Generate a response from OpenAI.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters
            
        Returns:
            LLM response
        """
        if not self.validate_messages(messages):
            raise ValueError("Invalid messages format")
        
        if not self.api_key:
            raise ValueError("API key is required for OpenAI provider")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": [msg.to_dict() for msg in messages],
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens)
        }
        
        # Add function calling if supported
        if "functions" in kwargs:
            payload["functions"] = kwargs["functions"]
        
        url = f"{self.base_url}/chat/completions"
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error: {response.status} - {error_text}")
                
                data = await response.json()
        
        return self._parse_response(data)
    
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs
    ):
        """
        Generate a streaming response from OpenAI.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters
            
        Yields:
            Chunks of the response
        """
        if not self.validate_messages(messages):
            raise ValueError("Invalid messages format")
        
        if not self.api_key:
            raise ValueError("API key is required for OpenAI provider")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": [msg.to_dict() for msg in messages],
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "stream": True
        }
        
        url = f"{self.base_url}/chat/completions"
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error: {response.status} - {error_text}")
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            import json
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']
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
        Parse OpenAI API response.
        
        Args:
            data: Response data
            
        Returns:
            LLM response
        """
        choice = data['choices'][0]
        message = choice['message']
        
        return LLMResponse(
            content=message.get('content', ''),
            finish_reason=choice.get('finish_reason', 'stop'),
            model=data.get('model', self.model),
            prompt_tokens=data.get('usage', {}).get('prompt_tokens', 0),
            completion_tokens=data.get('usage', {}).get('completion_tokens', 0),
            total_tokens=data.get('usage', {}).get('total_tokens', 0),
            metadata={
                'function_call': message.get('function_call')
            }
        )
