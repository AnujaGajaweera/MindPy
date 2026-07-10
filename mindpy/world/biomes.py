"""
Biome manager for MindPy.

Provides biome lookup, biome information, and biome-based operations.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from mindpy.navigation.movement import Position
from mindpy.logging import get_logger


class BiomeType(Enum):
    """Types of biomes."""
    PLAINS = "plains"
    FOREST = "forest"
    DESERT = "desert"
    MOUNTAINS = "mountains"
    TAIGA = "taiga"
    SWAMP = "swamp"
    JUNGLE = "jungle"
    OCEAN = "ocean"
    RIVER = "river"
    BEACH = "beach"
    SNOWY_TUNDRA = "snowy_tundra"
    ICE_SPIKES = "ice_spikes"
    MUSHROOM_FIELDS = "mushroom_fields"
    NETHER_WASTES = "nether_wastes"
    THE_END = "the_end"


@dataclass
class Biome:
    """
    Represents a biome in the world.
    
    Contains biome type, temperature, and properties.
    """
    biome_type: BiomeType
    temperature: float = 0.5
    humidity: float = 0.5
    has_precipitation: bool = True
    is_rare: bool = False
    
    def __repr__(self) -> str:
        return f"Biome({self.biome_type.value})"


class BiomeManager:
    """
    Manages biome information.
    
    Provides biome lookup and biome-based queries.
    """
    
    def __init__(self):
        """Initialize the biome manager."""
        self._biomes: Dict[Tuple[int, int], Biome] = {}  # chunk_x, chunk_z -> biome
        self._logger = get_logger(__name__)
        self._biome_properties = {
            BiomeType.PLAINS: {"temperature": 0.8, "humidity": 0.4},
            BiomeType.FOREST: {"temperature": 0.7, "humidity": 0.8},
            BiomeType.DESERT: {"temperature": 2.0, "humidity": 0.0},
            BiomeType.MOUNTAINS: {"temperature": 0.2, "humidity": 0.3},
            BiomeType.TAIGA: {"temperature": 0.25, "humidity": 0.8},
            BiomeType.SWAMP: {"temperature": 0.8, "humidity": 0.9},
            BiomeType.JUNGLE: {"temperature": 0.95, "humidity": 0.9},
            BiomeType.OCEAN: {"temperature": 0.5, "humidity": 0.5},
            BiomeType.RIVER: {"temperature": 0.5, "humidity": 0.7},
            BiomeType.BEACH: {"temperature": 0.8, "humidity": 0.7},
            BiomeType.SNOWY_TUNDRA: {"temperature": 0.0, "humidity": 0.5},
            BiomeType.ICE_SPIKES: {"temperature": 0.0, "humidity": 0.5},
            BiomeType.MUSHROOM_FIELDS: {"temperature": 0.9, "humidity": 1.0},
            BiomeType.NETHER_WASTES: {"temperature": 2.0, "humidity": 0.0},
            BiomeType.THE_END: {"temperature": 0.5, "humidity": 0.5},
        }
    
    def get_biome_at_chunk(self, chunk_x: int, chunk_z: int) -> Optional[Biome]:
        """
        Get the biome at chunk coordinates.
        
        Args:
            chunk_x: Chunk X coordinate
            chunk_z: Chunk Z coordinate
            
        Returns:
            Biome or None if not loaded
        """
        return self._biomes.get((chunk_x, chunk_z))
    
    def set_biome_at_chunk(self, chunk_x: int, chunk_z: int, biome: Biome) -> None:
        """
        Set the biome at chunk coordinates.
        
        Args:
            chunk_x: Chunk X coordinate
            chunk_z: Chunk Z coordinate
            biome: Biome to set
        """
        self._biomes[(chunk_x, chunk_z)] = biome
    
    def get_biome_at_position(self, position: Position) -> Optional[Biome]:
        """
        Get the biome at a world position.
        
        Args:
            position: World position
            
        Returns:
            Biome or None if not loaded
        """
        chunk_x = int(position.x) // 16
        chunk_z = int(position.z) // 16
        return self.get_biome_at_chunk(chunk_x, chunk_z)
    
    def create_biome(self, biome_type: BiomeType) -> Biome:
        """
        Create a biome with default properties.
        
        Args:
            biome_type: Type of biome
            
        Returns:
            Created biome
        """
        properties = self._biome_properties.get(biome_type, {})
        return Biome(
            biome_type=biome_type,
            temperature=properties.get("temperature", 0.5),
            humidity=properties.get("humidity", 0.5),
            has_precipitation=properties.get("has_precipitation", True)
        )
    
    def find_biomes_by_type(self, biome_type: BiomeType) -> List[Tuple[int, int]]:
        """
        Find all chunks with a specific biome type.
        
        Args:
            biome_type: Biome type to find
            
        Returns:
            List of (chunk_x, chunk_z) tuples
        """
        return [
            (chunk_x, chunk_z)
            for (chunk_x, chunk_z), biome in self._biomes.items()
            if biome.biome_type == biome_type
        ]
    
    def find_biomes_in_radius(
        self,
        position: Position,
        radius_chunks: int = 5
    ) -> List[Biome]:
        """
        Find biomes within a radius.
        
        Args:
            position: Center position
            radius_chunks: Radius in chunks
            
        Returns:
            List of biomes
        """
        center_chunk_x = int(position.x) // 16
        center_chunk_z = int(position.z) // 16
        
        biomes = []
        for dx in range(-radius_chunks, radius_chunks + 1):
            for dz in range(-radius_chunks, radius_chunks + 1):
                chunk_x = center_chunk_x + dx
                chunk_z = center_chunk_z + dz
                biome = self.get_biome_at_chunk(chunk_x, chunk_z)
                if biome:
                    biomes.append(biome)
        
        return biomes
    
    def is_hot(self, biome: Biome) -> bool:
        """Check if a biome is hot."""
        return biome.temperature > 1.0
    
    def is_cold(self, biome: Biome) -> bool:
        """Check if a biome is cold."""
        return biome.temperature < 0.3
    
    def is_humid(self, biome: Biome) -> bool:
        """Check if a biome is humid."""
        return biome.humidity > 0.7
    
    def is_dry(self, biome: Biome) -> bool:
        """Check if a biome is dry."""
        return biome.humidity < 0.3
    
    def get_biome_count(self) -> int:
        """Get the total number of loaded biomes."""
        return len(self._biomes)
    
    def clear(self) -> None:
        """Clear all biome data."""
        self._biomes.clear()
    
    def __repr__(self) -> str:
        return f"BiomeManager(biomes={self.get_biome_count()})"
