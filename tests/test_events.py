"""
Tests for the event bus system.
"""

import pytest
import asyncio
from mindpy.events import EventBus, Event, EventPriority, handler


class TestEventBus:
    """Test cases for EventBus."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a fresh event bus for each test."""
        return EventBus()
    
    @pytest.mark.unit
    def test_event_creation(self):
        """Test event creation."""
        event = Event(
            event_type="test_event",
            data={"key": "value"},
            source="test"
        )
        
        assert event.event_type == "test_event"
        assert event.data == {"key": "value"}
        assert event.source == "test"
        assert event.priority == EventPriority.NORMAL
    
    @pytest.mark.unit
    async def test_subscribe_and_publish(self, event_bus):
        """Test subscribing to and publishing events."""
        received_events = []
        
        async def handler(event):
            received_events.append(event)
        
        event_bus.subscribe("test_event", handler)
        await event_bus.publish(Event("test_event", {}, "test"))
        
        assert len(received_events) == 1
        assert received_events[0].event_type == "test_event"
    
    @pytest.mark.unit
    async def test_unsubscribe(self, event_bus):
        """Test unsubscribing from events."""
        received_events = []
        
        async def handler(event):
            received_events.append(event)
        
        event_bus.subscribe("test_event", handler)
        event_bus.unsubscribe("test_event", handler)
        
        await event_bus.publish(Event("test_event", {}, "test"))
        
        assert len(received_events) == 0
    
    @pytest.mark.unit
    async def test_wildcard_subscription(self, event_bus):
        """Test wildcard event subscriptions."""
        received_events = []
        
        async def handler(event):
            received_events.append(event)
        
        event_bus.subscribe("test.*", handler)
        
        await event_bus.publish(Event("test.event1", {}, "test"))
        await event_bus.publish(Event("test.event2", {}, "test"))
        await event_bus.publish(Event("other.event", {}, "test"))
        
        assert len(received_events) == 2
    
    @pytest.mark.unit
    async def test_event_priority(self, event_bus):
        """Test event priority ordering."""
        received_order = []
        
        async def high_handler(event):
            received_order.append("high")
        
        async def normal_handler(event):
            received_order.append("normal")
        
        async def low_handler(event):
            received_order.append("low")
        
        event_bus.subscribe("test", low_handler, EventPriority.LOW)
        event_bus.subscribe("test", high_handler, EventPriority.HIGH)
        event_bus.subscribe("test", normal_handler, EventPriority.NORMAL)
        
        await event_bus.publish(Event("test", {}, "test"))
        
        assert received_order == ["high", "normal", "low"]
    
    @pytest.mark.unit
    async def test_wait_for_event(self, event_bus):
        """Test waiting for a specific event."""
        async def publish_later():
            await asyncio.sleep(0.1)
            await event_bus.publish(Event("test_event", {"value": 42}, "test"))
        
        task = asyncio.create_task(publish_later())
        event = await event_bus.wait_for("test_event", timeout=1.0)
        
        assert event is not None
        assert event.data["value"] == 42
        await task
    
    @pytest.mark.unit
    def test_event_handler_decorator(self, event_bus):
        """Test the event handler decorator."""
        received_events = []
        
        @handler("test_event")
        async def my_handler(event):
            received_events.append(event)
        
        my_handler.register_handlers(event_bus)
        
        # Test that handler was registered
        assert "test_event" in event_bus._handlers


class TestEvent:
    """Test cases for Event class."""
    
    @pytest.mark.unit
    def test_event_to_dict(self):
        """Test event serialization to dictionary."""
        event = Event(
            event_type="test",
            data={"key": "value"},
            source="test_source"
        )
        
        event_dict = event.to_dict()
        
        assert event_dict["event_type"] == "test"
        assert event_dict["data"] == {"key": "value"}
        assert event_dict["source"] == "test_source"
    
    @pytest.mark.unit
    def test_event_from_dict(self):
        """Test event deserialization from dictionary."""
        event_dict = {
            "event_type": "test",
            "data": {"key": "value"},
            "source": "test_source",
            "priority": "high"
        }
        
        event = Event.from_dict(event_dict)
        
        assert event.event_type == "test"
        assert event.data == {"key": "value"}
        assert event.source == "test_source"
