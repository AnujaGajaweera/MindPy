# Plugin Development Guide

This guide covers how to create plugins for MindPy to extend its functionality.

## Plugin Basics

A plugin is a Python module that extends MindPy's capabilities. Plugins can:
- Add new commands
- Respond to events
- Provide new skills
- Integrate with external services
- Modify bot behavior

## Creating a Plugin

### Basic Plugin Structure

```python
from mindpy.plugins import Plugin, PluginMetadata
from mindpy.events import Event, EventTypes
from mindpy.logging import get_logger

class MyPlugin(Plugin):
    """A simple example plugin."""
    
    @property
    def metadata(self):
        """Return plugin metadata."""
        return PluginMetadata(
            name="my_plugin",
            version="1.0.0",
            description="My custom plugin",
            author="Your Name",
            dependencies=[]
        )
    
    async def on_enable(self):
        """Called when the plugin is enabled."""
        self._logger = get_logger(__name__)
        self._logger.info("MyPlugin enabled!")
        
        # Subscribe to events
        self._event_bus.subscribe(
            EventTypes.BOT_CONNECTED,
            self._on_bot_connected
        )
    
    async def on_disable(self):
        """Called when the plugin is disabled."""
        self._logger.info("MyPlugin disabled!")
        
        # Unsubscribe from events
        self._event_bus.unsubscribe(
            EventTypes.BOT_CONNECTED,
            self._on_bot_connected
        )
    
    async def _on_bot_connected(self, event: Event):
        """Handle bot connected event."""
        self._logger.info(f"Bot connected: {event.data}")
```

### Plugin Lifecycle

Plugins go through the following lifecycle:

1. **Discovery**: Plugin manager finds the plugin
2. **Loading**: Plugin is loaded and metadata is read
3. **Dependency Resolution**: Dependencies are checked
4. **Enabling**: `on_enable()` is called
5. **Running**: Plugin is active and responding to events
6. **Disabling**: `on_disable()` is called
7. **Unloading**: Plugin is removed from memory

## Plugin Dependencies

Plugins can depend on other plugins:

```python
class MyPlugin(Plugin):
    @property
    def metadata(self):
        return PluginMetadata(
            name="my_plugin",
            version="1.0.0",
            description="Plugin with dependencies",
            dependencies=["other_plugin"]
        )
```

The plugin manager will ensure dependencies are loaded before enabling your plugin.

## Event Handling

### Subscribing to Events

```python
async def on_enable(self):
    # Subscribe to specific event type
    self._event_bus.subscribe(
        EventTypes.BOT_CONNECTED,
        self._on_bot_connected
    )
    
    # Subscribe with wildcard
    self._event_bus.subscribe(
        "bot.*",
        self._on_bot_event
    )
    
    # Subscribe with priority
    self._event_bus.subscribe(
        EventTypes.CHAT_MESSAGE,
        self._on_chat,
        priority=EventPriority.HIGH
    )
```

### Event Handlers

```python
async def _on_bot_connected(self, event: Event):
    """Handle bot connected event."""
    bot_id = event.data.get("bot_id")
    self._logger.info(f"Bot {bot_id} connected")

async def _on_chat(self, event: Event):
    """Handle chat messages."""
    message = event.data.get("message")
    sender = event.data.get("sender")
    
    # Respond to specific messages
    if message == "hello":
        await self._bot.chat(f"Hi {sender}!")
```

## Adding Commands

Plugins can add custom commands to the CLI:

```python
async def on_enable(self):
    # Register command with CLI
    # This requires integration with the CLI system
    pass
```

## Providing Skills

Plugins can provide new skills:

```python
from mindpy.skills import Skill, SkillResult

class CustomSkill(Skill):
    @property
    def name(self):
        return "custom_skill"
    
    @property
    def description(self):
        return "A custom skill"
    
    async def execute(self, context):
        # Skill implementation
        return SkillResult(success=True, message="Skill executed")

async def on_enable(self):
    # Register skill with skill registry
    skill = CustomSkill()
    self._skill_registry.register(skill)
```

## Configuration

Plugins can have their own configuration:

```python
async def on_enable(self):
    # Get plugin-specific config
    config = self._config.get(f"plugins.{self.metadata.name}", {})
    
    # Use config values
    self._setting = config.get("setting", "default")
```

Configuration in `config.yaml`:

```yaml
plugins:
  my_plugin:
    setting: value
```

## Plugin Distribution

### Package Structure

