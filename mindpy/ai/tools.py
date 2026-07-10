"""
Tool calling system for MindPy AI.

Provides tool definitions, registry, and execution for AI tool calling.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import inspect


class ToolPermission(Enum):
    """Permission levels for tools."""
    SAFE = "safe"  # Can be called without restrictions
    REQUIRES_CONFIRMATION = "requires_confirmation"  # Requires user confirmation
    ADMIN_ONLY = "admin_only"  # Only for admin users
    DANGEROUS = "dangerous"  # Potentially harmful operations


@dataclass
class ToolParameter:
    """
    A parameter for a tool.
    
    Describes a parameter that a tool accepts.
    """
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None
    
    def __repr__(self) -> str:
        return f"ToolParameter({self.name}: {self.type})"


@dataclass
class Tool:
    """
    A tool that can be called by the AI.
    
    Represents a function or operation that the AI can invoke.
    """
    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)
    permission: ToolPermission = ToolPermission.SAFE
    function: Optional[Callable] = None
    
    async def execute(self, **kwargs) -> Any:
        """
        Execute the tool.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool result
        """
        if self.function is None:
            raise NotImplementedError(f"Tool {self.name} has no function defined")
        
        # Validate parameters
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                raise ValueError(f"Required parameter missing: {param.name}")
        
        # Execute the function
        if inspect.iscoroutinefunction(self.function):
            return await self.function(**kwargs)
        else:
            return self.function(**kwargs)
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the tool schema for LLM function calling.
        
        Returns:
            Tool schema dictionary
        """
        properties = {}
        required = []
        
        for param in self.parameters:
            param_schema = {
                "type": param.type,
                "description": param.description
            }
            
            if param.enum:
                param_schema["enum"] = param.enum
            if param.default is not None:
                param_schema["default"] = param.default
            
            properties[param.name] = param_schema
            
            if param.required:
                required.append(param.name)
        
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    
    def __repr__(self) -> str:
        return f"Tool({self.name}, permission={self.permission.value})"


@dataclass
class ToolCall:
    """
    A tool call made by the AI.
    
    Represents a specific invocation of a tool.
    """
    tool_name: str
    parameters: Dict[str, Any]
    result: Optional[Any] = None
    error: Optional[str] = None
    executed: bool = False
    
    def execute(self, tool_registry: 'ToolRegistry') -> None:
        """
        Execute the tool call.
        
        Args:
            tool_registry: Tool registry to get the tool from
        """
        tool = tool_registry.get_tool(self.tool_name)
        if not tool:
            self.error = f"Tool not found: {self.tool_name}"
            return
        
        try:
            import asyncio
            result = asyncio.run(tool.execute(**self.parameters))
            self.result = result
            self.executed = True
        except Exception as e:
            self.error = str(e)
    
    def __repr__(self) -> str:
        return f"ToolCall({self.tool_name}, executed={self.executed})"


class ToolRegistry:
    """
    Registry for AI tools.
    
    Manages tool registration, lookup, and execution.
    """
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """
        Register a tool.
        
        Args:
            tool: Tool to register
        """
        self._tools[tool.name] = tool
    
    def unregister(self, tool_name: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            tool_name: Tool name
            
        Returns:
            True if unregistered
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
            return True
        return False
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: Tool name
            
        Returns:
            Tool or None
        """
        return self._tools.get(tool_name)
    
    def get_all_tools(self) -> List[Tool]:
        """Get all registered tools."""
        return list(self._tools.values())
    
    def get_tools_by_permission(self, permission: ToolPermission) -> List[Tool]:
        """
        Get tools by permission level.
        
        Args:
            permission: Permission level
            
        Returns:
            List of tools
        """
        return [t for t in self._tools.values() if t.permission == permission]
    
    def get_safe_tools(self) -> List[Tool]:
        """Get all safe tools."""
        return self.get_tools_by_permission(ToolPermission.SAFE)
    
    def get_schemas(self) -> List[Dict[str, Any]]:
        """
        Get all tool schemas for LLM function calling.
        
        Returns:
            List of tool schemas
        """
        return [tool.get_schema() for tool in self._tools.values()]
    
    def has_tool(self, tool_name: str) -> bool:
        """Check if a tool is registered."""
        return tool_name in self._tools
    
    def clear(self) -> None:
        """Clear all tools."""
        self._tools.clear()
    
    def __repr__(self) -> str:
        return f"ToolRegistry(tools={len(self._tools)})"
