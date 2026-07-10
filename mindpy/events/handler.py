"""
Event handler decorator and utilities.
"""

from functools import wraps
from typing import Callable, Optional, Any
from mindpy.events.event import Event, EventPriority


class EventHandler:
    """
    Base class for event handlers.
    
    Subclasses can define handler methods that will be automatically
    registered with the event bus.
    """
    
    def __init__(self):
        """Initialize the event handler."""
        self._handlers: list[tuple[str, Callable]] = []
    
    def register_handlers(self, event_bus) -> None:
        """
        Register all handler methods with the event bus.
        
        Args:
            event_bus: The event bus to register with
        """
        for event_type, handler in self._handlers:
            event_bus.subscribe(event_type, handler)
    
    def unregister_handlers(self, event_bus) -> None:
        """
        Unregister all handler methods from the event bus.
        
        Args:
            event_bus: The event bus to unregister from
        """
        # Note: This would require tracking unsubscribe functions
        # For now, this is a placeholder
        pass


def event_handler(
    event_type: str,
    priority: EventPriority = EventPriority.NORMAL
) -> Callable:
    """
    Decorator to mark a method as an event handler.
    
    Args:
        event_type: The type of event to handle
        priority: The priority of this handler
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, event: Event, *args, **kwargs) -> Any:
            return await func(self, event, *args, **kwargs)
        
        wrapper.event_type = event_type
        wrapper.priority = priority
        wrapper.is_event_handler = True
        return wrapper
    
    return decorator


def sync_event_handler(
    event_type: str,
    priority: EventPriority = EventPriority.NORMAL
) -> Callable:
    """
    Decorator to mark a synchronous method as an event handler.
    
    Args:
        event_type: The type of event to handle
        priority: The priority of this handler
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, event: Event, *args, **kwargs) -> Any:
            return func(self, event, *args, **kwargs)
        
        wrapper.event_type = event_type
        wrapper.priority = priority
        wrapper.is_event_handler = True
        wrapper.is_sync = True
        return wrapper
    
    return decorator
