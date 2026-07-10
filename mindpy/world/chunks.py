"""
Chunk manager for MindPy.

Provides chunk loading, chunk management, and chunk-based operations.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

from mindpy.navigation.movement import Position
from mindpy.world.blocks import BlockManager, BlockState, BlockType
from mindpy.logging import get_logger


@dataclass
class Chunk:
    """
    Represents a Minecraft chunk.
    
    Contains block data for a 16x256x16 area.
    """
    chunk_x: int
    chunk_z: int
    blocks: Dict[Tuple[int, int, int], BlockState] = None
    loaded: bool = False
    modified: bool = False
    
    def __post_init__(self):
        if self.blocks is None:
            self.blocks = {}
    
    def get_block_key(self, x: int, y: int, z: int) -> Tuple[int, int, int]:
        """
        Get the block key for local coordinates.
        
        Args:
            x: Local X coordinate (0-15)
            y: Y coordinate (0-255)
            z: Local Z coordinate (0-15)
            
        Returns:
            Block key tuple
        """
        return (x, y, z)
    
    def get_block(self, x: int, y: int, z: int) -> Optional[BlockState]:
        """
        Get a block at local coordinates.
        
        Args:
            x: Local X coordinate (0-15)
            y: Y coordinate (0-255)
            z: Local Z coordinate (0-15)
            
        Returns:
            Block state or None
        """
        key = self.get_block_key(x, y, z)
        return self.blocks.get(key)
    
    def set_block(self, x: int, y: int, z: int, block_type: BlockType) -> None:
        """
        Set a block at local coordinates.
        
        Args:
            x: Local X coordinate (0-15)
            y: Y coordinate (0-255)
            z: Local Z coordinate (0-15)
            block_type: Block type
        """
        from mindpy.world.blocks import BlockState
        key = self.get_block_key(x, y, z)
        
        block_state = BlockState(
            position=Position(
                self.chunk_x * 16 + x,
                y,
                self.chunk_z * 16 + z
            ),
            block_type=block_type
        )
        
        self.blocks[key] = block_state
        self.modified = True
    
    def get_block_count(self) -> int:
        """Get the number of blocks in the chunk."""
        return len(self.blocks)
    
    def __repr__(self) -> str:
        return f"Chunk({self.chunk_x}, {self.chunk_z}, loaded={self.loaded})"


class ChunkManager:
    """
    Manages chunk loading and operations.
    
    Handles chunk loading, unloading, and chunk-based queries.
    """
    
    def __init__(self, block_manager: BlockManager):
        """
        Initialize the chunk manager.
        
        Args:
            block_manager: Block manager to sync with
        """
        self._block_manager = block_manager
        self._chunks: Dict[Tuple[int, int], Chunk] = {}
        self._loaded_radius = 5  # Chunks to load around player
        self._logger = get_logger(__name__)
    
    def position_to_chunk(self, position: Position) -> Tuple[int, int]:
        """
        Convert a world position to chunk coordinates.
        
        Args:
            position: World position
            
        Returns:
            Tuple of (chunk_x, chunk_z)
        """
        chunk_x = int(position.x) // 16
        chunk_z = int(position.z) // 16
        return (chunk_x, chunk_z)
    
    def chunk_to_position(self, chunk_x: int, chunk_z: int) -> Position:
        """
        Convert chunk coordinates to world position.
        
        Args:
            chunk_x: Chunk X coordinate
            chunk_z: Chunk Z coordinate
            
        Returns:
            World position (chunk center)
        """
        return Position(
            chunk_x * 16 + 8,
            64,  # Default Y level
            chunk_z * 16 + 8
        )
    
    def get_chunk(self, chunk_x: int, chunk_z: int) -> Optional[Chunk]:
        """
        Get a chunk by coordinates.
        
        Args:
            chunk_x: Chunk X coordinate
            chunk_z: Chunk Z coordinate
            
        Returns:
            Chunk or None if not loaded
        """
        return self._chunks.get((chunk_x, chunk_z))
    
    def load_chunk(self, chunk_x: int, chunk_z: int) -> Chunk:
        """
        Load a chunk.
        
        Args:
            chunk_x: Chunk X coordinate
            chunk_z: Chunk Z coordinate
            
        Returns:
            Loaded chunk
        """
        chunk_key = (chunk_x, chunk_z)
        
        if chunk_key not in self._chunks:
            chunk = Chunk(chunk_x=chunk_x, chunk_z=chunk_z)
            self._chunks[chunk_key] = chunk
            self._logger.debug(f"Loaded chunk: {chunk_x}, {chunk_z}")
        else:
            chunk = self._chunks[chunk_key]
        
        chunk.loaded = True
        return chunk
    
    def unload_chunk(self, chunk_x: int, chunk_z: int) -> bool:
        """
        Unload a chunk.
        
        Args:
            chunk_x: Chunk X coordinate
            chunk_z: Chunk Z coordinate
            
        Returns:
            True if unloaded
        """
        chunk_key = (chunk_x, chunk_z)
        
        if chunk_key in self._chunks:
            chunk = self._chunks[chunk_key]
            
            # Save if modified
            if chunk.modified:
                self._save_chunk(chunk)
            
            del self._chunks[chunk_key]
            self._logger.debug(f"Unloaded chunk: {chunk_x}, {chunk_z}")
            return True
        
        return False
    
    def _save_chunk(self, chunk: Chunk) -> None:
        """
        Save a chunk's block data to the block manager.
        
        Args:
            chunk: Chunk to save
        """
        for block_state in chunk.blocks.values():
            self._block_manager.set_block(
                block_state.position,
                block_state.block_type
            )
    
    def load_around_position(self, position: Position) -> List[Chunk]:
        """
        Load chunks around a position.
        
        Args:
            position: Center position
            
        Returns:
            List of loaded chunks
        """
        center_chunk = self.position_to_chunk(position)
        loaded_chunks = []
        
        for dx in range(-self._loaded_radius, self._loaded_radius + 1):
            for dz in range(-self._loaded_radius, self._loaded_radius + 1):
                chunk_x = center_chunk[0] + dx
                chunk_z = center_chunk[1] + dz
                chunk = self.load_chunk(chunk_x, chunk_z)
                loaded_chunks.append(chunk)
        
        self._logger.debug(f"Loaded {len(loaded_chunks)} chunks around position")
        return loaded_chunks
    
    def unload_far_chunks(self, position: Position) -> int:
        """
        Unload chunks that are too far from a position.
        
        Args:
            position: Center position
            
        Returns:
            Number of chunks unloaded
        """
        center_chunk = self.position_to_chunk(position)
        to_unload = []
        
        for chunk_key, chunk in self._chunks.items():
            distance = max(
                abs(chunk.chunk_x - center_chunk[0]),
                abs(chunk.chunk_z - center_chunk[1])
            )
            
            if distance > self._loaded_radius + 2:
                to_unload.append(chunk_key)
        
        for chunk_key in to_unload:
            chunk_x, chunk_z = chunk_key
            self.unload_chunk(chunk_x, chunk_z)
        
        return len(to_unload)
    
    def get_loaded_chunks(self) -> List[Chunk]:
        """Get all loaded chunks."""
        return list(self._chunks.values())
    
    def get_chunk_count(self) -> int:
        """Get the number of loaded chunks."""
        return len(self._chunks)
    
    def get_blocks_in_chunk(self, chunk_x: int, chunk_z: int) -> List[BlockState]:
        """
        Get all blocks in a chunk.
        
        Args:
            chunk_x: Chunk X coordinate
            chunk_z: Chunk Z coordinate
            
        Returns:
            List of block states
        """
        chunk = self.get_chunk(chunk_x, chunk_z)
        if chunk:
            return list(chunk.blocks.values())
        return []
    
    def find_blocks_in_chunks(
        self,
        block_type: BlockType,
        chunk_x: int,
        chunk_z: int
    ) -> List[Position]:
        """
        Find blocks of a specific type in a chunk.
        
        Args:
            block_type: Block type to find
            chunk_x: Chunk X coordinate
            chunk_z: Chunk Z coordinate
            
        Returns:
            List of positions
        """
        chunk = self.get_chunk(chunk_x, chunk_z)
        if not chunk:
            return []
        
        positions = []
        for block_state in chunk.blocks.values():
            if block_state.block_type == block_type:
                positions.append(block_state.position)
        
        return positions
    
    def clear(self) -> None:
        """Clear all chunks."""
        for chunk in list(self._chunks.values()):
            if chunk.modified:
                self._save_chunk(chunk)
        self._chunks.clear()
    
    def __repr__(self) -> str:
        return f"ChunkManager(chunks={self.get_chunk_count()})"
