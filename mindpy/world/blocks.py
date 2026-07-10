"""
Block manager for MindPy.

Provides block lookup, block state management, and block interaction.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from mindpy.navigation.movement import Position
from mindpy.logging import get_logger


class BlockType(Enum):
    """Common block types."""
    AIR = "air"
    STONE = "stone"
    DIRT = "dirt"
    GRASS_BLOCK = "grass_block"
    COBBLESTONE = "cobblestone"
    OAK_LOG = "oak_log"
    OAK_PLANKS = "oak_planks"
    WATER = "water"
    LAVA = "lava"
    SAND = "sand"
    GRAVEL = "gravel"
    COAL_ORE = "coal_ore"
    IRON_ORE = "iron_ore"
    GOLD_ORE = "gold_ore"
    DIAMOND_ORE = "diamond_ore"
    BEDROCK = "bedrock"


@dataclass
class BlockState:
    """
    State of a block at a specific position.
    
    Contains block type, position, and additional properties.
    """
    position: Position
    block_type: BlockType
    hardness: float = 1.0
    transparent: bool = False
    solid: bool = True
    properties: Dict[str, any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
    
    def is_walkable(self) -> bool:
        """Check if the block can be walked on."""
        return self.solid and not self.transparent
    
    def is_obstacle(self) -> bool:
        """Check if the block is an obstacle."""
        return self.solid
    
    def __repr__(self) -> str:
        return f"BlockState({self.block_type.value} at {self.position})"


class BlockManager:
    """
    Manages block information and state.
    
    Provides block lookup, state tracking, and block interaction.
    """
    
    def __init__(self):
        """Initialize the block manager."""
        self._blocks: Dict[Tuple[int, int, int], BlockState] = {}
        self._logger = get_logger(__name__)
        self._block_hardness = {
            BlockType.AIR: 0.0,
            BlockType.STONE: 1.5,
            BlockType.DIRT: 0.5,
            BlockType.GRASS_BLOCK: 0.6,
            BlockType.COBBLESTONE: 2.0,
            BlockType.OAK_LOG: 2.0,
            BlockType.OAK_PLANKS: 2.0,
            BlockType.WATER: 100.0,
            BlockType.LAVA: 100.0,
            BlockType.SAND: 0.5,
            BlockType.GRAVEL: 0.6,
            BlockType.COAL_ORE: 3.0,
            BlockType.IRON_ORE: 3.0,
            BlockType.GOLD_ORE: 3.0,
            BlockType.DIAMOND_ORE: 3.0,
            BlockType.BEDROCK: -1.0,  # Unbreakable
        }
    
    def get_block(self, position: Position) -> Optional[BlockState]:
        """
        Get the block state at a position.
        
        Args:
            position: Block position
            
        Returns:
            Block state or None if not loaded
        """
        key = (int(position.x), int(position.y), int(position.z))
        return self._blocks.get(key)
    
    def set_block(self, position: Position, block_type: BlockType) -> BlockState:
        """
        Set the block type at a position.
        
        Args:
            position: Block position
            block_type: Block type
            
        Returns:
            Created block state
        """
        key = (int(position.x), int(position.y), int(position.z))
        hardness = self._block_hardness.get(block_type, 1.0)
        
        block_state = BlockState(
            position=position,
            block_type=block_type,
            hardness=hardness,
            transparent=block_type in [BlockType.AIR, BlockType.WATER, BlockType.LAVA],
            solid=block_type not in [BlockType.AIR, BlockType.WATER, BlockType.LAVA]
        )
        
        self._blocks[key] = block_state
        return block_state
    
    def remove_block(self, position: Position) -> bool:
        """
        Remove a block (set to air).
        
        Args:
            position: Block position
            
        Returns:
            True if removed
        """
        return self.set_block(position, BlockType.AIR) is not None
    
    def get_blocks_in_area(
        self,
        min_pos: Position,
        max_pos: Position
    ) -> List[BlockState]:
        """
        Get all blocks in an area.
        
        Args:
            min_pos: Minimum position (inclusive)
            max_pos: Maximum position (inclusive)
            
        Returns:
            List of block states
        """
        blocks = []
        
        for x in range(int(min_pos.x), int(max_pos.x) + 1):
            for y in range(int(min_pos.y), int(max_pos.y) + 1):
                for z in range(int(min_pos.z), int(max_pos.z) + 1):
                    block = self.get_block(Position(x, y, z))
                    if block:
                        blocks.append(block)
        
        return blocks
    
    def find_blocks_by_type(
        self,
        block_type: BlockType,
        center: Position,
        radius: int = 10
    ) -> List[Position]:
        """
        Find all blocks of a specific type within a radius.
        
        Args:
            block_type: Block type to find
            center: Center position
            radius: Search radius
            
        Returns:
            List of positions
        """
        positions = []
        
        for x in range(int(center.x) - radius, int(center.x) + radius + 1):
            for y in range(int(center.y) - radius, int(center.y) + radius + 1):
                for z in range(int(center.z) - radius, int(center.z) + radius + 1):
                    block = self.get_block(Position(x, y, z))
                    if block and block.block_type == block_type:
                        positions.append(block.position)
        
        return positions
    
    def is_solid(self, position: Position) -> bool:
        """
        Check if a block at a position is solid.
        
        Args:
            position: Block position
            
        Returns:
            True if solid
        """
        block = self.get_block(position)
        return block.is_obstacle() if block else False
    
    def is_walkable(self, position: Position) -> bool:
        """
        Check if a block at a position can be walked on.
        
        Args:
            position: Block position
            
        Returns:
            True if walkable
        """
        block = self.get_block(position)
        return block.is_walkable() if block else False
    
    def get_block_hardness(self, position: Position) -> float:
        """
        Get the hardness of a block.
        
        Args:
            position: Block position
            
        Returns:
            Block hardness
        """
        block = self.get_block(position)
        return block.hardness if block else 0.0
    
    def clear(self) -> None:
        """Clear all block data."""
        self._blocks.clear()
    
    def get_block_count(self) -> int:
        """Get the total number of loaded blocks."""
        return len(self._blocks)
    
    def __repr__(self) -> str:
        return f"BlockManager(blocks={self.get_block_count()})"
