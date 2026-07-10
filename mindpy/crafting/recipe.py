"""
Recipe system for MindPy.

Provides recipe definitions and lookup.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class RecipeType(Enum):
    """Types of crafting recipes."""
    CRAFTING_TABLE = "crafting_table"
    FURNACE = "furnace"
    BLAST_FURNACE = "blast_furnace"
    SMOKER = "smoker"
    STONECUTTER = "stonecutter"
    SMITHING_TABLE = "smithing_table"


@dataclass
class Ingredient:
    """
    An ingredient in a recipe.
    
    Represents a required item with optional count and tag matching.
    """
    item_id: str
    count: int = 1
    tag: Optional[str] = None  # For tag-based matching
    
    def __repr__(self) -> str:
        return f"Ingredient({self.item_id} x{self.count})"


@dataclass
class Recipe:
    """
    A crafting recipe.
    
    Defines inputs, outputs, and crafting requirements.
    """
    recipe_id: str
    result_item_id: str
    result_count: int = 1
    ingredients: List[Ingredient] = field(default_factory=list)
    recipe_type: RecipeType = RecipeType.CRAFTING_TABLE
    crafting_time: float = 0.0  # In seconds for machines
    experience_reward: float = 0.0
    pattern: Optional[List[List[str]]] = None  # For shaped recipes
    shapeless: bool = False
    metadata: Dict[str, any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate recipe after initialization."""
        if not self.recipe_id:
            raise ValueError("Recipe ID cannot be empty")
        if not self.result_item_id:
            raise ValueError("Result item ID cannot be empty")
        if self.result_count <= 0:
            raise ValueError("Result count must be positive")
    
    def can_craft(self, inventory: 'Inventory') -> bool:
        """
        Check if the recipe can be crafted with the given inventory.
        
        Args:
            inventory: Inventory to check
            
        Returns:
            True if craftable
        """
        from mindpy.inventory.inventory import Inventory
        
        for ingredient in self.ingredients:
            if not inventory.has_item(ingredient.item_id, ingredient.count):
                return False
        return True
    
    def get_missing_ingredients(self, inventory: 'Inventory') -> List[Ingredient]:
        """
        Get missing ingredients for crafting.
        
        Args:
            inventory: Inventory to check
            
        Returns:
            List of missing ingredients
        """
        from mindpy.inventory.inventory import Inventory
        
        missing = []
        for ingredient in self.ingredients:
            available = inventory.count_item(ingredient.item_id)
            if available < ingredient.count:
                missing.append(Ingredient(
                    item_id=ingredient.item_id,
                    count=ingredient.count - available
                ))
        return missing
    
    def get_crafting_cost(self) -> Dict[str, int]:
        """
        Get the total cost of ingredients.
        
        Returns:
            Dictionary of item_id -> total count
        """
        cost = {}
        for ingredient in self.ingredients:
            if ingredient.item_id in cost:
                cost[ingredient.item_id] += ingredient.count
            else:
                cost[ingredient.item_id] = ingredient.count
        return cost
    
    def __repr__(self) -> str:
        return f"Recipe({self.recipe_id}: {self.result_item_id} x{self.result_count})"


class RecipeRegistry:
    """
    Registry of all crafting recipes.
    
    Provides recipe lookup and management.
    """
    
    def __init__(self):
        """Initialize the recipe registry."""
        self._recipes: Dict[str, Recipe] = {}
        self._recipes_by_result: Dict[str, List[str]] = {}
        self._recipes_by_type: Dict[RecipeType, List[str]] = {}
    
    def register(self, recipe: Recipe) -> None:
        """
        Register a recipe.
        
        Args:
            recipe: Recipe to register
        """
        self._recipes[recipe.recipe_id] = recipe
        
        # Index by result
        if recipe.result_item_id not in self._recipes_by_result:
            self._recipes_by_result[recipe.result_item_id] = []
        self._recipes_by_result[recipe.result_item_id].append(recipe.recipe_id)
        
        # Index by type
        if recipe.recipe_type not in self._recipes_by_type:
            self._recipes_by_type[recipe.recipe_type] = []
        self._recipes_by_type[recipe.recipe_type].append(recipe.recipe_id)
    
    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """
        Get a recipe by ID.
        
        Args:
            recipe_id: Recipe ID
            
        Returns:
            Recipe or None if not found
        """
        return self._recipes.get(recipe_id)
    
    def get_recipes_for_item(self, item_id: str) -> List[Recipe]:
        """
        Get all recipes that produce an item.
        
        Args:
            item_id: Item ID
            
        Returns:
            List of recipes
        """
        recipe_ids = self._recipes_by_result.get(item_id, [])
        return [self._recipes[rid] for rid in recipe_ids if rid in self._recipes]
    
    def get_recipes_by_type(self, recipe_type: RecipeType) -> List[Recipe]:
        """
        Get all recipes of a specific type.
        
        Args:
            recipe_type: Recipe type
            
        Returns:
            List of recipes
        """
        recipe_ids = self._recipes_by_type.get(recipe_type, [])
        return [self._recipes[rid] for rid in recipe_ids if rid in self._recipes]
    
    def find_recipe_by_ingredients(self, ingredients: List[str]) -> Optional[Recipe]:
        """
        Find a recipe that matches the given ingredients.
        
        Args:
            ingredients: List of ingredient item IDs
            
        Returns:
            Matching recipe or None
        """
        for recipe in self._recipes.values():
            if recipe.shapeless:
                recipe_ingredients = [ing.item_id for ing in recipe.ingredients]
                if set(recipe_ingredients) == set(ingredients):
                    return recipe
        return None
    
    def search_recipes(self, query: str) -> List[Recipe]:
        """
        Search recipes by item ID or name.
        
        Args:
            query: Search query
            
        Returns:
            List of matching recipes
        """
        query_lower = query.lower()
        results = []
        
        for recipe in self._recipes.values():
            if (query_lower in recipe.result_item_id.lower() or
                query_lower in recipe.recipe_id.lower()):
                results.append(recipe)
        
        return results
    
    def get_all_recipes(self) -> List[Recipe]:
        """Get all registered recipes."""
        return list(self._recipes.values())
    
    def get_recipe_count(self) -> int:
        """Get the total number of recipes."""
        return len(self._recipes)
    
    def clear(self) -> None:
        """Clear all recipes."""
        self._recipes.clear()
        self._recipes_by_result.clear()
        self._recipes_by_type.clear()
    
    def __repr__(self) -> str:
        return f"RecipeRegistry(recipes={self.get_recipe_count()})"
