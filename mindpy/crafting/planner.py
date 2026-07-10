"""
Craft planner for MindPy.

Provides craft tree generation and planning for complex crafting operations.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque

from mindpy.crafting.recipe import Recipe, RecipeRegistry
from mindpy.inventory.inventory import Inventory
from mindpy.logging import get_logger


@dataclass
class CraftStep:
    """
    A single step in a crafting plan.
    
    Represents one crafting operation in the craft tree.
    """
    recipe_id: str
    result_item_id: str
    count: int
    depth: int = 0
    dependencies: List[str] = field(default_factory=list)
    completed: bool = False
    
    def __repr__(self) -> str:
        return f"CraftStep({self.result_item_id} x{self.count}, depth={self.depth})"


@dataclass
class CraftPlan:
    """
    A complete crafting plan.
    
    Contains all steps needed to craft an item, organized as a tree.
    """
    target_item_id: str
    target_count: int
    steps: List[CraftStep] = field(default_factory=list)
    total_cost: Dict[str, int] = field(default_factory=dict)
    estimated_time: float = 0.0
    
    def get_steps_by_depth(self, depth: int) -> List[CraftStep]:
        """
        Get all steps at a specific depth.
        
        Args:
            depth: Depth level
            
        Returns:
            List of steps at that depth
        """
        return [step for step in self.steps if step.depth == depth]
    
    def get_leaf_steps(self) -> List[CraftStep]:
        """Get all leaf steps (steps with no dependencies)."""
        return [step for step in self.steps if not step.dependencies]
    
    def get_ready_steps(self) -> List[CraftStep]:
        """Get all steps whose dependencies are completed."""
        return [
            step for step in self.steps
            if not step.completed and all(
                dep_step.completed for dep_step in self.steps
                if dep_step.recipe_id in step.dependencies
            )
        ]
    
    def __repr__(self) -> str:
        return f"CraftPlan({self.target_item_id} x{self.target_count}, steps={len(self.steps)})"


class CraftPlanner:
    """
    Plans crafting operations by generating craft trees.
    
    Determines the optimal sequence of crafting operations to produce
    a target item, including all intermediate items.
    """
    
    def __init__(self, recipe_registry: RecipeRegistry):
        """
        Initialize the craft planner.
        
        Args:
            recipe_registry: Recipe registry to use
        """
        self._recipe_registry = recipe_registry
        self._logger = get_logger(__name__)
    
    def plan_craft(
        self,
        target_item_id: str,
        target_count: int,
        inventory: Optional[Inventory] = None
    ) -> Optional[CraftPlan]:
        """
        Generate a crafting plan for an item.
        
        Args:
            target_item_id: Item to craft
            target_count: Number of items to craft
            inventory: Optional inventory to account for existing items
            
        Returns:
            Craft plan or None if not possible
        """
        # Get recipes for the target item
        recipes = self._recipe_registry.get_recipes_for_item(target_item_id)
        
        if not recipes:
            self._logger.error(f"No recipe found for: {target_item_id}")
            return None
        
        # Use the first available recipe (could be optimized)
        recipe = recipes[0]
        
        # Calculate how many times we need to craft
        crafts_needed = (target_count + recipe.result_count - 1) // recipe.result_count
        
        # Build craft tree
        steps = []
        step_id = 0
        
        def add_craft_step(
            item_id: str,
            count: int,
            depth: int,
            dependencies: List[str]
        ) -> str:
            nonlocal step_id
            current_step_id = f"step_{step_id}"
            step_id += 1
            
            # Get recipe for this item
            item_recipes = self._recipe_registry.get_recipes_for_item(item_id)
            if not item_recipes:
                return current_step_id
            
            item_recipe = item_recipes[0]
            crafts_for_item = (count + item_recipe.result_count - 1) // item_recipe.result_count
            
            step = CraftStep(
                recipe_id=item_recipe.recipe_id,
                result_item_id=item_id,
                count=crafts_for_item,
                depth=depth,
                dependencies=dependencies
            )
            steps.append(step)
            
            # Add ingredient steps
            for ingredient in item_recipe.ingredients:
                total_ingredient_count = ingredient.count * crafts_for_item
                
                # Check if we have enough in inventory
                available = 0
                if inventory:
                    available = inventory.count_item(ingredient.item_id)
                
                if available < total_ingredient_count:
                    needed = total_ingredient_count - available
                    add_craft_step(
                        ingredient.item_id,
                        needed,
                        depth + 1,
                        [current_step_id]
                    )
            
            return current_step_id
        
        add_craft_step(target_item_id, target_count, 0, [])
        
        # Calculate total cost
        total_cost = self._calculate_total_cost(steps)
        
        # Estimate time
        estimated_time = sum(
            self._recipe_registry.get_recipe(step.recipe_id).crafting_time * step.count
            for step in steps
        )
        
        return CraftPlan(
            target_item_id=target_item_id,
            target_count=target_count,
            steps=steps,
            total_cost=total_cost,
            estimated_time=estimated_time
        )
    
    def _calculate_total_cost(self, steps: List[CraftStep]) -> Dict[str, int]:
        """
        Calculate the total cost of all raw materials.
        
        Args:
            steps: Craft steps
            
        Returns:
            Dictionary of item_id -> total count
        """
        cost = defaultdict(int)
        
        for step in steps:
            recipe = self._recipe_registry.get_recipe(step.recipe_id)
            if recipe:
                for ingredient in recipe.ingredients:
                    cost[ingredient.item_id] += ingredient.count * step.count
        
        return dict(cost)
    
    def optimize_plan(self, plan: CraftPlan) -> CraftPlan:
        """
        Optimize a crafting plan.
        
        Args:
            plan: Plan to optimize
            
        Returns:
            Optimized plan
        """
        # TODO: Implement optimization logic:
        # - Batch similar crafts
        # - Reorder for efficiency
        # - Minimize machine switches
        
        return plan
    
    def get_missing_materials(
        self,
        plan: CraftPlan,
        inventory: Inventory
    ) -> Dict[str, int]:
        """
        Get missing materials for a plan.
        
        Args:
            plan: Craft plan
            inventory: Inventory to check
            
        Returns:
            Dictionary of missing item_id -> count
        """
        missing = {}
        
        for item_id, count in plan.total_cost.items():
            available = inventory.count_item(item_id)
            if available < count:
                missing[item_id] = count - available
        
        return missing
    
    def can_execute_plan(self, plan: CraftPlan, inventory: Inventory) -> bool:
        """
        Check if a plan can be executed with the given inventory.
        
        Args:
            plan: Craft plan
            inventory: Inventory to check
            
        Returns:
            True if executable
        """
        missing = self.get_missing_materials(plan, inventory)
        return len(missing) == 0
    
    def __repr__(self) -> str:
        return f"CraftPlanner(recipes={self._recipe_registry.get_recipe_count()})"
