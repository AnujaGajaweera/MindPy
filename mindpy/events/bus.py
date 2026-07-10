"""
Event bus implementation for MindPy.

Provides a central event bus for all communication between components.
"""

import asyncio
from collections import defaultdict
from typing import Callable, Dict, List, Set, Optional, Any
from weakref import WeakSet

from mindpy.events.event import Event, EventPriority


class EventBus:
    """
    Central event bus for all communication in MindPy.
    
    The event bus follows a publish-subscribe pattern and allows
    components to communicate without direct dependencies.
    """
    
    def __init__(self):
        """Initialize the event bus."""
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._wildcard_handlers: Set[Callable] = WeakSet()
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
    
    def subscribe(
        self,
        event_type: str,
        handler: Callable[[Event], Any]
    ) -> Callable:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: The type of event to subscribe to
            handler: The callback function to handle the event
            
        Returns:
            Unsubscribe function
        """
        self._handlers[event_type].append(handler)
        
        def unsubscribe():
            """Unsubscribe the handler."""
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
        
        return unsubscribe
    
    def subscribe_wildcard(
        self,
        handler: Callable[[Event], Any]
    ) -> Callable:
        """
        Subscribe to all events (wildcard subscription).
        
        Args:
            handler: The callback function to handle all events
            
        Returns:
            Unsubscribe function
        """
        self._wildcard_handlers.add(handler)
        
        def unsubscribe():
            """Unsubscribe the handler."""
            self._wildcard_handlers.discard(handler)
        
        return unsubscribe
    
    async def publish(self, event: Event) -> None:
        """
        Publish an event to the bus.
        
        Args:
            event: The event to publish
        """
        await self._event_queue.put(event)
    
    def publish_sync(self, event: Event) -> None:
        """
        Publish an event synchronously (immediate dispatch).
        
        Args:
            event: The event to publish
        """
        asyncio.create_task(self._dispatch(event))
    
    async def start(self) -> None:
        """Start the event bus worker."""
        if self._running:
            return
        
        self._running = True
        self._worker_task = asyncio.create_task(self._worker())
    
    async def stop(self) -> None:
        """Stop the event bus worker."""
        if not self._running:
            return
        
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
    
    async def _worker(self) -> None:
        """Worker task that processes events from the queue."""
        while self._running:
            try:
                event = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=1.0
                )
                await self._dispatch(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                # Log error but continue processing
                print(f"Error in event bus worker: {e}")
    
    async def _dispatch(self, event: Event) -> None:
        """
        Dispatch an event to all registered handlers.
        
        Args:
            event: The event to dispatch
        """
        async with self._lock:
            # Get handlers for this event type
            handlers = self._handlers.get(event.event_type, []).copy()
            
            # Add wildcard handlers
            handlers.extend(list(self._wildcard_handlers))
            
            # Sort by priority if handlers have priority attribute
            handlers.sort(
                key=lambda h: getattr(h, 'priority', EventPriority.NORMAL).value
            )
        
        # Dispatch to all handlers
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                # Log error but continue with other handlers
                print(f"Error in event handler {handler.__name__}: {e}")
    
    async def wait_for(
        self,
        event_type: str,
        timeout: Optional[float] = None,
        predicate: Optional[Callable[[Event], bool]] = None
    ) -> Event:
        """
        Wait for a specific event type.
        
        Args:
            event_type: The type of event to wait for
            timeout: Optional timeout in seconds
            predicate: Optional predicate to filter events
            
        Returns:
            The matching event
            
        Raises:
            asyncio.TimeoutError: If timeout is reached
        """
        future = asyncio.Future()
        
        def handler(event: Event):
            if predicate is None or predicate(event):
                if not future.done():
                    future.set_result(event)
        
        unsubscribe = self.subscribe(event_type, handler)
        
        try:
            return await asyncio.wait_for(future, timeout)
        finally:
            unsubscribe()
    
    def clear(self) -> None:
        """Clear all handlers."""
        self._handlers.clear()
        self._wildcard_handlers.clear()
    
    def get_handler_count(self, event_type: Optional[str] = None) -> int:
        """
        Get the number of handlers.
        
        Args:
            event_type: Optional event type to filter by
            
        Returns:
            Number of handlers
        """
        if event_type:
            return len(self._handlers.get(event_type, []))
        return sum(len(handlers) for handlers in self._handlers.values()) + len(self._wildcard_handlers)
