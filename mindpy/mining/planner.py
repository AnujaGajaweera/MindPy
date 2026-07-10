"""
Mining planner for MindPy.

Provides mining planning and ore detection strategies.
"""

from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

from mindpy.navigation.movement import Position
from mindpy.mining.miner import BlockTarget, MiningTool
from mindpy.logging import get_logger


class OreType(Enum):
    """Types of ores."""
    COAL = "coal_ore"
    IRON = "iron_ore"
    GOLD = "gold_ore"
    DIAMOND = "diamond_ore"
    REDSTONE = "redstone_ore"
    LAPIS = "lapis_ore"
    EMERALD = "emerald_ore"
    COPPER = "copper_ore"
    NETHER_GOLD = "nether_gold_ore"
    ANCIENT_DEBRIS = "ancient_debris"


@dataclass
class MiningTarget:
    """
    A mining target with priority and metadata.
    
    Represents a block or area to mine with planning information.
    """
    target: BlockTarget
    priority: int = 0
    estimated_yield: int = 1
    required_tool: Optional[MiningTool] = None
    safety_level: int = 0  # 0 = safe, 1 = caution, 2 = dangerous
    
    def __repr__(self) -> str:
        return f"MiningTarget({self.target.block_type}, priority={self.priority})"


@dataclass
class MiningPlan:
    """
    A complete mining plan.
    
    Contains targets, path, and safety considerations.
    """
    targets: List[MiningTarget] = field(default_factory=list)
    total_blocks: int = 0
    estimated_time: float = 0.0
    required_tools: Set[MiningTool] = field(default_factory=set)
    safety_concerns: List[str] = field(default_factory=list)
    
    def add_target(self, target: MiningTarget) -> None:
        """Add a target to the plan."""
        self.targets.append(target)
        self.total_blocks += 1
        if target.required_tool:
            self.required_tools.add(target.required_tool)
    
    def sort_by_priority(self) -> None:
        """Sort targets by priority (highest first)."""
        self.targets.sort(key=lambda t: t.priority, reverse=True)
    
    def get_high_priority_targets(self) -> List[MiningTarget]:
        """Get high priority targets."""
        return [t for t in self.targets if t.priority >= 5]
    
    def __repr__(self) -> str:
        return f"MiningPlan(targets={len(self.targets)}, blocks={self.total_blocks})"


