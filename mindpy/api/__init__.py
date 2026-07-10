"""
REST API for MindPy.

Provides HTTP API for controlling bots remotely.
"""

from mindpy.api.server import APIServer
from mindpy.api.routes import bot_routes, inventory_routes, navigation_routes

__all__ = [
    "APIServer",
    "bot_routes",
    "inventory_routes",
    "navigation_routes",
]
