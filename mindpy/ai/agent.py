"""
AI agent for MindPy.

Provides AI decision-making and tool execution capabilities.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from mindpy.ai.tools import ToolRegistry, ToolCall, Tool
from mindpy.llm.provider import LLMProvider, LLMMessage, MessageRole
from mindpy.llm.manager import LLMManager
from mindpy.logging import get_logger


@dataclass
class AgentContext:
    """
    Context for the AI agent.
    
    Contains information about the current state and environment.
    """
    bot_state: Dict[str, Any] = field(default_factory=dict)
    inventory: Dict[str, Any] = field(default_factory=dict)
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    health: float = 20.0
    hunger: float = 20.0
    goals: List[str] = field(default_factory=list)
    recent_events: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "bot_state": self.bot_state,
            "inventory": self.inventory,
            "position": self.position,
            "health": self.health,
            "hunger": self.hunger,
            "goals": self.goals,
            "recent_events": self.recent_events
        }


class AIAgent:
    """
    AI agent for decision-making and tool execution.
    
    Uses an LLM to make decisions and execute tools.
    """
    
    def __init__(
        self,
        llm_manager: LLMManager,
        tool_registry: ToolRegistry,
        system_prompt: Optional[str] = None
    ):
        """
        Initialize the AI agent.
        
        Args:
            llm_manager: LLM manager for AI generation
            tool_registry: Tool registry for tool calling
            system_prompt: Optional system prompt
        """
        self._llm_manager = llm_manager
        self._tool_registry = tool_registry
        self._system_prompt = system_prompt or self._default_system_prompt()
        self._conversation_history: List[LLMMessage] = []
        self._logger = get_logger(__name__)
    
    def _default_system_prompt(self) -> str:
        """Get the default system prompt."""
        return """You are an AI assistant controlling a Minecraft bot. Your goal is to help the bot achieve its objectives by making intelligent decisions and using available tools.

You have access to various tools that allow you to interact with the Minecraft world. Use tools when appropriate to accomplish tasks.

Always consider the current context, available resources, and potential risks before taking action. Be efficient and prioritize safety."""
    
    async def decide(
        self,
        context: AgentContext,
        user_message: str = ""
    ) -> str:
        """
        Make a decision based on the current context.
        
        Args:
            context: Current agent context
            user_message: Optional user message
            
        Returns:
            AI decision/response
        """
        # Build messages
        messages = [
            LLMMessage(
                role=MessageRole.SYSTEM,
                content=self._system_prompt
            )
        ]
        
        # Add context
        context_message = f"Current context:\n{self._format_context(context)}"
        messages.append(LLMMessage(
            role=MessageRole.USER,
            content=context_message
        ))
        
        # Add user message if provided
        if user_message:
            messages.append(LLMMessage(
                role=MessageRole.USER,
                content=user_message
            ))
        
        # Add conversation history
        messages.extend(self._conversation_history)
        
        # Generate response
        response = await self._llm_manager.generate(messages)
        
        # Add to history
        self._conversation_history.append(LLMMessage(
            role=MessageRole.USER,
            content=context_message
        ))
        self._conversation_history.append(LLMMessage(
            role=MessageRole.ASSISTANT,
            content=response.content
        ))
        
        return response.content
    
    async def decide_with_tools(
        self,
        context: AgentContext,
        user_message: str = ""
    ) -> List[ToolCall]:
        """
        Make a decision and execute tools.
        
        Args:
            context: Current agent context
            user_message: Optional user message
            
        Returns:
            List of tool calls made
        """
        # Build messages with tool schemas
        messages = [
            LLMMessage(
                role=MessageRole.SYSTEM,
                content=self._system_prompt
            )
        ]
        
        # Add context
        context_message = f"Current context:\n{self._format_context(context)}"
        messages.append(LLMMessage(
            role=MessageRole.USER,
            content=context_message
        ))
        
        # Add user message if provided
        if user_message:
            messages.append(LLMMessage(
                role=MessageRole.USER,
                content=user_message
            ))
        
        # Get tool schemas
        tool_schemas = self._tool_registry.get_schemas()
        
        # Generate response with function calling
        response = await self._llm_manager.generate(
            messages,
            functions=tool_schemas
        )
        
        # Parse tool calls from response
        tool_calls = self._parse_tool_calls(response)
        
        # Execute tool calls
        for tool_call in tool_calls:
            tool_call.execute(self._tool_registry)
        
        return tool_calls
    
    def _format_context(self, context: AgentContext) -> str:
        """
        Format the agent context for the LLM.
        
        Args:
            context: Agent context
            
        Returns:
            Formatted context string
        """
        lines = []
        
        if context.position:
            lines.append(f"Position: {context.position}")
        
        lines.append(f"Health: {context.health:.1f}/20")
        lines.append(f"Hunger: {context.hunger:.1f}/20")
        
        if context.goals:
            lines.append(f"Goals: {', '.join(context.goals)}")
        
        if context.inventory:
            lines.append(f"Inventory: {context.inventory}")
        
        if context.recent_events:
            lines.append(f"Recent events: {', '.join(context.recent_events[-5:])}")
        
        return "\n".join(lines)
    
    def _parse_tool_calls(self, response) -> List[ToolCall]:
        """
        Parse tool calls from LLM response.
        
        Args:
            response: LLM response
            
        Returns:
            List of tool calls
        """
        # TODO: Implement proper tool call parsing
        # This depends on the specific LLM provider's response format
        return []
    
    def set_system_prompt(self, prompt: str) -> None:
        """
        Set the system prompt.
        
        Args:
            prompt: New system prompt
        """
        self._system_prompt = prompt
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self._conversation_history.clear()
    
    def get_history(self) -> List[LLMMessage]:
        """Get conversation history."""
        return self._conversation_history.copy()
    
    def __repr__(self) -> str:
        return f"AIAgent(history={len(self._conversation_history)})"
