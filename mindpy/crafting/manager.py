"""
Crafting manager for MindPy.

Manages crafting operations and recipe execution.
"""

from typing import Optional, Dict, List
from mindpy.crafting.recipe import Recipe, RecipeRegistry, RecipeType
from mindpy.inventory.inventory import Inventory
from mindpy.logging import get_logger


class CraftingManager:
    """
    Manages crafting operations for the bot.
    
    Handles recipe lookup, crafting execution, and machine management.
    """
    
    def __init__(self):
        """Initialize the crafting manager."""
        self._recipe_registry = RecipeRegistry()
        self._logger = get_logger(__name__)
        self._current_crafting: Optional[Recipe] = None
        self._crafting_progress: float = 0.0
    
    def register_recipe(self, recipe: Recipe) -> None:
        """
        Register a crafting recipe.
        
        Args:
            recipe: Recipe to register
        """
        self._recipe_registry.register(recipe)
        self._logger.info(f"Registered recipe: {recipe.recipe_id}")
    
    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """
        Get a recipe by ID.
        
        Args:
            recipe_id: Recipe ID
            
        Returns:
            Recipe or None if not found
        """
        return self._recipe_registry.get_recipe(recipe_id)
    
    def get_recipes_for_item(self, item_id: str) -> List[Recipe]:
        """
        Get all recipes that produce an item.
        
        Args:
            item_id: Item ID
            
        Returns:
            List of recipes
        """
        return self._recipe_registry.get_recipes_for_item(item_id)
    
    def can_craft(self, recipe_id: str, inventory: Inventory) -> bool:
        """
        Check if a recipe can be crafted.
        
        Args:
            recipe_id: Recipe ID
            inventory: Inventory to check
            
        Returns:
            True if craftable
        """
        recipe = self._recipe_registry.get_recipe(recipe_id)
        if not recipe:
            return False
        return recipe.can_craft(inventory)
    
    async def craft(
        self,
        recipe_id: str,
        inventory: Inventory,
        count: int = 1
    ) -> bool:
        """
        Craft an item using a recipe.
        
        Args:
            recipe_id: Recipe ID
            inventory: Inventory to use
            count: Number of items to craft
            
        Returns:
            True if successful
        """
        recipe = self._recipe_registry.get_recipe(recipe_id)
        if not recipe:
            self._logger.error(f"Recipe not found: {recipe_id}")
            return False
        
        for _ in range(count):
            if not await self._craft_single(recipe, inventory):
                return False
        
        return True
    
    async def _craft_single(self, recipe: Recipe, inventory: Inventory) -> bool:
        """
        Craft a single item.
        
        Args:
            recipe: Recipe to use
            inventory: Inventory to use
            
        Returns:
            True if successful
        """
        # Check if we can craft
        if not recipe.can_craft(inventory):
            self._logger.warning(f"Cannot craft {recipe.recipe_id}: missing ingredients")
            return False
        
        # Remove ingredients
        for ingredient in recipe.ingredients:
            inventory.remove_item(ingredient.item_id, ingredient.count)
        
        # Add result
        result_stack = type(inventory).__bases__[0].__subclasses__()[0].__dict__['ItemStack']
        # Actually, let's just import ItemStack properly
        from mindpy.inventory.inventory import ItemStack
        result = ItemStack(
            item_id=recipe.result_item_id,
            count=recipe.result_count
        )
        inventory.add_item(result)
        
        self._logger.info(f"Crafted {recipe.result_item_id} x{recipe.result_count}")
        return True
    
    async def craft_item(
        self,
        item_id: str,
        inventory: Inventory,
        count: int = 1
    ) -> bool:
        """
        Craft an item by finding an appropriate recipe.
        
        Args:
            item_id: Item ID to craft
            inventory: Inventory to use
            count: Number of items to craft
            
        Returns:
            True if successful
        """
        recipes = self._recipe_registry.get_recipes_for_item(item_id)
        
        if not recipes:
            self._logger.error(f"No recipe found for: {item_id}")
            return False
        
        # Try each recipe until one works
        for recipe in recipes:
            if await self.craft(recipe.recipe_id, inventory, count):
                return True
        
        return False
    
    def get_missing_ingredients(
        self,
        recipe_id: str,
        inventory: Inventory
    ) -> List[Dict[str, int]]:
        """
        Get missing ingredients for a recipe.
        
        Args:
            recipe_id: Recipe ID
            inventory: Inventory to check
            
        Returns:
            List of missing ingredient info
        """
        recipe = self._recipe_registry.get_recipe(recipe_id)
        if not recipe:
            return []
        
        missing = recipe.get_missing_ingredients(inventory)
        return [
            {"item_id": ing.item_id, "count": ing.count}
            for ing in missing
        ]
    
    def search_recipes(self, query: str) -> List[Recipe]:
        """
        Search recipes by query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching recipes
        """
        return self._recipe_registry.search_recipes(query)
    
    def get_all_recipes(self) -> List[Recipe]:
        """Get all registered recipes."""
        return self._recipe_registry.get_all_recipes()
    
    def get_recipe_count(self) -> int:
        """Get the total number of recipes."""
        return self._recipe_registry.get_recipe_count()
    
    def __repr__(self) -> str:
        return f"CraftingManager(recipes={self.get_recipe_count()})"
