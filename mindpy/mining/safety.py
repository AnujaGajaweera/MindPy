"""
Safety checker for mining operations.

Provides safety checks for mining operations including lava detection,
fall damage prevention, and cave safety.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from mindpy.navigation.movement import Position
from mindpy.logging import get_logger


class SafetyLevel(Enum):
    """Safety levels for mining operations."""
    SAFE = "safe"
    CAUTION = "caution"
    DANGEROUS = "dangerous"
    CRITICAL = "critical"


@dataclass
class SafetyCheck:
    """
    Result of a safety check.
    
    Contains the safety level and any warnings or errors.
    """
    level: SafetyLevel
    warnings: List[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []
    
    def is_safe(self) -> bool:
        """Check if the operation is safe."""
        return self.level == SafetyLevel.SAFE
    
    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self.warnings) > 0
    
    def has_errors(self) -> bool:
        """Check if there are errors."""
        return len(self.errors) > 0


class SafetyChecker:
    """
    Checks safety conditions for mining operations.
    
    Evaluates mining targets for hazards like lava, falls, and caves.
    """
    
    def __init__(self):
        """Initialize the safety checker."""
        self._logger = get_logger(__name__)
        self._lava_y_levels = range(11)  # Y levels 0-10 can have lava
        self._fall_damage_threshold = 4  # Blocks before fall damage
    
    def check_position(self, position: Position) -> SafetyCheck:
        """
        Check the safety of a specific position.
        
        Args:
            position: Position to check
            
        Returns:
            Safety check result
        """
        check = SafetyCheck(level=SafetyLevel.SAFE)
        
        # Check for lava risk
        if position.y in self._lava_y_levels:
            check.warnings.append(f"Lava risk at Y={position.y}")
            check.level = SafetyLevel.CAUTION
        
        # Check for deep mining
        if position.y < 10:
            check.warnings.append(f"Deep mining at Y={position.y}")
            if check.level == SafetyLevel.SAFE:
                check.level = SafetyLevel.CAUTION
        
        # Check for bedrock
        if position.y <= 0:
            check.errors.append("Bedrock layer reached")
            check.level = SafetyLevel.CRITICAL
        
        return check
    
    def check_mining_path(
        self,
        start: Position,
        end: Position,
        blocks: List[Position]
    ) -> SafetyCheck:
        """
        Check the safety of a mining path.
        
        Args:
            start: Starting position
            end: Ending position
            blocks: Blocks to be mined
            
        Returns:
            Safety check result
        """
        check = SafetyCheck(level=SafetyLevel.SAFE)
        
        # Check each block
        for block in blocks:
            block_check = self.check_position(block)
            
            # Merge warnings and errors
            check.warnings.extend(block_check.warnings)
            check.errors.extend(block_check.errors)
            
            # Update safety level if worse
            if block_check.level.value > check.level.value:
                check.level = block_check.level
        
        # Check for fall risk
        fall_risk = self._check_fall_risk(blocks)
        if fall_risk:
            check.warnings.append(f"Fall risk detected: {fall_risk} blocks")
            if check.level == SafetyLevel.SAFE:
                check.level = SafetyLevel.CAUTION
        
        return check
    
    def _check_fall_risk(self, blocks: List[Position]) -> int:
        """
        Check for fall risk in a set of blocks.
        
        Args:
            blocks: Blocks to check
            
        Returns:
            Maximum fall distance
        """
        if not blocks:
            return 0
        
        # Find the lowest Y level
        min_y = min(block.y for block in blocks)
        
        # Calculate potential fall distance
        max_fall = 0
        for block in blocks:
            fall_distance = block.y - min_y
            if fall_distance > max_fall:
                max_fall = fall_distance
        
        return max_fall
    
    def check_lava_proximity(
        self,
        position: Position,
        known_lava: List[Position]
    ) -> SafetyCheck:
        """
        Check proximity to known lava sources.
        
        Args:
            position: Position to check
            known_lava: Known lava positions
            
        Returns:
            Safety check result
        """
        check = SafetyCheck(level=SafetyLevel.SAFE)
        
        for lava_pos in known_lava:
            distance = position.distance_to(lava_pos)
            
            if distance < 3:
                check.errors.append(f"Lava within {distance:.1f} blocks")
                check.level = SafetyLevel.CRITICAL
            elif distance < 5:
                check.warnings.append(f"Lava within {distance:.1f} blocks")
                if check.level == SafetyLevel.SAFE:
                    check.level = SafetyLevel.CAUTION
        
        return check
    
    def check_cave_safety(
        self,
        position: Position,
        cave_size: int
    ) -> SafetyCheck:
        """
        Check safety of entering a cave.
        
        Args:
            position: Cave entrance position
            cave_size: Estimated size of the cave
            
        Returns:
            Safety check result
        """
        check = SafetyCheck(level=SafetyLevel.SAFE)
        
        # Large caves are more dangerous
        if cave_size > 100:
            check.warnings.append("Large cave detected")
            check.level = SafetyLevel.CAUTION
        
        # Deep caves are more dangerous
        if position.y < 20:
            check.warnings.append(f"Deep cave at Y={position.y}")
            if check.level == SafetyLevel.SAFE:
                check.level = SafetyLevel.CAUTION
        
        # Very deep caves are dangerous
        if position.y < 10:
            check.errors.append(f"Very deep cave at Y={position.y}")
            check.level = SafetyLevel.DANGEROUS
        
        return check
    
    def recommend_safety_measures(self, check: SafetyCheck) -> List[str]:
        """
        Recommend safety measures based on a safety check.
        
        Args:
            check: Safety check result
            
        Returns:
            List of recommended measures
        """
        measures = []
        
        if check.level == SafetyLevel.CAUTION:
            measures.append("Place torches for lighting")
            measures.append("Keep water bucket ready")
            measures.append("Block off potential lava sources")
        
        elif check.level == SafetyLevel.DANGEROUS:
            measures.extend([
                "Place torches for lighting",
                "Keep water bucket ready",
                "Block off potential lava sources",
                "Use scaffolding for safe movement",
                "Consider bringing armor"
            ])
        
        elif check.level == SafetyLevel.CRITICAL:
            measures.extend([
                "Do not proceed without proper preparation",
                "Bring full armor and weapons",
                "Keep water bucket ready",
                "Use scaffolding for safe movement",
                "Consider bringing backup supplies"
            ])
        
        return measures
    
    def __repr__(self) -> str:
        return "SafetyChecker()"
