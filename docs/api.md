# API Documentation

This document provides detailed API reference for MindPy components.

## Core Components

### Bot

The main bot class for connecting to and controlling a Minecraft bot.

```python
from mindpy import Bot

bot = Bot(
    host: str = "localhost",
    port: int = 25565,
    username: str = "MindPyBot",
    config: Optional[Config] = None
)
```

**Methods:**

- `async connect() -> None`: Connect to the server
- `async disconnect() -> None`: Disconnect from the server
- `async run() -> None`: Run the bot main loop
- `async chat(message: str) -> None`: Send a chat message
- `is_connected() -> bool`: Check if connected
- `get_position() -> Position`: Get current position
- `get_health() -> float`: Get current health
- `get_hunger() -> float`: Get current hunger

### EventBus

Central event bus for component communication.

```python
from mindpy.events import EventBus

event_bus = EventBus()
```

**Methods:**

- `subscribe(event_type: str, handler: Callable, priority: EventPriority = EventPriority.NORMAL) -> None`: Subscribe to events
- `unsubscribe(event_type: str, handler: Callable) -> None`: Unsubscribe from events
- `async publish(event: Event) -> None`: Publish an event
- `async wait_for(event_type: str, timeout: float = 10.0) -> Optional[Event]`: Wait for a specific event

### Config

Configuration management supporting multiple formats.

```python
from mindpy.config import Config

config = Config(config_path: Optional[str] = None)
```

**Methods:**

- `get(key: str, default: Any = None) -> Any`: Get a config value
- `set(key: str, value: Any) -> None`: Set a config value
- `load(path: str) -> None`: Load config from file
- `save(path: Optional[str] = None) -> None`: Save config to file
- `to_dict() -> Dict[str, Any]`: Convert to dictionary

### MemoryManager

Manages all memory types.

```python
from mindpy.memory import MemoryManager

memory_manager = MemoryManager()
```

**Properties:**

- `working_memory: WorkingMemory`: Current context memory
- `short_term_memory: ShortTermMemory`: Recent events memory
- `long_term_memory: LongTermMemory`: Persistent facts memory
- `conversation_memory: ConversationMemory`: Chat history memory
- `world_memory: WorldMemory`: World state memory
- `player_memory: PlayerMemory`: Player information memory
- `task_memory: TaskMemory`: Task history memory
- `knowledge_base: KnowledgeBase`: Structured knowledge memory

**Methods:**

- `async load_all() -> None`: Load all memories from storage
- `async save_all() -> None`: Save all memories to storage
- `async cleanup() -> None`: Clean up expired entries
- `get_statistics() -> Dict[str, int]`: Get memory statistics

### GoalManager

Manages hierarchical goals.

```python
from mindpy.goals import GoalManager

goal_manager = GoalManager(event_bus)
```

**Methods:**

- `create_goal(name: str, description: str, priority: GoalPriority, **metadata) -> Goal`: Create a goal
- `get_goal(goal_id: str) -> Optional[Goal]`: Get a goal by ID
- `async decompose_goal(goal_id: str, context: Optional[Dict] = None) -> List[Goal]`: Decompose a goal
- `update_goal_status(goal_id: str, status: GoalStatus, error_message: Optional[str] = None) -> bool`: Update goal status
- `get_goals_by_status(status: GoalStatus) -> List[Goal]`: Get goals by status
- `get_goal_tree(goal_id: str) -> Dict[str, Any]`: Get goal hierarchy

### TaskManager

Manages task execution.

```python
from mindpy.tasks import TaskManager

task_manager = TaskManager(event_bus)
await task_manager.start(num_workers: int = 4)
```

**Methods:**

- `async start(num_workers: int = 4) -> None`: Start task workers
- `async stop() -> None`: Stop task workers
- `async submit_task(task: Task) -> str`: Submit a task
- `get_task(task_id: str) -> Optional[Task]`: Get a task by ID
- `async cancel_task(task_id: str) -> bool`: Cancel a task
- `async suspend_task(task_id: str) -> bool`: Suspend a task
- `async resume_task(task_id: str) -> bool`: Resume a task
- `get_statistics() -> Dict[str, int]`: Get task statistics

### InventoryManager

Manages inventory and equipment.

```python
from mindpy.inventory import InventoryManager

inventory_manager = InventoryManager()
```

**Methods:**

- `get_player_inventory() -> Inventory`: Get player inventory
- `get_equipment(slot: EquipmentSlot) -> Optional[ItemStack]`: Get equipment
- `set_equipment(slot: EquipmentSlot, item_stack: Optional[ItemStack]) -> None`: Set equipment
- `equip_item(item_stack: ItemStack, slot: EquipmentSlot) -> bool`: Equip an item
- `unequip_item(slot: EquipmentSlot) -> Optional[ItemStack]`: Unequip an item
- `count_item(item_id: str) -> int`: Count items across all inventories
- `has_item(item_id: str, count: int = 1) -> bool`: Check if has enough items

### MovementController

Controls bot movement.

```python
from mindpy.navigation import MovementController

movement = MovementController()
```

**Methods:**

- `async move_to(target: Position, timeout: float = 30.0) -> bool`: Move to a position
- `async walk(direction: Tuple[float, float], distance: float) -> None`: Walk in a direction
- `async jump() -> None`: Jump
- `async sprint(enabled: bool = True) -> None`: Enable/disable sprinting
- `async swim(direction: Tuple[float, float, float]) -> None`: Swim
- `async climb(direction: Tuple[float, float]) -> None`: Climb
- `async stop() -> None`: Stop movement
- `get_position() -> Position`: Get current position

### PathFinder

A* pathfinding implementation.

