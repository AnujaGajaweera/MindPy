"""
REST API server for MindPy.

Provides HTTP API for controlling bots remotely using FastAPI.
"""

from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from mindpy.bot.manager import BotManager
from mindpy.logging import get_logger


class APIServer:
    """
    REST API server for MindPy.
    
    Provides HTTP endpoints for controlling bots remotely.
    """
    
    def __init__(
        self,
        bot_manager: BotManager,
        host: str = "0.0.0.0",
        port: int = 8000
    ):
        """
        Initialize the API server.
        
        Args:
            bot_manager: Bot manager instance
            host: Host to bind to
            port: Port to bind to
        """
        self._bot_manager = bot_manager
        self._host = host
        self._port = port
        self._app = FastAPI(title="MindPy API", version="0.1.0")
        self._logger = get_logger(__name__)
        
        self._setup_middleware()
        self._setup_routes()
    
    def _setup_middleware(self) -> None:
        """Setup CORS and other middleware."""
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self) -> None:
        """Setup API routes."""
        from mindpy.api.routes import setup_routes
        setup_routes(self._app, self._bot_manager)
    
    async def start(self) -> None:
        """Start the API server."""
        self._logger.info(f"Starting API server on {self._host}:{self._port}")
        
        config = uvicorn.Config(
            app=self._app,
            host=self._host,
            port=self._port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        return self._app
    
    def __repr__(self) -> str:
        return f"APIServer(host={self._host}, port={self._port})"
