"""
Simple bot example for MindPy.

This example demonstrates a basic bot that connects to a server
and responds to chat messages.
"""

import asyncio
from mindpy import Bot
from mindpy.events import EventBus, Event, EventTypes
from mindpy.logging import setup_logging, get_logger


async def main():
    """Run the simple bot."""
    # Setup logging
    setup_logging(level="INFO")
    logger = get_logger(__name__)
    
    # Create event bus
    event_bus = EventBus()
    
    # Create bot
    bot = Bot(
        host="localhost",
        port=25565,
        username="SimpleBot"
    )
    
    # Subscribe to chat events
    async def on_chat(event: Event):
        """Handle chat messages."""
        message = event.data.get("message", "")
        sender = event.data.get("sender", "Unknown")
        
        logger.info(f"Chat from {sender}: {message}")
        
        # Respond to greetings
        if message.lower() in ["hello", "hi", "hey"]:
            await bot.chat(f"Hi {sender}!")
        elif message.lower() == "status":
            await bot.chat(f"I'm running normally at {bot.get_position()}")
    
    event_bus.subscribe(EventTypes.CHAT_MESSAGE, on_chat)
    
    # Connect and run
    logger.info("Starting simple bot...")
    
    try:
        await bot.connect()
        logger.info("Connected to server")
        
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await bot.disconnect()
        logger.info("Disconnected")


if __name__ == "__main__":
    asyncio.run(main())