```python
from mindpy.navigation import PathFinder

path_finder = PathFinder()
```

**Methods:**

- `async find_path(start: Position, goal: Position, is_walkable: Optional[Callable] = None, get_neighbors: Optional[Callable] = None) -> List[Position]`: Find a path
- `smooth_path(path: List[Position]) -> List[Position]`: Smooth a path

### WaypointManager

Manages waypoints.

```python
from mindpy.navigation import WaypointManager

waypoint_manager = WaypointManager()
```

**Methods:**

- `add_waypoint(name: str, position: Position, waypoint_type: WaypointType, **metadata) -> Waypoint`: Add a waypoint
- `get_waypoint(name: str) -> Optional[Waypoint]`: Get a waypoint
- `remove_waypoint(name: str) -> bool`: Remove a waypoint
- `find_nearest_waypoint(position: Position, waypoint_type: Optional[WaypointType] = None, max_distance: Optional[float] = None) -> Optional[Waypoint]`: Find nearest waypoint
- `search_waypoints(query: str) -> List[Waypoint]`: Search waypoints

### CraftingManager

Manages crafting operations.

```python
from mindpy.crafting import CraftingManager

crafting_manager = CraftingManager()
```

**Methods:**

- `register_recipe(recipe: Recipe) -> None`: Register a recipe
- `get_recipe(recipe_id: str) -> Optional[Recipe]`: Get a recipe
- `get_recipes_for_item(item_id: str) -> List[Recipe]`: Get recipes for an item
- `async craft(recipe_id: str, inventory: Inventory, count: int = 1) -> bool`: Craft an item
- `async craft_item(item_id: str, inventory: Inventory, count: int = 1) -> bool`: Craft an item by finding recipe

### LLMManager

Manages LLM providers.

```python
from mindpy.llm import LLMManager

llm_manager = LLMManager()
```

**Methods:**

- `register_provider(name: str, provider: LLMProvider) -> None`: Register a provider
- `get_provider(name: Optional[str] = None) -> Optional[LLMProvider]`: Get a provider
- `set_default_provider(name: str) -> bool`: Set default provider
- `async generate(messages: List[LLMMessage], provider: Optional[str] = None, **kwargs) -> LLMResponse`: Generate a response
- `async generate_stream(messages: List[LLMMessage], provider: Optional[str] = None, **kwargs)`: Generate streaming response
- `setup_openai(api_key: str, model: str = "gpt-4", **kwargs) -> None`: Setup OpenAI provider
- `setup_anthropic(api_key: str, model: str = "claude-3-opus-20240229", **kwargs) -> None`: Setup Anthropic provider
- `setup_gemini(api_key: str, model: str = "gemini-pro", **kwargs) -> None`: Setup Gemini provider
- `setup_ollama(base_url: str = "http://localhost:11434", model: str = "llama2", **kwargs) -> None`: Setup Ollama provider

### ToolRegistry

Manages AI tools.

```python
from mindpy.ai import ToolRegistry

tool_registry = ToolRegistry()
```

**Methods:**

- `register(tool: Tool) -> None`: Register a tool
- `unregister(tool_name: str) -> bool`: Unregister a tool
- `get_tool(tool_name: str) -> Optional[Tool]`: Get a tool
- `get_all_tools() -> List[Tool]`: Get all tools
- `get_schemas() -> List[Dict[str, Any]]`: Get tool schemas for function calling

### AIAgent

AI decision-making agent.

```python
from mindpy.ai import AIAgent

ai_agent = AIAgent(llm_manager, tool_registry, system_prompt)
```

**Methods:**

- `async decide(context: AgentContext, user_message: str = "") -> str`: Make a decision
- `async decide_with_tools(context: AgentContext, user_message: str = "") -> List[ToolCall]`: Make a decision with tool execution
- `set_system_prompt(prompt: str) -> None`: Set system prompt
- `clear_history() -> None`: Clear conversation history
- `get_history() -> List[LLMMessage]`: Get conversation history

## Data Models

### Event

```python
from mindpy.events import Event, EventPriority

event = Event(
    event_type: str,
    data: Dict[str, Any],
    source: str,
    priority: EventPriority = EventPriority.NORMAL
)
```

### Goal

```python
from mindpy.goals import Goal, GoalStatus, GoalPriority

goal = Goal(
    name: str,
    description: str = "",
    priority: GoalPriority = GoalPriority.NORMAL,
    parent_goal_id: Optional[str] = None,
    **metadata
)
```

### Task

```python
from mindpy.tasks import Task, TaskStatus, TaskPriority

task = Task(
    task_type: str,
    description: str = "",
    priority: TaskPriority = TaskPriority.NORMAL,
    **metadata
)
```

### ItemStack

```python
from mindpy.inventory import ItemStack

stack = ItemStack(
    item_id: str,
    count: int = 1,
    max_count: int = 64,
    display_name: str = "",
    nbt: Optional[Dict] = None
)
```

### Position

```python
from mindpy.navigation import Position

position = Position(x: float, y: float, z: float)
```

## Enums

### GoalStatus

- `PENDING`: Goal is pending
- `IN_PROGRESS`: Goal is in progress
- `COMPLETED`: Goal is completed
- `FAILED`: Goal failed
- `ABORTED`: Goal was aborted
- `BLOCKED`: Goal is blocked

### TaskStatus

- `PENDING`: Task is pending
- `RUNNING`: Task is running
- `SUSPENDED`: Task is suspended
- `COMPLETED`: Task is completed
- `FAILED`: Task failed
- `CANCELLED`: Task was cancelled

### EventPriority

- `CRITICAL`: Highest priority
- `HIGH`: High priority
- `NORMAL`: Normal priority
- `LOW`: Low priority
