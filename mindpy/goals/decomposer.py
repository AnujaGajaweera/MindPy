"""
Goal decomposer for hierarchical goal decomposition.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from mindpy.goals.goal import Goal, GoalStatus, GoalPriority


class GoalDecompositionStrategy(ABC):
    """
    Base class for goal decomposition strategies.
    
    Strategies define how goals are decomposed into sub-goals and tasks.
    """
    
    @abstractmethod
    async def decompose(self, goal: Goal, context: Dict[str, Any]) -> List[Goal]:
        """
        Decompose a goal into sub-goals.
        
        Args:
            goal: The goal to decompose
            context: Additional context for decomposition
            
        Returns:
            List of sub-goals
        """
        pass


class GoalDecomposer:
    """
    Decomposes goals into hierarchical sub-goals.
    
    Uses registered strategies to decompose goals based on their type.
    """
    
    def __init__(self):
        """Initialize the goal decomposer."""
        self._strategies: Dict[str, GoalDecompositionStrategy] = {}
        self._default_strategy: Optional[GoalDecompositionStrategy] = None
    
    def register_strategy(
        self,
        goal_type: str,
        strategy: GoalDecompositionStrategy
    ) -> None:
        """
        Register a decomposition strategy for a goal type.
        
        Args:
            goal_type: The goal type this strategy handles
            strategy: The decomposition strategy
        """
        self._strategies[goal_type] = strategy
    
    def set_default_strategy(self, strategy: GoalDecompositionStrategy) -> None:
        """
        Set the default decomposition strategy.
        
        Args:
            strategy: The default strategy
        """
        self._default_strategy = strategy
    
    async def decompose(
        self,
        goal: Goal,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Goal]:
        """
        Decompose a goal into sub-goals.
        
        Args:
            goal: The goal to decompose
            context: Additional context for decomposition
            
        Returns:
            List of sub-goals
        """
        context = context or {}
        goal_type = goal.metadata.get("type", "default")
        
        strategy = self._strategies.get(goal_type, self._default_strategy)
        
        if strategy:
            sub_goals = await strategy.decompose(goal, context)
            
            # Set parent relationships
            for sub_goal in sub_goals:
                sub_goal.parent_goal_id = goal.goal_id
            
            return sub_goals
        
        return []
    
    def has_strategy(self, goal_type: str) -> bool:
        """
        Check if a strategy is registered for a goal type.
        
        Args:
            goal_type: The goal type to check
            
        Returns:
            True if strategy exists
        """
        return goal_type in self._strategies


class ExampleDecompositionStrategy(GoalDecompositionStrategy):
    """
    Example decomposition strategy for demonstration.
    
    Decomposes goals based on a simple rule-based approach.
    """
    
    async def decompose(self, goal: Goal, context: Dict[str, Any]) -> List[Goal]:
        """
        Decompose a goal using example logic.
        
        Args:
            goal: The goal to decompose
            context: Additional context
            
        Returns:
            List of sub-goals
        """
        sub_goals = []
        
        #Example: Decompose "Collect Diamonds" into sub-goals
        if goal.name == "Collect Diamonds":
            sub_goals.append(Goal(
                name="Acquire Iron Pickaxe",
                description="Get or craft an iron pickaxe",
                priority=GoalPriority.HIGH,
                metadata={"type": "crafting"}
            ))
            sub_goals.append(Goal(
                name="Mine Iron",
                description="Mine iron ore for the pickaxe",
                priority=GoalPriority.HIGH,
                metadata={"type": "mining"}
            ))
            sub_goals.append(Goal(
                name="Craft Furnace",
                description="Craft a furnace for smelting",
                priority=GoalPriority.NORMAL,
                metadata={"type": "crafting"}
            ))
            sub_goals.append(Goal(
                name="Collect Coal",
                description="Find coal for fuel",
                priority=GoalPriority.NORMAL,
                metadata={"type": "mining"}
            ))
            sub_goals.append(Goal(
                name="Mine Stone",
                description="Mine stone for crafting",
                priority=GoalPriority.LOW,
                metadata={"type": "mining"}
            ))
        
        return sub_goals
