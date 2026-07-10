# Getting Started with MindPy

Welcome to MindPy, a comprehensive Python framework for building AI-powered Minecraft bots.

## Installation

### Prerequisites

- Python 3.12 or higher
- pip package manager

### Install from Source

```bash
git clone https://github.com/yourusername/mindpy.git
cd mindpy
pip install -e .
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Bot

Create a simple bot that connects to a Minecraft server:

```python
import asyncio
from mindpy import Bot

async def main():
    bot = Bot(
        host="localhost",
        port=25565,
        username="MyBot"
    )
    
    await bot.connect()
    await bot.run()

asyncio.run(main())
```

### Using the CLI

MindPy includes a command-line interface for quick bot control:

```bash
# Run a bot
mindpy run --host localhost --port 25565 --username MyBot

# Connect to a server
mindpy connect localhost 25565 MyBot

# Run a chat-enabled bot
mindpy chat --host localhost --username MyBot
```

### Configuration

Create a `config.yaml` file:

```yaml
bot:
  username: MindPyBot
  host: localhost
  port: 25565

logging:
  level: INFO
  file: logs/mindpy.log

ai:
  provider: openai
  model: gpt-4
  api_key: your-api-key
```

Then run with:

```bash
mindpy run --config config.yaml
```

## Core Concepts

### Event Bus

MindPy uses an event-driven architecture. All communication between components happens through the event bus:

```python
from mindpy.events import EventBus, Event

event_bus = EventBus()

async def my_handler(event):
    print(f"Received: {event.event_type}")

event_bus.subscribe("my_event", my_handler)
await event_bus.publish(Event("my_event", {"data": "value"}, "source"))
```

### Memory System

MindPy includes a multi-layered memory system:

```python
from mindpy.memory import MemoryManager

memory_manager = MemoryManager()

# Working memory for current context
memory_manager.working_memory.add("current_task", "mining")

# Long-term memory for persistent storage
memory_manager.long_term_memory.store_fact("home_location", "100, 64, 100")
```

### Goal System

Define hierarchical goals for your bot:

```python
from mindpy.goals import GoalManager, GoalStatus, GoalPriority

goal_manager = GoalManager(event_bus)

goal = goal_manager.create_goal(
    name="Collect Diamonds",
    description="Collect 10 diamonds",
    priority=GoalPriority.HIGH
)
```

### Task System

Create interruptible and suspendable tasks:

```python
from mindpy.tasks import TaskManager, BaseTask

class MiningTask(BaseTask):
    @property
    def name(self):
        return "mining"
    
    @property
    def description(self):
        return "Mine ores"
    
    async def execute(self, context):
        # Mining logic here
        return "completed"

task_manager = TaskManager(event_bus)
await task_manager.start()
```

## Next Steps

- Read the [Architecture Documentation](architecture.md) to understand the system design
- Check out the [Plugin Development Guide](plugin-development.md) to extend MindPy
- Explore the [Examples](../examples/) directory for sample bots
- Review the [API Documentation](api.md) for detailed API reference
