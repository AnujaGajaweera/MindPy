"""
AI-powered bot example for MindPy.

This example demonstrates a bot that uses LLM integration
for decision-making and tool calling.
"""

import asyncio
from mindpy import Bot
from mindpy.llm import LLMManager, LLMMessage, MessageRole
from mindpy.ai import AIAgent, ToolRegistry, Tool, ToolParameter, ToolPermission, AgentContext
from mindpy.skills import SkillRegistry, Skill, SkillResult
from mindpy.logging import setup_logging, get_logger


# Define some tools for the AI
class MoveTool(Tool):
    """Tool for moving the bot."""
    
    def __init__(self, bot):
        super().__init__(
            name="move",
            description="Move the bot to a specific position",
            parameters=[
                ToolParameter(
                    name="x",
                    type="number",
                    description="X coordinate"
                ),
                ToolParameter(
                    name="y",
                    type="number",
                    description="Y coordinate"
                ),
                ToolParameter(
                    name="z",
                    type="number",
                    description="Z coordinate"
                )
            ],
            permission=ToolPermission.SAFE
        )
        self._bot = bot
    
    async def execute(self, **kwargs):
        """Execute the move tool."""
        from mindpy.navigation import Position
        
        target = Position(
            x=kwargs.get("x", 0),
            y=kwargs.get("y", 64),
            z=kwargs.get("z", 0)
        )
        
        # Placeholder for actual movement
        self._logger = get_logger(__name__)
        self._logger.info(f"Moving to {target}")
        
        return {"position": (target.x, target.y, target.z)}


class ChatTool(Tool):
    """Tool for sending chat messages."""
    
    def __init__(self, bot):
        super().__init__(
            name="chat",
            description="Send a chat message",
            parameters=[
                ToolParameter(
                    name="message",
                    type="string",
                    description="Message to send"
                )
            ],
            permission=ToolPermission.SAFE
        )
        self._bot = bot
    
    async def execute(self, **kwargs):
        """Execute the chat tool."""
        message = kwargs.get("message", "")
        
        await self._bot.chat(message)
        
        return {"message": message}


class GatherSkill(Skill):
    """A skill for gathering resources."""
    
    @property
    def name(self):
        return "gather"
    
    @property
    def description(self):
        return "Gather resources in the area"
    
    async def execute(self, context):
        """Execute the gather skill."""
        self.update_progress(0.5)
        await asyncio.sleep(1)  # Simulate gathering
        self.update_progress(1.0)
        
        return SkillResult(
            success=True,
            message="Gathered resources",
            data={"items_collected": 10}
        )
    
    async def pause(self):
        """Pause gathering."""
        pass
    
    async def resume(self):
        """Resume gathering."""
        pass
    
    async def cancel(self):
        """Cancel gathering."""
        pass


async def main():
    """Run the AI-powered bot."""
    setup_logging(level="INFO")
    logger = get_logger(__name__)
    
    # Create bot
    bot = Bot(
        host="localhost",
        port=25565,
        username="AIBot"
    )
    
    # Setup LLM manager (using a mock for demo)
    llm_manager = LLMManager()
    # In production, you would do:
    # llm_manager.setup_openai(api_key="your-key", model="gpt-4")
    
    # Setup tool registry
    tool_registry = ToolRegistry()
    tool_registry.register(MoveTool(bot))
    tool_registry.register(ChatTool(bot))
    
    # Setup skill registry
    skill_registry = SkillRegistry()
    skill_registry.register(GatherSkill())
    
    # Create AI agent
    system_prompt = """You are an AI assistant controlling a Minecraft bot. 
    You can move around, chat with players, and gather resources. 
    Be helpful and friendly."""
    
    ai_agent = AIAgent(llm_manager, tool_registry, system_prompt)
    
    logger.info("Starting AI-powered bot...")
    logger.info("The bot will use AI to make decisions.")
    
    try:
        await bot.connect()
        logger.info("Connected to server")
        
        # Example: Use AI to decide what to do
        context = AgentContext(
            position=(0, 64, 0),
            health=20.0,
            hunger=20.0,
            goals=["Explore", "Gather resources"]
        )
        
        # In production, this would use the LLM
        # decision = await ai_agent.decide(context, "What should I do?")
        logger.info("AI decision-making ready")
        
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await bot.disconnect()
        logger.info("Disconnected")


if __name__ == "__main__":
    asyncio.run(main())
