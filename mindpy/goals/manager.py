"""
Goal manager for MindPy.

Manages hierarchical goals, their decomposition, and execution.
"""

import asyncio
from typing import Dict, List, Optional, Set
from collections import defaultdict

from mindpy.goals.goal import Goal, GoalStatus, GoalPriority
from mindpy.goals.decomposer import GoalDecomposer, GoalDecompositionStrategy
from mindpy.events import EventBus, Event, EventTypes
from mindpy.logging import get_logger


class GoalManager:
    """
    Manages hierarchical goals for the bot.
    
    Handles goal creation, decomposition, tracking, and completion.
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Initialize the goal manager.
        
        Args:
            event_bus: The event bus for goal events
        """
        self._event_bus = event_bus
        self._goals: Dict[str, Goal] = {}
        self._decomposer = GoalDecomposer()
        self._active_goal_id: Optional[str] = None
        self._logger = get_logger(__name__)
        
        # Register default strategy
        from mindpy.goals.decomposer import ExampleDecompositionStrategy
        self._decomposer.set_default_strategy(ExampleDecompositionStrategy())
    
    def create_goal(
        self,
        name: str,
        description: str = "",
        priority: GoalPriority = GoalPriority.NORMAL,
        parent_goal_id: Optional[str] = None,
        **metadata
    ) -> Goal:
        """
        Create a new goal.
        
        Args:
            name: Goal name
            description: Goal description
            priority: Goal priority
            parent_goal_id: Optional parent goal ID
            **metadata: Additional metadata
            
        Returns:
            The created goal
        """
        goal = Goal(
            name=name,
            description=description,
            priority=priority,
            parent_goal_id=parent_goal_id,
            metadata=metadata
        )
        
        self._goals[goal.goal_id] = goal
        
        # Add to parent if specified
        if parent_goal_id and parent_goal_id in self._goals:
            self._goals[parent_goal_id].add_sub_goal(goal.goal_id)
        
        # Publish event
        asyncio.create_task(self._event_bus.publish(Event(
            event_type=EventTypes.GOAL_CREATED,
            data={
                "goal_id": goal.goal_id,
                "name": name,
                "priority": priority.value
            },
            source="goal_manager"
        )))
        
        self._logger.info(f"Created goal: {name}")
        return goal
    
    async def decompose_goal(
        self,
        goal_id: str,
        context: Optional[Dict] = None
    ) -> List[Goal]:
        """
        Decompose a goal into sub-goals.
        
        Args:
            goal_id: ID of the goal to decompose
            context: Additional context for decomposition
            
        Returns:
            List of sub-goals
        """
        goal = self._goals.get(goal_id)
        if not goal:
            return []
        
        sub_goals = await self._decomposer.decompose(goal, context)
        
        for sub_goal in sub_goals:
            self._goals[sub_goal.goal_id] = sub_goal
            goal.add_sub_goal(sub_goal.goal_id)
        
        self._logger.info(f"Decomposed goal {goal.name} into {len(sub_goals)} sub-goals")
        return sub_goals
    
    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """
        Get a goal by ID.
        
        Args:
            goal_id: Goal ID
            
        Returns:
            Goal or None if not found
        """
        return self._goals.get(goal_id)
    
    def get_active_goal(self) -> Optional[Goal]:
        """
        Get the currently active goal.
        
        Returns:
            Active goal or None
        """
        if self._active_goal_id:
            return self._goals.get(self._active_goal_id)
        return None
    
    def set_active_goal(self, goal_id: str) -> bool:
        """
        Set the active goal.
        
        Args:
            goal_id: Goal ID to set as active
            
        Returns:
            True if successful, False if not found
        """
        if goal_id in self._goals:
            self._active_goal_id = goal_id
            goal = self._goals[goal_id]
            goal.mark_started()
            return True
        return False
    
    def update_goal_status(
        self,
        goal_id: str,
        status: GoalStatus,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update the status of a goal.
        
        Args:
            goal_id: Goal ID
            status: New status
            error_message: Optional error message
            
        Returns:
            True if updated, False if not found
        """
        goal = self._goals.get(goal_id)
        if not goal:
            return False
        
        old_status = goal.status
        goal.status = status
        
        if status == GoalStatus.COMPLETED:
            goal.mark_completed()
            asyncio.create_task(self._event_bus.publish(Event(
                event_type=EventTypes.GOAL_COMPLETED,
                data={"goal_id": goal_id, "name": goal.name},
                source="goal_manager"
            )))
            self._logger.info(f"Goal completed: {goal.name}")
        
        elif status == GoalStatus.FAILED:
            goal.mark_failed(error_message)
            asyncio.create_task(self._event_bus.publish(Event(
                event_type=EventTypes.GOAL_FAILED,
                data={
                    "goal_id": goal_id,
                    "name": goal.name,
                    "error": error_message
                },
                source="goal_manager"
            )))
            self._logger.error(f"Goal failed: {goal.name} - {error_message}")
        
        elif status == GoalStatus.ABORTED:
            goal.mark_aborted()
            asyncio.create_task(self._event_bus.publish(Event(
                event_type=EventTypes.GOAL_ABORTED,
                data={"goal_id": goal_id, "name": goal.name},
                source="goal_manager"
            )))
        
        return True
    
    def update_goal_progress(self, goal_id: str, progress: float) -> bool:
        """
        Update the progress of a goal.
        
        Args:
            goal_id: Goal ID
            progress: Progress value (0.0 to 1.0)
            
        Returns:
            True if updated, False if not found
        """
        goal = self._goals.get(goal_id)
        if goal:
            goal.update_progress(progress)
            return True
        return False
    
    def get_goals_by_status(self, status: GoalStatus) -> List[Goal]:
        """
        Get all goals with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of goals
        """
        return [g for g in self._goals.values() if g.status == status]
    
    def get_goals_by_priority(self, priority: GoalPriority) -> List[Goal]:
        """
        Get all goals with a specific priority.
        
        Args:
            priority: Priority to filter by
            
        Returns:
            List of goals
        """
        return [g for g in self._goals.values() if g.priority == priority]
    
    def get_root_goals(self) -> List[Goal]:
        """Get all root goals (goals without parents)."""
        return [g for g in self._goals.values() if g.is_root()]
    
    def get_leaf_goals(self) -> List[Goal]:
        """Get all leaf goals (goals without sub-goals)."""
        return [g for g in self._goals.values() if g.is_leaf()]
    
    def get_sub_goals(self, goal_id: str) -> List[Goal]:
        """
        Get all sub-goals of a goal.
        
        Args:
            goal_id: Parent goal ID
            
        Returns:
            List of sub-goals
        """
        goal = self._goals.get(goal_id)
        if not goal:
            return []
        
        return [self._goals[sub_id] for sub_id in goal.sub_goal_ids if sub_id in self._goals]
    
    def get_goal_tree(self, goal_id: str) -> Dict[str, Any]:
        """
        Get the full goal tree for a goal.
        
        Args:
            goal_id: Root goal ID
            
        Returns:
            Dictionary representing the goal tree
        """
        goal = self._goals.get(goal_id)
        if not goal:
            return {}
        
        tree = {
            "goal_id": goal.goal_id,
            "name": goal.name,
            "description": goal.description,
            "status": goal.status.value,
            "priority": goal.priority.value,
            "progress": goal.progress,
            "sub_goals": []
        }
        
        for sub_id in goal.sub_goal_ids:
            if sub_id in self._goals:
                tree["sub_goals"].append(self.get_goal_tree(sub_id))
        
        return tree
    
    def remove_goal(self, goal_id: str) -> bool:
        """
        Remove a goal and all its sub-goals.
        
        Args:
            goal_id: Goal ID to remove
            
        Returns:
            True if removed, False if not found
        """
        goal = self._goals.get(goal_id)
        if not goal:
            return False
        
        # Remove sub-goals recursively
        for sub_id in goal.sub_goal_ids:
            self.remove_goal(sub_id)
        
        # Remove from parent
        if goal.parent_goal_id and goal.parent_goal_id in self._goals:
            parent = self._goals[goal.parent_goal_id]
            parent.sub_goal_ids.remove(goal_id)
        
        # Remove the goal
        del self._goals[goal_id]
        
        # Clear active if this was the active goal
        if self._active_goal_id == goal_id:
            self._active_goal_id = None
        
        return True
    
    def get_goal_count(self) -> int:
        """Get the total number of goals."""
        return len(self._goals)
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get goal statistics.
        
        Returns:
            Dictionary with goal counts by status
        """
        stats = {
            "total": len(self._goals),
            "pending": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0,
            "aborted": 0,
            "blocked": 0
        }
        
        for goal in self._goals.values():
            status = goal.status.value
            if status in stats:
                stats[status] += 1
        
        return stats
    
    def register_decomposition_strategy(
        self,
        goal_type: str,
        strategy: GoalDecompositionStrategy
    ) -> None:
        """
        Register a decomposition strategy for a goal type.
        
        Args:
            goal_type: The goal type
            strategy: The decomposition strategy
        """
        self._decomposer.register_strategy(goal_type, strategy)
    
    def clear(self) -> None:
        """Clear all goals."""
        self._goals.clear()
        self._active_goal_id = None
    
    def __repr__(self) -> str:
        return f"GoalManager(goals={self.get_goal_count()}, active={self._active_goal_id})"