class MiningPlanner:
    """
    Plans mining operations.
    
    Generates efficient mining plans based on ore locations,
    tool availability, and safety considerations.
    """
    
    def __init__(self):
        """Initialize the mining planner."""
        self._ore_y_ranges = {
            OreType.COAL: (5, 66),
            OreType.IRON: (5, 66),
            OreType.GOLD: (5, 32),
            OreType.DIAMOND: (5, 16),
            OreType.REDSTONE: (5, 16),
            OreType.LAPIS: (5, 16),
            OreType.EMERALD: (5, 32),
            OreType.COPPER: (5, 95),
        }
        self._logger = get_logger(__name__)
    
    def plan_mining(
        self,
        target_ores: List[OreType],
        start_position: Position,
        available_tools: List[MiningTool],
        max_depth: int = 60
    ) -> MiningPlan:
        """
        Generate a mining plan for specific ores.
        
        Args:
            target_ores: Types of ores to mine
            start_position: Starting position
            available_tools: Available mining tools
            max_depth: Maximum mining depth
            
        Returns:
            Mining plan
        """
        plan = MiningPlan()
        
        # Determine optimal Y levels for target ores
        y_levels = self._get_optimal_y_levels(target_ores)
        
        # Generate mining targets
        for ore_type in target_ores:
            targets = self._generate_ore_targets(
                ore_type,
                start_position,
                y_levels.get(ore_type, 10),
                available_tools
            )
            for target in targets:
                plan.add_target(target)
        
        # Sort by priority
        plan.sort_by_priority()
        
        # Estimate time
        plan.estimated_time = self._estimate_mining_time(plan)
        
        # Check safety
        plan.safety_concerns = self._check_safety(plan)
        
        self._logger.info(f"Generated mining plan with {len(plan.targets)} targets")
        return plan
    
    def _get_optimal_y_levels(self, ore_types: List[OreType]) -> Dict[OreType, int]:
        """
        Get optimal Y levels for mining specific ores.
        
        Args:
            ore_types: Ore types to mine
            
        Returns:
            Dictionary of ore type -> optimal Y level
        """
        optimal_levels = {}
        
        for ore_type in ore_types:
            if ore_type in self._ore_y_ranges:
                min_y, max_y = self._ore_y_ranges[ore_type]
                # Use the middle of the range as optimal
                optimal_levels[ore_type] = (min_y + max_y) // 2
        
        return optimal_levels
    
    def _generate_ore_targets(
        self,
        ore_type: OreType,
        start_position: Position,
        y_level: int,
        available_tools: List[MiningTool]
    ) -> List[MiningTarget]:
        """
        Generate mining targets for an ore type.
        
        Args:
            ore_type: Type of ore
            start_position: Starting position
            y_level: Target Y level
            available_tools: Available tools
            
        Returns:
            List of mining targets
        """
        targets = []
        
        # Determine required tool
        required_tool = self._get_required_tool(ore_type, available_tools)
        
        # Generate branch mining pattern
        branch_length = 20
        branch_spacing = 3
        
        for branch in range(5):  # 5 branches
            branch_x = start_position.x + (branch * branch_spacing)
            
            for i in range(branch_length):
                target_pos = Position(
                    branch_x,
                    y_level,
                    start_position.z + i
                )
                
                block_target = BlockTarget(
                    position=target_pos,
                    block_type=ore_type.value,
                    hardness=3.0,
                    requires_tool=required_tool
                )
                
                mining_target = MiningTarget(
                    target=block_target,
                    priority=self._get_ore_priority(ore_type),
                    estimated_yield=1,
                    required_tool=required_tool,
                    safety_level=0
                )
                
                targets.append(mining_target)
        
        return targets
    
    def _get_required_tool(
        self,
        ore_type: OreType,
        available_tools: List[MiningTool]
    ) -> Optional[MiningTool]:
        """
        Get the required tool for mining an ore.
        
        Args:
            ore_type: Type of ore
            available_tools: Available tools
            
        Returns:
            Required tool or None
        """
        # Most ores require at least a stone pickaxe
        if ore_type in [OreType.DIAMOND, OreType.GOLD, OreType.EMERALD]:
            if MiningTool.IRON_PICKAXE in available_tools:
                return MiningTool.IRON_PICKAXE
            elif MiningTool.DIAMOND_PICKAXE in available_tools:
                return MiningTool.DIAMOND_PICKAXE
        
        # Default to best available pickaxe
        pickaxes = [
            MiningTool.DIAMOND_PICKAXE,
            MiningTool.IRON_PICKAXE,
            MiningTool.STONE_PICKAXE,
            MiningTool.WOODEN_PICKAXE
        ]
        
        for pickaxe in pickaxes:
            if pickaxe in available_tools:
                return pickaxe
        
        return None
    
    def _get_ore_priority(self, ore_type: OreType) -> int:
        """
        Get the priority of an ore type.
        
        Args:
            ore_type: Type of ore
            
        Returns:
            Priority value (higher = more important)
        """
        priorities = {
            OreType.DIAMOND: 10,
            OreType.EMERALD: 9,
            OreType.GOLD: 8,
            OreType.REDSTONE: 7,
            OreType.LAPIS: 6,
            OreType.IRON: 5,
            OreType.COPPER: 4,
            OreType.COAL: 3,
        }
        return priorities.get(ore_type, 1)
    
    def _estimate_mining_time(self, plan: MiningPlan) -> float:
        """
        Estimate the total time for a mining plan.
        
        Args:
            plan: Mining plan
            
        Returns:
            Estimated time in seconds
        """
        # Simple estimation: 2 seconds per block
        return plan.total_blocks * 2.0
    
    def _check_safety(self, plan: MiningPlan) -> List[str]:
        """
        Check a mining plan for safety concerns.
        
        Args:
            plan: Mining plan
            
        Returns:
            List of safety concerns
        """
        concerns = []
        
        # Check for deep mining
        for target in plan.targets:
            if target.target.position.y < 10:
                concerns.append(f"Deep mining at Y={target.target.position.y}")
        
        # Check for lava risk (simplified)
        for target in plan.targets:
            if target.target.position.y < 12:
                concerns.append(f"Lava risk at Y={target.target.position.y}")
        
        return concerns
    
    def plan_strip_mine(
        self,
        start_position: Position,
        length: int = 50,
        spacing: int = 3,
        branches: int = 5
    ) -> MiningPlan:
        """
        Plan a strip mining operation.
        
        Args:
            start_position: Starting position
            length: Length of each branch
            spacing: Spacing between branches
            branches: Number of branches
            
        Returns:
            Mining plan
        """
        plan = MiningPlan()
        
        for branch in range(branches):
            branch_x = start_position.x + (branch * spacing)
            
            for i in range(length):
                target_pos = Position(
                    branch_x,
                    start_position.y,
                    start_position.z + i
                )
                
                block_target = BlockTarget(
                    position=target_pos,
                    block_type="stone",
                    hardness=1.5
                )
                
                mining_target = MiningTarget(
                    target=block_target,
                    priority=1,
                    estimated_yield=1
                )
                
                plan.add_target(mining_target)
        
        return plan
    
    def __repr__(self) -> str:
        return "MiningPlanner()"
