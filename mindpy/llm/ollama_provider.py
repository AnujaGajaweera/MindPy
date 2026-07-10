"""
Ollama provider implementation for MindPy.
"""

from typing import List, Optional
import aiohttp

from mindpy.llm.provider import LLMProvider, LLMResponse, LLMMessage, MessageRole
from mindpy.logging import get_logger


class OllamaProvider(LLMProvider):
    """
    Ollama API provider.
    
    Implements the LLM provider interface for local Ollama models.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "llama2",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        timeout: int = 30
    ):
        """
        Initialize the Ollama provider.
        
        Args:
            api_key: Not used for Ollama (kept for interface compatibility)
            base_url: Base URL (defaults to http://localhost:11434)
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            timeout: Request timeout
        """
        super().__init__(
            api_key=api_key,
            base_url=base_url or "http://localhost:11434",
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
        Generate a response from Ollama.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters
            
        Returns:
            LLM response
        """
        if not self.validate_messages(messages):
            raise ValueError("Invalid messages format")
        
        # Convert messages to Ollama format
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": ollama_messages,
            "options": {
                "temperature": kwargs.get("temperature", self.temperature),
                "num_predict": kwargs.get("max_tokens", self.max_tokens)
            }
        }
        
        url = f"{self.base_url}/api/chat"
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {response.status} - {error_text}")
                
                data = await response.json()
        
        return self._parse_response(data)
    
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs
    ):
        """
        Generate a streaming response from Ollama.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters
            
        Yields:
            Chunks of the response
        """
        if not self.validate_messages(messages):
            raise ValueError("Invalid messages format")
        
        # Convert messages to Ollama format
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": ollama_messages,
            "options": {
                "temperature": kwargs.get("temperature", self.temperature),
                "num_predict": kwargs.get("max_tokens", self.max_tokens)
            },
            "stream": True
        }
        
        url = f"{self.base_url}/api/chat"
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {response.status} - {error_text}")
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line:
                        try:
                            import json
                            data = json.loads(line)
                            if 'message' in data and 'content' in data['message']:
                                yield data['message']['content']
                        except json.JSONDecodeError:
                            continue
    
    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return True
    
    def supports_function_calling(self) -> bool:
        """Check if function calling is supported."""
        return False  # Ollama doesn't support function calling natively
    
    def _parse_response(self, data: dict) -> LLMResponse:
        """
        Parse Ollama API response.
        
        Args:
            data: Response data
            
        Returns:
            LLM response
        """
        message = data.get('message', {})
        
        return LLMResponse(
            content=message.get('content', ''),
            finish_reason=data.get('done', True) and 'stop' or 'length',
            model=data.get('model', self.model),
            prompt_tokens=data.get('prompt_eval_count', 0),
            completion_tokens=data.get('eval_count', 0),
            total_tokens=data.get('prompt_eval_count', 0) + data.get('eval_count', 0),
            metadata={
                'done': data.get('done', True)
            }
        )
