"""
API routes for MindPy.

Provides HTTP endpoints for controlling bots.
"""

from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from mindpy.bot.manager import BotManager
from mindpy.logging import get_logger


# Request/Response Models
class BotCreateRequest(BaseModel):
    """Request model for creating a bot."""
    username: str
    host: str
    port: int = 25565


class BotResponse(BaseModel):
    """Response model for bot information."""
    bot_id: str
    username: str
    host: str
    port: int
    connected: bool


class PositionRequest(BaseModel):
    """Request model for position."""
    x: float
    y: float
    z: float


class ChatRequest(BaseModel):
    """Request model for chat messages."""
    message: str


def setup_routes(app: FastAPI, bot_manager: BotManager) -> None:
    """
    Setup all API routes.
    
    Args:
        app: FastAPI application
        bot_manager: Bot manager instance
    """
    logger = get_logger(__name__)
    
    @app.get("/")
    async def root() -> Dict[str, Any]:
        """Root endpoint."""
        return {
            "name": "MindPy API",
            "version": "0.1.0",
            "status": "running"
        }
    
    @app.get("/health")
    async def health() -> Dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy"}
    
    # Bot routes
    @app.post("/bots", response_model=BotResponse)
    async def create_bot(request: BotCreateRequest) -> BotResponse:
        """Create a new bot."""
        bot = bot_manager.create_bot(
            username=request.username,
            host=request.host,
            port=request.port
        )
        
        return BotResponse(
            bot_id=bot.bot_id,
            username=bot.username,
            host=bot.host,
            port=bot.port,
            connected=bot.is_connected()
        )
    
    @app.get("/bots", response_model=List[BotResponse])
    async def list_bots() -> List[BotResponse]:
        """List all bots."""
        bots = []
        for bot_id, bot in bot_manager._bots.items():
            bots.append(BotResponse(
                bot_id=bot_id,
                username=bot.username,
                host=bot.host,
                port=bot.port,
                connected=bot.is_connected()
            ))
        return bots
    
    @app.get("/bots/{bot_id}", response_model=BotResponse)
    async def get_bot(bot_id: str) -> BotResponse:
        """Get a specific bot."""
        bot = bot_manager.get_bot(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        return BotResponse(
            bot_id=bot.bot_id,
            username=bot.username,
            host=bot.host,
            port=bot.port,
            connected=bot.is_connected()
        )
    
    @app.post("/bots/{bot_id}/connect")
    async def connect_bot(bot_id: str) -> Dict[str, str]:
        """Connect a bot to the server."""
        bot = bot_manager.get_bot(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        await bot.connect()
        return {"status": "connected"}
    
    @app.post("/bots/{bot_id}/disconnect")
    async def disconnect_bot(bot_id: str) -> Dict[str, str]:
        """Disconnect a bot from the server."""
        bot = bot_manager.get_bot(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        await bot.disconnect()
        return {"status": "disconnected"}
    
    @app.delete("/bots/{bot_id}")
    async def delete_bot(bot_id: str) -> Dict[str, str]:
        """Delete a bot."""
        success = bot_manager.remove_bot(bot_id)
        if not success:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        return {"status": "deleted"}
    
    # Bot state routes
    @app.get("/bots/{bot_id}/position")
    async def get_position(bot_id: str) -> Dict[str, float]:
        """Get bot position."""
        bot = bot_manager.get_bot(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        pos = bot.get_position()
        return {"x": pos.x, "y": pos.y, "z": pos.z}
    
    @app.get("/bots/{bot_id}/health")
    async def get_health(bot_id: str) -> Dict[str, float]:
        """Get bot health."""
        bot = bot_manager.get_bot(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        return {"health": bot.get_health(), "max_health": 20.0}
    
    @app.get("/bots/{bot_id}/hunger")
    async def get_hunger(bot_id: str) -> Dict[str, float]:
        """Get bot hunger."""
        bot = bot_manager.get_bot(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        return {"hunger": bot.get_hunger(), "max_hunger": 20.0}
    
    @app.post("/bots/{bot_id}/chat")
    async def send_chat(bot_id: str, request: ChatRequest) -> Dict[str, str]:
        """Send a chat message."""
        bot = bot_manager.get_bot(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        await bot.chat(request.message)
        return {"status": "sent"}
    
    # Inventory routes
    @app.get("/bots/{bot_id}/inventory")
    async def get_inventory(bot_id: str) -> Dict[str, Any]:
        """Get bot inventory."""
        bot = bot_manager.get_bot(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        # TODO: Return actual inventory data
        return {"items": [], "size": 36}
    
    # Navigation routes
    @app.post("/bots/{bot_id}/move")
    async def move_bot(bot_id: str, request: PositionRequest) -> Dict[str, str]:
        """Move bot to position."""
        bot = bot_manager.get_bot(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        # TODO: Implement actual movement
        return {"status": "moving"}
    
    # WebSocket endpoint for real-time updates
    @app.websocket("/ws/{bot_id}")
    async def websocket_endpoint(websocket: WebSocket, bot_id: str):
        """WebSocket endpoint for real-time bot updates."""
        bot = bot_manager.get_bot(bot_id)
        if not bot:
            await websocket.close(code=1008)
            return
        
        await websocket.accept()
        
        try:
            while True:
                # Send bot state updates
                state = {
                    "position": {"x": 0, "y": 0, "z": 0},  # TODO: Actual position
                    "health": bot.get_health(),
                    "hunger": bot.get_hunger()
                }
                await websocket.send_json(state)
                
                # Wait a bit before next update
                import asyncio
                await asyncio.sleep(1)
        
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for bot {bot_id}")


def bot_routes(app: FastAPI, bot_manager: BotManager) -> None:
    """Setup bot-specific routes."""
    setup_routes(app, bot_manager)


def inventory_routes(app: FastAPI, bot_manager: BotManager) -> None:
    """Setup inventory-specific routes."""
    setup_routes(app, bot_manager)


def navigation_routes(app: FastAPI, bot_manager: BotManager) -> None:
    """Setup navigation-specific routes."""
    setup_routes(app, bot_manager)
