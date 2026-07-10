"""
Tests for the AI system.
"""

import pytest
from mindpy.ai import Tool, ToolParameter, ToolPermission, ToolRegistry, ToolCall


class TestTool:
    """Test cases for Tool."""
    
    @pytest.mark.unit
    def test_tool_creation(self):
        """Test creating a tool."""
        tool = Tool(
            name="test_tool",
            description="A test tool",
            permission=ToolPermission.SAFE
        )
        
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.permission == ToolPermission.SAFE
    
    @pytest.mark.unit
    async def test_tool_execute(self):
        """Test executing a tool."""
        async def test_function():
            return "executed"
        
        tool = Tool(
            name="test_tool",
            description="Test",
            function=test_function
        )
        
        result = await tool.execute()
        
        assert result == "executed"
    
    @pytest.mark.unit
    def test_tool_get_schema(self):
        """Test getting tool schema."""
        parameters = [
            ToolParameter(
                name="param1",
                type="string",
                description="A parameter"
            )
        ]
        
        tool = Tool(
            name="test_tool",
            description="Test",
            parameters=parameters
        )
        
        schema = tool.get_schema()
        
        assert schema["name"] == "test_tool"
        assert "parameters" in schema


class TestToolRegistry:
    """Test cases for ToolRegistry."""
    
    @pytest.fixture
    def tool_registry(self):
        """Create a fresh tool registry for each test."""
        return ToolRegistry()
    
    @pytest.mark.unit
    def test_tool_registry_creation(self, tool_registry):
        """Test creating a tool registry."""
        assert tool_registry is not None
    
    @pytest.mark.unit
    def test_register_tool(self, tool_registry):
        """Test registering a tool."""
        tool = Tool(name="test", description="Test")
        tool_registry.register(tool)
        
        assert tool_registry.get_tool_count() == 1
    
    @pytest.mark.unit
    def test_get_tool(self, tool_registry):
        """Test getting a tool."""
        tool = Tool(name="test", description="Test")
        tool_registry.register(tool)
        
        retrieved = tool_registry.get_tool("test")
        
        assert retrieved is not None
        assert retrieved.name == "test"
    
    @pytest.mark.unit
    def test_unregister_tool(self, tool_registry):
        """Test unregistering a tool."""
        tool = Tool(name="test", description="Test")
        tool_registry.register(tool)
        
        success = tool_registry.unregister("test")
        
        assert success is True
        assert tool_registry.get_tool("test") is None
    
    @pytest.mark.unit
    def test_get_schemas(self, tool_registry):
        """Test getting all tool schemas."""
        tool = Tool(name="test", description="Test")
        tool_registry.register(tool)
        
        schemas = tool_registry.get_schemas()
        
        assert len(schemas) == 1
    
    @pytest.mark.unit
    def test_has_tool(self, tool_registry):
        """Test checking if a tool is registered."""
        tool = Tool(name="test", description="Test")
        tool_registry.register(tool)
        
        assert tool_registry.has_tool("test") is True
        assert tool_registry.has_tool("nonexistent") is False


class TestToolCall:
    """Test cases for ToolCall."""
    
    @pytest.mark.unit
    def test_tool_call_creation(self):
        """Test creating a tool call."""
        call = ToolCall(
            tool_name="test_tool",
            parameters={"param1": "value1"}
        )
        
        assert call.tool_name == "test_tool"
        assert call.parameters == {"param1": "value1"}
    
    @pytest.mark.unit
    def test_tool_call_execute(self):
        """Test executing a tool call."""
        async def test_function(param1):
            return f"Received: {param1}"
        
        tool = Tool(
            name="test_tool",
            description="Test",
            function=test_function,
            parameters=[
                ToolParameter(name="param1", type="string", description="Test")
            ]
        )
        
        call = ToolCall(
            tool_name="test_tool",
            parameters={"param1": "value1"}
        )
        
        registry = ToolRegistry()
        registry.register(tool)
        call.execute(registry)
        
        assert call.executed is True
        assert call.result == "Received: value1"
