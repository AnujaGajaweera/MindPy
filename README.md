# MindPy

A Python AI framework for controlling Minecraft bots using PyCraft.

## Vision

MindPy is the definitive Python AI framework for Minecraft, built entirely around PyCraft. It provides a clean, modular, plugin-based, event-driven, and highly extensible architecture for building intelligent Minecraft bots.

## Features

- **Bot Management**: Login, reconnect, disconnect, multi-bot support
- **Navigation**: Walking, jumping, swimming, parkour, pathfinding, waypoints
- **Mining**: Ore detection, tool selection, safety checks, inventory management
- **Crafting**: Recipe lookup, craft planning, execution with multiple machines
- **Inventory**: Equipment, storage, chest interaction, sorting
- **Farming**: Harvesting, planting, animal breeding, fishing
- **Combat**: PvE, PvP, bows, shields, critical attacks
- **World**: Block lookup, biome lookup, chunk management, entities
- **Communication**: Chat, private messages, command parsing
- **AI System**: Perception, memory, planning, decision making, execution
- **Memory System**: Working, short-term, long-term, conversation, world, player, task, knowledge base
- **Goal System**: Hierarchical goal decomposition
- **Task System**: Interruptible, suspendable, serializable, cancelable, restartable
- **Skills**: Reusable high-level behaviors
- **Plugin System**: Automatic discovery, dependencies, metadata, versioning
- **Event Bus**: All communication through events
- **LLM Integration**: OpenAI, Anthropic, Google Gemini, Ollama, LM Studio, OpenRouter
- **Tool Calling**: AI can invoke tools with descriptions and parameters
- **Reflection**: Self-improvement through task evaluation
- **Configuration**: YAML, JSON, TOML, environment variables
- **Logging**: Structured logging with rich console and file logs
- **CLI**: Comprehensive command-line interface
- **API**: REST API and optional WebSocket API

## Installation

```bash
pip install mindpy
```

For development:

```bash
git clone https://github.com/AnujaGajaweera/MindPy.git
cd mindpy
pip install -e ".[dev,llm,docs]"
```

## Quick Start

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
    
    # Your bot logic here
    
    await bot.disconnect()

asyncio.run(main())
```

## Architecture

MindPy follows clean architecture principles:

- **SOLID principles**
- **Dependency Injection**
- **Composition over inheritance**
- **Event Bus architecture**
- **Service-oriented design**
- **Plugin architecture**
- **Domain Driven Design**

No global state. Everything is injectable.

## Documentation

Comprehensive documentation is available at [https://mindpy.readthedocs.io](https://mindpy.readthedocs.io)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](https://github.com/AnujaGajaweera/MindPy/blob/main/CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](https://github.com/AnujaGajaweera/MindPy/blob/main/LICENSE) for details.

## Acknowledgments

MindPy is inspired by [Mineflayer](https://github.com/prismarinejs/mineflayer) but is a complete reimplementation in Python with modern architecture and extensibility in mind.
