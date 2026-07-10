"""
Tests for the LLM system.
"""

import pytest
from mindpy.llm import LLMProvider, LLMMessage, MessageRole, LLMResponse


class TestLLMMessage:
    """Test cases for LLMMessage."""
    
    @pytest.mark.unit
    def test_message_creation(self):
        """Test creating an LLM message."""
        message = LLMMessage(
            role=MessageRole.USER,
            content="Hello, world!"
        )
        
        assert message.role == MessageRole.USER
        assert message.content == "Hello, world!"
    
    @pytest.mark.unit
    def test_message_to_dict(self):
        """Test converting message to dictionary."""
        message = LLMMessage(
            role=MessageRole.USER,
            content="Hello, world!"
        )
        
        message_dict = message.to_dict()
        
        assert message_dict["role"] == "user"
        assert message_dict["content"] == "Hello, world!"


class TestLLMResponse:
    """Test cases for LLMResponse."""
    
    @pytest.mark.unit
    def test_response_creation(self):
        """Test creating an LLM response."""
        response = LLMResponse(
            content="Hello back!",
            finish_reason="stop",
            model="test-model"
        )
        
        assert response.content == "Hello back!"
        assert response.finish_reason == "stop"
        assert response.model == "test-model"
    
    @pytest.mark.unit
    def test_response_total_tokens(self):
        """Test total tokens calculation."""
        response = LLMResponse(
            content="Test",
            prompt_tokens=10,
            completion_tokens=5
        )
        
        assert response.total_tokens == 15


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""
    
    async def generate(self, messages, **kwargs):
        """Generate a mock response."""
        return LLMResponse(
            content="Mock response",
            model="mock-model"
        )
    
    async def generate_stream(self, messages, **kwargs):
        """Generate a mock streaming response."""
        yield "Mock "
        yield "response"
    
    def supports_streaming(self):
        """Mock supports streaming."""
        return True
    
    def supports_function_calling(self):
        """Mock supports function calling."""
        return False


class TestLLMProvider:
    """Test cases for LLMProvider."""
    
    @pytest.fixture
    def provider(self):
        """Create a mock provider for each test."""
        return MockLLMProvider()
    
    @pytest.mark.unit
    def test_provider_creation(self, provider):
        """Test creating a provider."""
        assert provider is not None
    
    @pytest.mark.unit
    async def test_generate(self, provider):
        """Test generating a response."""
        messages = [LLMMessage(role=MessageRole.USER, content="Test")]
        response = await provider.generate(messages)
        
        assert response is not None
        assert response.content == "Mock response"
    
    @pytest.mark.unit
    async def test_generate_stream(self, provider):
        """Test generating a streaming response."""
        messages = [LLMMessage(role=MessageRole.USER, content="Test")]
        
        chunks = []
        async for chunk in provider.generate_stream(messages):
            chunks.append(chunk)
        
        assert len(chunks) == 2
        assert "".join(chunks) == "Mock response"
    
    @pytest.mark.unit
    def test_supports_streaming(self, provider):
        """Test checking streaming support."""
        assert provider.supports_streaming() is True
    
    @pytest.mark.unit
    def test_set_model(self, provider):
        """Test setting the model."""
        provider.set_model("new-model")
        assert provider.model == "new-model"
    
    @pytest.mark.unit
    def test_set_temperature(self, provider):
        """Test setting temperature."""
        provider.set_temperature(0.5)
        assert provider.temperature == 0.5
    
    @pytest.mark.unit
    def test_set_max_tokens(self, provider):
        """Test setting max tokens."""
        provider.set_max_tokens(1024)
        assert provider.max_tokens == 1024
    
    @pytest.mark.unit
    def test_validate_messages_valid(self, provider):
        """Test validating valid messages."""
        messages = [
            LLMMessage(role=MessageRole.SYSTEM, content="System"),
            LLMMessage(role=MessageRole.USER, content="User")
        ]
        
        assert provider.validate_messages(messages) is True
    
    @pytest.mark.unit
    def test_validate_messages_invalid(self, provider):
        """Test validating invalid messages."""
        messages = []
        assert provider.validate_messages(messages) is False