```
my_mindpy_plugin/
├── setup.py
├── README.md
├── my_mindpy_plugin/
│   ├── __init__.py
│   └── plugin.py
```

### setup.py

```python
from setuptools import setup, find_packages

setup(
    name="my-mindpy-plugin",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "mindpy.plugins": [
            "my_plugin = my_mindpy_plugin.plugin:MyPlugin"
        ]
    }
)
```

### Installation

```bash
pip install my-mindpy-plugin
```

## Best Practices

### Error Handling

Always handle errors gracefully:

```python
async def _on_event(self, event: Event):
    try:
        # Event handling logic
        pass
    except Exception as e:
        self._logger.error(f"Error handling event: {e}")
```

### Resource Cleanup

Clean up resources in `on_disable`:

```python
async def on_disable(self):
    # Close connections
    # Unsubscribe from events
    # Release resources
    pass
```

### Logging

Use the logging system:

```python
self._logger = get_logger(__name__)
self._logger.info("Info message")
self._logger.warning("Warning message")
self._logger.error("Error message")
```

### Performance

Avoid blocking operations:

```python
# Bad - blocking
def _on_event(self, event):
    time.sleep(1)  # Blocks the event loop

# Good - async
async def _on_event(self, event):
    await asyncio.sleep(1)  # Non-blocking
```

## Example Plugins

### Chat Responder Plugin

```python
from mindpy.plugins import Plugin, PluginMetadata
from mindpy.events import Event, EventTypes
from mindpy.logging import get_logger

class ChatResponderPlugin(Plugin):
    """Plugin that responds to chat messages."""
    
    @property
    def metadata(self):
        return PluginMetadata(
            name="chat_responder",
            version="1.0.0",
            description="Responds to chat messages"
        )
    
    async def on_enable(self):
        self._logger = get_logger(__name__)
        self._event_bus.subscribe(
            EventTypes.CHAT_MESSAGE,
            self._on_chat
        )
    
    async def on_disable(self):
        self._event_bus.unsubscribe(
            EventTypes.CHAT_MESSAGE,
            self._on_chat
        )
    
    async def _on_chat(self, event: Event):
        message = event.data.get("message", "").lower()
        sender = event.data.get("sender")
        
        responses = {
            "hello": f"Hi {sender}!",
            "help": "I'm a MindPy bot. Type 'hello' to greet me!",
            "status": "I'm running normally!"
        }
        
        if message in responses:
            bot = self._bot_manager.get_bot(event.data.get("bot_id"))
            if bot:
                await bot.chat(responses[message])
```

### Auto-Save Plugin

```python
from mindpy.plugins import Plugin, PluginMetadata
from mindpy.events import Event, EventTypes
from mindpy.logging import get_logger
import asyncio

class AutoSavePlugin(Plugin):
    """Plugin that periodically saves bot state."""
    
    @property
    def metadata(self):
        return PluginMetadata(
            name="auto_save",
            version="1.0.0",
            description="Periodically saves bot state"
        )
    
    async def on_enable(self):
        self._logger = get_logger(__name__)
        self._save_interval = 300  # 5 minutes
        self._save_task = asyncio.create_task(self._save_loop())
    
    async def on_disable(self):
        if self._save_task:
            self._save_task.cancel()
            try:
                await self._save_task
            except asyncio.CancelledError:
                pass
    
    async def _save_loop(self):
        """Periodically save bot state."""
        while True:
            await asyncio.sleep(self._save_interval)
            await self._save_state()
    
    async def _save_state(self):
        """Save current bot state."""
        # Save logic here
        self._logger.info("Bot state saved")
```

## Testing Plugins

Test your plugins using pytest:

```python
import pytest
from mindpy.plugins import Plugin, PluginMetadata

class TestPlugin(Plugin):
    @property
    def metadata(self):
        return PluginMetadata(
            name="test_plugin",
            version="1.0.0"
        )

@pytest.mark.unit
def test_plugin_enable():
    """Test plugin enabling."""
    plugin = TestPlugin()
    # Mock dependencies
    # plugin._event_bus = EventBus()
    # plugin._bot_manager = BotManager()
    
    # asyncio.run(plugin.on_enable())
    # assert plugin.is_enabled()
```

## Debugging Plugins

Enable debug logging:

```yaml
logging:
  level: DEBUG
```

Check plugin status:

```python
# In your code
plugin_manager.list_plugins()
```

## Plugin Security

Plugins run with the same privileges as the bot. Be careful with:

- File system access
- Network requests
- System commands
- Sensitive data

Always validate inputs and sanitize outputs.
