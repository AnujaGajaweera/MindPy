"""
World memory implementation for MindPy.

World memory stores information about the Minecraft world: blocks, chunks, biomes, etc.
"""

from typing import Any, Dict, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime
from mindpy.memory.base import Memory, MemoryEntry


@dataclass
class BlockInfo:
    """Information about a block."""
    position: Tuple[int, int, int]  # x, y, z
    block_type: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ChunkInfo:
    """Information about a chunk."""
    chunk_x: int
    chunk_z: int
    timestamp: datetime
    blocks: Dict[Tuple[int, int, int], str] = None  # local coordinates to block type
    
    def __post_init__(self):
        if self.blocks is None:
            self.blocks = {}


@dataclass
class BiomeInfo:
    """Information about a biome."""
    position: Tuple[int, int, int]
    biome_type: str
    timestamp: datetime


class WorldMemory(Memory):
    """
    World memory for storing Minecraft world information.
    
    Tracks blocks, chunks, biomes, and other world state information.
    """
    
    def __init__(self, capacity: int = 1000, persistence_enabled: bool = True):
        """
        Initialize world memory.
        
        Args:
            capacity: Maximum number of entries (default: 1000)
            persistence_enabled: Whether to persist to disk
        """
        super().__init__(capacity=capacity, persistence_enabled=persistence_enabled)
        self._block_index: Dict[Tuple[int, int, int], str] = {}  # position -> entry_id
        self._chunk_index: Dict[Tuple[int, int], str] = {}  # chunk coords -> entry_id
    
    def add(self, content: Any, entry_type: str = "world", **metadata) -> MemoryEntry:
        """
        Add world information to memory.
        
        Args:
            content: The content to store
            entry_type: Type of the entry
            **metadata: Additional metadata
            
        Returns:
            The created memory entry
        """
        if self.is_full():
            self._evict_oldest()
        
        entry = MemoryEntry(
            content=content,
            entry_type=entry_type,
            metadata=metadata,
            importance=metadata.get("importance", 0.6)
        )
        
        self._entries[entry.entry_id] = entry
        
        # Index by type
        if entry_type == "block" and isinstance(content, BlockInfo):
            self._block_index[content.position] = entry.entry_id
        elif entry_type == "chunk" and isinstance(content, ChunkInfo):
            self._chunk_index[(content.chunk_x, content.chunk_z)] = entry.entry_id
        
        return entry
    
    def add_block(
        self,
        position: Tuple[int, int, int],
        block_type: str,
        **metadata
    ) -> MemoryEntry:
        """
        Add block information.
        
        Args:
            position: Block position (x, y, z)
            block_type: Type of block
            **metadata: Additional metadata
            
        Returns:
            The memory entry
        """
        block_info = BlockInfo(
            position=position,
            block_type=block_type,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
        return self.add(block_info, "block", importance=0.4)
    
    def get_block(self, position: Tuple[int, int, int]) -> Optional[BlockInfo]:
        """
        Get block information at a position.
        
        Args:
            position: Block position (x, y, z)
            
        Returns:
            BlockInfo or None if not found
        """
        entry_id = self._block_index.get(position)
        if entry_id:
            entry = self.get(entry_id)
            if entry:
                return entry.content
        return None
    
    def add_chunk(
        self,
        chunk_x: int,
        chunk_z: int,
        blocks: Dict[Tuple[int, int, int], str],
        **metadata
    ) -> MemoryEntry:
        """
        Add chunk information.
        
        Args:
            chunk_x: Chunk X coordinate
            chunk_z: Chunk Z coordinate
            blocks: Dictionary of block positions to types
            **metadata: Additional metadata
            
        Returns:
            The memory entry
        """
        chunk_info = ChunkInfo(
            chunk_x=chunk_x,
            chunk_z=chunk_z,
            timestamp=datetime.utcnow(),
            blocks=blocks
        )
        return self.add(chunk_info, "chunk", importance=0.7)
    
    def get_chunk(self, chunk_x: int, chunk_z: int) -> Optional[ChunkInfo]:
        """
        Get chunk information.
        
        Args:
            chunk_x: Chunk X coordinate
            chunk_z: Chunk Z coordinate
            
        Returns:
            ChunkInfo or None if not found
        """
        entry_id = self._chunk_index.get((chunk_x, chunk_z))
        if entry_id:
            entry = self.get(entry_id)
            if entry:
                return entry.content
        return None
    
    def add_biome(
        self,
        position: Tuple[int, int, int],
        biome_type: str
    ) -> MemoryEntry:
        """
        Add biome information.
        
        Args:
            position: Position
            biome_type: Type of biome
            
        Returns:
            The memory entry
        """
        biome_info = BiomeInfo(
            position=position,
            biome_type=biome_type,
            timestamp=datetime.utcnow()
        )
        return self.add(biome_info, "biome", importance=0.5)
    
    def get_biomes(self) -> List[BiomeInfo]:
        """Get all biome information."""
        biomes = self.get_by_type("biome")
        return [b.content for b in biomes]
    
    def find_blocks_by_type(self, block_type: str, limit: int = 50) -> List[BlockInfo]:
        """
        Find all blocks of a specific type.
        
        Args:
            block_type: Type of block to find
            limit: Maximum number of results
            
        Returns:
            List of BlockInfo
        """
        blocks = self.get_by_type("block")
        matching = [b for b in blocks if b.content.block_type == block_type]
        
        for block in matching[:limit]:
            block.access()
        
        return [b.content for b in matching[:limit]]
    
    def get_loaded_chunks(self) -> List[Tuple[int, int]]:
        """
        Get list of loaded chunk coordinates.
        
        Returns:
            List of (chunk_x, chunk_z) tuples
        """
        return list(self._chunk_index.keys())
