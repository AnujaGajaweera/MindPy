# MindPy Architecture

MindPy is built on clean architecture principles with a focus on modularity, extensibility, and testability.

## Design Principles

### SOLID Principles

- **Single Responsibility**: Each component has one clear purpose
- **Open/Closed**: Components are open for extension, closed for modification
- **Liskov Substitution**: Subtypes are substitutable for their base types
- **Interface Segregation**: Small, focused interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

### Core Principles

- **Dependency Injection**: All dependencies are injected, no global state
- **Composition over Inheritance**: Prefer composition to share behavior
- **Event-Driven**: All communication happens through the event bus
- **Service-Oriented**: Each subsystem is a self-contained service
- **Domain-Driven Design**: Clear separation of domains (bot, world, AI, etc.)

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Layer                            │
│  (Commands: run, connect, chat, shell, config, plugins)   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                       API Layer                            │
│              (REST API + WebSocket)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                      Bot Layer                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │   Bot    │  │BotManager│  │ Lifecycle│                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Service Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  Events  │  │  Memory  │  │  Goals   │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  Tasks   │  │  Skills  │  │  Config  │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                 Domain Layer                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │Navigation│  │Inventory │  │ Crafting │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  Mining  │  │  World   │  │   AI     │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                Infrastructure Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  Logging │  │  Config  │  │  Plugins │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
│  ┌──────────┐  ┌──────────┐                                 │
│  │   LLM    │  │  PyCraft │                                 │
│  └──────────┘  └──────────┘                                 │
└─────────────────────────────────────────────────────────────┘
```

## Component Overview

### Event Bus

The central communication hub for the entire system. All components publish and subscribe to events.

**Key Features:**
- Async publish/subscribe
- Event priority ordering
- Wildcard subscriptions
- Wait for specific events

### Memory System

Multi-layered memory for different types of information:

- **Working Memory**: Current context and active task
- **Short-Term Memory**: Recent events with expiration
- **Long-Term Memory**: Persistent facts and patterns
- **Conversation Memory**: Chat history
- **World Memory**: Blocks, chunks, biomes
- **Player Memory**: Player information and relationships
- **Task Memory**: Task history and statistics
- **Knowledge Base**: Structured knowledge triples

### Goal System

Hierarchical goal decomposition:

- Goals can have sub-goals
- Automatic decomposition into tasks
- Priority-based execution
- Progress tracking

### Task System

Interruptible and suspendable tasks:

- Tasks can be paused and resumed
- Tasks can be serialized and restored
- Tasks can be cancelled
- Automatic retry on failure

### Navigation

Movement and pathfinding:

- Movement controller for basic actions
- A* pathfinding with heuristics
- Waypoint management
- Path smoothing

### Inventory

Item management:

- Inventory with slots and item stacks
- Equipment management
- Chest interaction
- Item transfer operations

### Crafting

Recipe-based crafting:

- Recipe registry
- Craft planning
- Multi-machine support
- Cost calculation

### Mining

Automated mining:

- Mining planner
- Ore detection
- Tool selection
- Safety checks

### World Perception

World state tracking:

- Block manager
- Entity tracking
- Chunk management
- Biome information

### AI System

LLM integration:

- Provider abstraction (OpenAI, Anthropic, Gemini, Ollama)
- Tool calling
- Reflection engine
- Agent decision-making

### Plugin System

Extensible architecture:

- Automatic plugin discovery
- Dependency resolution
- Lifecycle management
- Event hooks

## Data Flow

### Bot Startup Flow

1. Configuration loaded
2. Event bus initialized
3. Memory manager created
4. Plugin manager loads plugins
5. Bot instance created
6. Bot connects to server
7. Event loop starts

### Goal Execution Flow

1. Goal created by user or AI
2. Goal decomposed into sub-goals
3. Sub-goals decomposed into tasks
4. Tasks queued in task manager
5. Task workers execute tasks
6. Results reported via events
7. Goal progress updated
8. Goal marked complete when all tasks done

### AI Decision Flow

1. Context gathered from memory
2. Context formatted for LLM
3. LLM generates decision
4. Tools called if needed
5. Actions executed
6. Results stored in memory
7. Reflection on outcome

## Extension Points

### Custom Plugins

Create plugins to extend functionality:

```python
from mindpy.plugins import Plugin, PluginMetadata

class MyPlugin(Plugin):
    @property
    def metadata(self):
        return PluginMetadata(
            name="my_plugin",
            version="1.0.0",
            description="My custom plugin"
        )
    
    async def on_enable(self):
        # Plugin initialization
        pass
    
    async def on_disable(self):
        # Plugin cleanup
        pass
```

### Custom Skills

Create reusable behaviors:

```python
from mindpy.skills import Skill, SkillResult

class MySkill(Skill):
    @property
    def name(self):
        return "my_skill"
    
    @property
    def description(self):
        return "My custom skill"
    
    async def execute(self, context):
        # Skill logic
        return SkillResult(success=True)
```

### Custom LLM Providers

Add support for new LLM APIs:

```python
from mindpy.llm import LLMProvider, LLMResponse

class MyProvider(LLMProvider):
    async def generate(self, messages, **kwargs):
        # Provider-specific implementation
        return LLMResponse(content="response")
```

## Performance Considerations

- Async/await for all I/O operations
- Minimal allocations in hot paths
- No blocking operations in event loop
- Efficient event queue processing
- Memory pooling where appropriate

## Security Considerations

- API keys stored securely
- Plugin sandboxing
- Input validation on all external inputs
- Rate limiting on API calls
- Secure WebSocket connections
