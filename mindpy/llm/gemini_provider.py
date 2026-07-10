"""
Google Gemini provider implementation for MindPy.
"""

from typing import List, Optional
import aiohttp

from mindpy.llm.provider import LLMProvider, LLMResponse, LLMMessage, MessageRole
from mindpy.logging import get_logger


class GeminiProvider(LLMProvider):
    """
    Google Gemini API provider.
    
    Implements the LLM provider interface for Google's Gemini API.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gemini-pro",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        timeout: int = 30
    ):
        """
        Initialize the Gemini provider.
        
        Args:
            api_key: Google API key
            base_url: Base URL (defaults to https://generativelanguage.googleapis.com)
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            timeout: Request timeout
        """
        super().__init__(
            api_key=api_key,
            base_url=base_url or "https://generativelanguage.googleapis.com",
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
        Generate a response from Gemini.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters
            
        Returns:
            LLM response
        """
        if not self.validate_messages(messages):
            raise ValueError("Invalid messages format")
        
        if not self.api_key:
            raise ValueError("API key is required for Gemini provider")
        
        # Convert messages to Gemini format
        system_instruction = None
        contents = []
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_instruction = msg.content
            else:
                role = "user" if msg.role == MessageRole.USER else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg.content}]
                })
        
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", self.temperature),
                "maxOutputTokens": kwargs.get("max_tokens", self.max_tokens)
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = system_instruction
        
        url = f"{self.base_url}/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Gemini API error: {response.status} - {error_text}")
                
                data = await response.json()
        
        return self._parse_response(data)
    
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs
    ):
        """
        Generate a streaming response from Gemini.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters
            
        Yields:
            Chunks of the response
        """
        if not self.validate_messages(messages):
            raise ValueError("Invalid messages format")
        
        if not self.api_key:
            raise ValueError("API key is required for Gemini provider")
        
        # Convert messages to Gemini format
        system_instruction = None
        contents = []
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_instruction = msg.content
            else:
                role = "user" if msg.role == MessageRole.USER else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg.content}]
                })
        
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", self.temperature),
                "maxOutputTokens": kwargs.get("max_tokens", self.max_tokens)
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = system_instruction
        
        url = f"{self.base_url}/v1beta/models/{self.model}:streamGenerateContent?key={self.api_key}"
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Gemini API error: {response.status} - {error_text}")
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            import json
                            data = json.loads(data_str)
                            if 'candidates' in data and len(data['candidates']) > 0:
                                candidate = data['candidates'][0]
                                if 'content' in candidate and 'parts' in candidate['content']:
                                    for part in candidate['content']['parts']:
                                        if 'text' in part:
                                            yield part['text']
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
        Parse Gemini API response.
        
        Args:
            data: Response data
            
        Returns:
            LLM response
        """
        candidate = data['candidates'][0]
        content = candidate.get('content', {})
        parts = content.get('parts', [])
        text = ''.join(part.get('text', '') for part in parts)
        
        usage_metadata = data.get('usageMetadata', {})
        
        return LLMResponse(
            content=text,
            finish_reason=candidate.get('finishReason', 'stop'),
            model=data.get('model', self.model),
            prompt_tokens=usage_metadata.get('promptTokenCount', 0),
            completion_tokens=usage_metadata.get('candidatesTokenCount', 0),
            total_tokens=usage_metadata.get('totalTokenCount', 0),
            metadata={}
        )
