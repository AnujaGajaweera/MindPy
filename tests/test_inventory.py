"""
Tests for the inventory system.
"""

import pytest
from mindpy.inventory import Inventory, ItemStack, Slot, InventoryManager


class TestItemStack:
    """Test cases for ItemStack."""
    
    @pytest.mark.unit
    def test_item_stack_creation(self):
        """Test creating an item stack."""
        stack = ItemStack(
            item_id="minecraft:stone",
            count=32
        )
        
        assert stack.item_id == "minecraft:stone"
        assert stack.count == 32
        assert stack.max_count == 64
    
    @pytest.mark.unit
    def test_item_stack_add(self):
        """Test adding items to a stack."""
        stack = ItemStack(item_id="minecraft:stone", count=10)
        overflow = stack.add(20)
        
        assert stack.count == 30
        assert overflow == 0
    
    @pytest.mark.unit
    def test_item_stack_add_overflow(self):
        """Test adding items with overflow."""
        stack = ItemStack(item_id="minecraft:stone", count=60)
        overflow = stack.add(10)
        
        assert stack.count == 64
        assert overflow == 6
    
    @pytest.mark.unit
    def test_item_stack_remove(self):
        """Test removing items from a stack."""
        stack = ItemStack(item_id="minecraft:stone", count=32)
        overflow = stack.remove(10)
        
        assert stack.count == 22
        assert overflow == 0
    
    @pytest.mark.unit
    def test_item_stack_is_empty(self):
        """Test checking if stack is empty."""
        stack = ItemStack(item_id="minecraft:stone", count=0)
        assert stack.is_empty()
    
    @pytest.mark.unit
    def test_item_stack_is_full(self):
        """Test checking if stack is full."""
        stack = ItemStack(item_id="minecraft:stone", count=64)
        assert stack.is_full()
    
    @pytest.mark.unit
    def test_item_stack_can_merge(self):
        """Test checking if stacks can merge."""
        stack1 = ItemStack(item_id="minecraft:stone", count=32)
        stack2 = ItemStack(item_id="minecraft:stone", count=10)
        
        assert stack1.can_merge(stack2)
    
    @pytest.mark.unit
    def test_item_stack_merge(self):
        """Test merging stacks."""
        stack1 = ItemStack(item_id="minecraft:stone", count=32)
        stack2 = ItemStack(item_id="minecraft:stone", count=10)
        
        overflow = stack1.merge(stack2)
        
        assert stack1.count == 42
        assert stack2.count == 0
    
    @pytest.mark.unit
    def test_item_stack_split(self):
        """Test splitting a stack."""
        stack = ItemStack(item_id="minecraft:stone", count=32)
        new_stack = stack.split(10)
        
        assert stack_count == 22
        assert new_stack.count == 10


class TestSlot:
    """Test cases for Slot."""
    
    @pytest.mark.unit
    def test_slot_creation(self):
        """Test creating a slot."""
        slot = Slot(slot_index=0)
        
        assert slot.slot_index == 0
        assert slot.is_empty()
    
    @pytest.mark.unit
    def test_slot_set_item(self):
        """Test setting an item in a slot."""
        slot = Slot(slot_index=0)
        item = ItemStack(item_id="minecraft:stone", count=32)
        
        slot.set_item(item)
        
        assert not slot.is_empty()
        assert slot.get_item().count == 32
    
    @pytest.mark.unit
    def test_slot_clear(self):
        """Test clearing a slot."""
        slot = Slot(slot_index=0)
        item = ItemStack(item_id="minecraft:stone", count=32)
        slot.set_item(item)
        
        previous = slot.clear()
        
        assert slot.is_empty()
        assert previous is not None


class TestInventory:
    """Test cases for Inventory."""
    
    @pytest.fixture
    def inventory(self):
        """Create a fresh inventory for each test."""
        return Inventory(size=36)
    
    @pytest.mark.unit
    def test_inventory_creation(self, inventory):
        """Test creating an inventory."""
        assert inventory.get_size() == 36
        assert inventory.is_empty()
    
    @pytest.mark.unit
    def test_inventory_get_slot(self, inventory):
        """Test getting a slot."""
        slot = inventory.get_slot(0)
        
        assert slot is not None
        assert slot.slot_index == 0
    
    @pytest.mark.unit
    def test_inventory_set_slot(self, inventory):
        """Test setting a slot."""
        item = ItemStack(item_id="minecraft:stone", count=32)
        success = inventory.set_slot(0, item)
        
        assert success is True
        assert inventory.get_item(0).count == 32
    
    @pytest.mark.unit
    def test_inventory_add_item(self, inventory):
        """Test adding an item to inventory."""
        item = ItemStack(item_id="minecraft:stone", count=32)
        remaining, affected = inventory.add_item(item)
        
        assert remaining == 0
        assert len(affected) > 0
    
    @pytest.mark.unit
    def test_inventory_remove_item(self, inventory):
        """Test removing an item from inventory."""
        item = ItemStack(item_id="minecraft:stone", count=32)
        inventory.add_item(item)
        
        remaining, affected = inventory.remove_item("minecraft:stone", 10)
        
        assert remaining == 0
        assert len(affected) > 0
    
    @pytest.mark.unit
    def test_inventory_count_item(self, inventory):
        """Test counting items in inventory."""
        item = ItemStack(item_id="minecraft:stone", count=32)
        inventory.add_item(item)
        
        count = inventory.count_item("minecraft:stone")
        
        assert count == 32
    
    @pytest.mark.unit
    def test_inventory_has_item(self, inventory):
        """Test checking if inventory has an item."""
        item = ItemStack(item_id="minecraft:stone", count=32)
        inventory.add_item(item)
        
        assert inventory.has_item("minecraft:stone", 32)
        assert not inventory.has_item("minecraft:stone", 64)
    
    @pytest.mark.unit
    def test_inventory_find_item(self, inventory):
        """Test finding an item in inventory."""
        item = ItemStack(item_id="minecraft:stone", count=32)
        inventory.set_slot(5, item)
        
        slot = inventory.find_item("minecraft:stone")
        
        assert slot == 5
    
    @pytest.mark.unit
    def test_inventory_swap_slots(self, inventory):
        """Test swapping items between slots."""
        item1 = ItemStack(item_id="minecraft:stone", count=32)
        item2 = ItemStack(item_id="minecraft:dirt", count=16)
        
        inventory.set_slot(0, item1)
        inventory.set_slot(1, item2)
        
        inventory.swap_slots(0, 1)
        
        assert inventory.get_item(0).item_id == "minecraft:dirt"
        assert inventory.get_item(1).item_id == "minecraft:stone"


class TestInventoryManager:
    """Test cases for InventoryManager."""
    
    @pytest.fixture
    def inventory_manager(self):
        """Create a fresh inventory manager for each test."""
        return InventoryManager()
    
    @pytest.mark.unit
    def test_inventory_manager_creation(self, inventory_manager):
        """Test creating an inventory manager."""
        assert inventory_manager is not None
        assert inventory_manager.get_player_inventory() is not None
    
    @pytest.mark.unit
    def test_get_player_inventory(self, inventory_manager):
        """Test getting player inventory."""
        inventory = inventory_manager.get_player_inventory()
        
        assert inventory is not None
        assert isinstance(inventory, Inventory)
    
    @pytest.mark.unit
    def test_count_item(self, inventory_manager):
        """Test counting items across all inventories."""
        player_inv = inventory_manager.get_player_inventory()
        item = ItemStack(item_id="minecraft:stone", count=32)
        player_inv.add_item(item)
        
        count = inventory_manager.count_item("minecraft:stone")
        
        assert count == 32
