"""
Mining bot example for MindPy.

This example demonstrates a bot that automatically mines ores
using the mining and navigation systems.
"""

import asyncio
from mindpy import Bot
from mindpy.events import EventBus, Event, EventTypes
from mindpy.mining import MiningPlanner, OreType
from mindpy.navigation import MovementController, Position
from mindpy.logging import setup_logging, get_logger


class MiningBot:
    """A bot that automatically mines ores."""
    
    def __init__(self, bot: Bot):
        """Initialize the mining bot."""
        self._bot = bot
        self._event_bus = EventBus()
        self._movement = MovementController()
        self._mining_planner = MiningPlanner()
        self._logger = get_logger(__name__)
        self._mining = False
    
    async def start_mining(self, target_ores: list):
        """Start mining for specific ores."""
        self._mining = True
        self._logger.info(f"Starting mining for: {target_ores}")
        
        while self._mining:
            # Get current position
            current_pos = self._bot.get_position()
            
            # Create mining plan
            plan = self._mining_planner.plan_mining(
                target_ores=target_ores,
                start_position=current_pos,
                available_tools=[]
            )
            
            self._logger.info(f"Mining plan: {len(plan.targets)} targets")
            
            # Execute mining plan
            for target in plan.targets[:5]:  # Limit to 5 targets for demo
                if not self._mining:
                    break
                
                # Move to target
                await self._movement.move_to(target.target.position)
                
                # Mine the block (placeholder)
                self._logger.info(f"Mining {target.target.block_type}")
                await asyncio.sleep(1)  # Simulate mining time
            
            # Wait before next cycle
            await asyncio.sleep(5)
    
    def stop_mining(self):
        """Stop mining."""
        self._mining = False
        self._logger.info("Stopping mining")


async def main():
    """Run the mining bot."""
    setup_logging(level="INFO")
    logger = get_logger(__name__)
    
    bot = Bot(
        host="localhost",
        port=25565,
        username="MiningBot"
    )
    
    mining_bot = MiningBot(bot)
    
    # Subscribe to chat for control
    async def on_chat(event: Event):
        """Handle chat messages."""
        message = event.data.get("message", "").lower()
        
        if message == "start mining":
            await mining_bot.start_mining([OreType.IRON, OreType.COAL])
        elif message == "stop mining":
            mining_bot.stop_mining()
    
    bot._event_bus.subscribe(EventTypes.CHAT_MESSAGE, on_chat)
    
    logger.info("Starting mining bot...")
    logger.info("Type 'start mining' or 'stop mining' in chat to control")
    
    try:
        await bot.connect()
        logger.info("Connected to server")
        
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        mining_bot.stop_mining()
    finally:
        await bot.disconnect()
        logger.info("Disconnected")


if __name__ == "__main__":
    asyncio.run(main())
