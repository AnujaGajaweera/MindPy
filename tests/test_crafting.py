"""
Tests for the crafting system.
"""

import pytest
from mindpy.crafting import Recipe, RecipeType, RecipeRegistry, CraftingManager, Ingredient


class TestIngredient:
    """Test cases for Ingredient."""
    
    @pytest.mark.unit
    def test_ingredient_creation(self):
        """Test creating an ingredient."""
        ingredient = Ingredient(
            item_id="minecraft:stone",
            count=2
        )
        
        assert ingredient.item_id == "minecraft:stone"
        assert ingredient.count == 2


class TestRecipe:
    """Test cases for Recipe."""
    
    @pytest.mark.unit
    def test_recipe_creation(self):
        """Test creating a recipe."""
        ingredients = [
            Ingredient(item_id="minecraft:stone", count=2)
        ]
        
        recipe = Recipe(
            recipe_id="stone_to_cobble",
            result_item_id="minecraft:cobblestone",
            result_count=1,
            ingredients=ingredients,
            recipe_type=RecipeType.CRAFTING_TABLE
        )
        
        assert recipe.recipe_id == "stone_to_cobble"
        assert recipe.result_item_id == "minecraft:cobblestone"
        assert len(recipe.ingredients) == 1
    
    @pytest.mark.unit
    def test_recipe_get_crafting_cost(self):
        """Test getting crafting cost."""
        ingredients = [
            Ingredient(item_id="minecraft:stone", count=2),
            Ingredient(item_id="minecraft:wood", count=1)
        ]
        
        recipe = Recipe(
            recipe_id="test",
            result_item_id="minecraft:test",
            ingredients=ingredients
        )
        
        cost = recipe.get_crafting_cost()
        
        assert cost["minecraft:stone"] == 2
        assert cost["minecraft:wood"] == 1


class TestRecipeRegistry:
    """Test cases for RecipeRegistry."""
    
    @pytest.fixture
    def recipe_registry(self):
        """Create a fresh recipe registry for each test."""
        return RecipeRegistry()
    
    @pytest.mark.unit
    def test_recipe_registry_creation(self, recipe_registry):
        """Test creating a recipe registry."""
        assert recipe_registry is not None
    
    @pytest.mark.unit
    def test_register_recipe(self, recipe_registry):
        """Test registering a recipe."""
        recipe = Recipe(
            recipe_id="test",
            result_item_id="minecraft:test"
        )
        
        recipe_registry.register(recipe)
        
        assert recipe_registry.get_recipe_count() == 1
    
    @pytest.mark.unit
    def test_get_recipe(self, recipe_registry):
        """Test getting a recipe."""
        recipe = Recipe(
            recipe_id="test",
            result_item_id="minecraft:test"
        )
        recipe_registry.register(recipe)
        
        retrieved = recipe_registry.get_recipe("test")
        
        assert retrieved is not None
        assert retrieved.recipe_id == "test"
    
    @pytest.mark.unit
    def test_get_recipes_for_item(self, recipe_registry):
        """Test getting recipes for an item."""
        recipe1 = Recipe(
            recipe_id="test1",
            result_item_id="minecraft:stone"
        )
        recipe2 = Recipe(
            recipe_id="test2",
            result_item_id="minecraft:stone"
        )
        
        recipe_registry.register(recipe1)
        recipe_registry.register(recipe2)
        
        recipes = recipe_registry.get_recipes_for_item("minecraft:stone")
        
        assert len(recipes) == 2
    
    @pytest.mark.unit
    def test_search_recipes(self, recipe_registry):
        """Test searching recipes."""
        recipe = Recipe(
            recipe_id="stone_recipe",
            result_item_id="minecraft:stone"
        )
        recipe_registry.register(recipe)
        
        results = recipe_registry.search_recipes("stone")
        
        assert len(results) == 1


class TestCraftingManager:
    """Test cases for CraftingManager."""
    
    @pytest.fixture
    def crafting_manager(self):
        """Create a fresh crafting manager for each test."""
        return CraftingManager()
    
    @pytest.mark.unit
    def test_crafting_manager_creation(self, crafting_manager):
        """Test creating a crafting manager."""
        assert crafting_manager is not None
    
    @pytest.mark.unit
    def test_register_recipe(self, crafting_manager):
        """Test registering a recipe."""
        recipe = Recipe(
            recipe_id="test",
            result_item_id="minecraft:test"
        )
        
        crafting_manager.register_recipe(recipe)
        
        assert crafting_manager.get_recipe_count() == 1
    
    @pytest.mark.unit
    def test_get_recipe(self, crafting_manager):
        """Test getting a recipe."""
        recipe = Recipe(
            recipe_id="test",
            result_item_id="minecraft:test"
        )
        crafting_manager.register_recipe(recipe)
        
        retrieved = crafting_manager.get_recipe("test")
        
        assert retrieved is not None
    
    @pytest.mark.unit
    async def test_craft(self, crafting_manager):
        """Test crafting an item."""
        from mindpy.inventory import Inventory
        
        recipe = Recipe(
            recipe_id="test",
            result_item_id="minecraft:test",
            ingredients=[]
        )
        crafting_manager.register_recipe(recipe)
        
        inventory = Inventory(size=36)
        success = await crafting_manager.craft("test", inventory)
        
        assert success is True
