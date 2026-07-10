"""
Inventory manager for MindPy.

Manages multiple inventories including player inventory, equipment, and storage.
"""

from typing import Dict, Optional, List
from mindpy.inventory.inventory import Inventory, ItemStack, EquipmentSlot
from mindpy.logging import get_logger


class InventoryManager:
    """
    Manages all inventories for the bot.
    
    Handles player inventory, equipment, and coordinates inventory operations.
    """
    
    def __init__(self):
        """Initialize the inventory manager."""
        self._player_inventory = Inventory(size=36)
        self._equipment: Dict[EquipmentSlot, Optional[ItemStack]] = {
            slot: None for slot in EquipmentSlot
        }
        self._hotbar_size = 9
        self._selected_hotbar_slot = 0
        self._logger = get_logger(__name__)
    
    def get_player_inventory(self) -> Inventory:
        """Get the player's main inventory."""
        return self._player_inventory
    
    def get_equipment(self, slot: EquipmentSlot) -> Optional[ItemStack]:
        """
        Get equipment in a specific slot.
        
        Args:
            slot: Equipment slot
            
        Returns:
            Item stack or None
        """
        return self._equipment.get(slot)
    
    def set_equipment(self, slot: EquipmentSlot, item_stack: Optional[ItemStack]) -> None:
        """
        Set equipment in a specific slot.
        
        Args:
            slot: Equipment slot
            item_stack: Item stack to equip
        """
        self._equipment[slot] = item_stack
    
    def equip_item(self, item_stack: ItemStack, slot: EquipmentSlot) -> bool:
        """
        Equip an item in a specific slot.
        
        Args:
            item_stack: Item stack to equip
            slot: Equipment slot
            
        Returns:
            True if successful
        """
        # Remove from inventory first
        if self._player_inventory.has_item(item_stack.item_id, item_stack.count):
            self._player_inventory.remove_item(item_stack.item_id, item_stack.count)
            self._equipment[slot] = item_stack
            return True
        return False
    
    def unequip_item(self, slot: EquipmentSlot) -> Optional[ItemStack]:
        """
        Unequip an item from a slot.
        
        Args:
            slot: Equipment slot
            
        Returns:
            Previous item stack or None
        """
        item = self._equipment[slot]
        self._equipment[slot] = None
        
        if item:
            # Add back to inventory
            self._player_inventory.add_item(item)
        
        return item
    
    def get_held_item(self) -> Optional[ItemStack]:
        """Get the item currently held in the main hand."""
        return self._equipment[EquipmentSlot.MAIN_HAND]
    
    def set_held_item(self, item_stack: Optional[ItemStack]) -> None:
        """
        Set the item held in the main hand.
        
        Args:
            item_stack: Item stack to hold
        """
        self._equipment[EquipmentSlot.MAIN_HAND] = item_stack
    
    def select_hotbar_slot(self, slot_index: int) -> bool:
        """
        Select a hotbar slot.
        
        Args:
            slot_index: Hotbar slot index (0-8)
            
        Returns:
            True if successful
        """
        if 0 <= slot_index < self._hotbar_size:
            self._selected_hotbar_slot = slot_index
            
            # Update held item from hotbar
            item = self._player_inventory.get_item(slot_index)
            self._equipment[EquipmentSlot.MAIN_HAND] = item
            
            return True
        return False
    
    def get_selected_hotbar_slot(self) -> int:
        """Get the currently selected hotbar slot."""
        return self._selected_hotbar_slot
    
    def get_hotbar_item(self, slot_index: int) -> Optional[ItemStack]:
        """
        Get the item in a hotbar slot.
        
        Args:
            slot_index: Hotbar slot index
            
        Returns:
            Item stack or None
        """
        return self._player_inventory.get_item(slot_index)
    
    def count_item(self, item_id: str) -> int:
        """
        Count total items across all inventories.
        
        Args:
            item_id: Item ID to count
            
        Returns:
            Total count
        """
        total = self._player_inventory.count_item(item_id)
        
        for item in self._equipment.values():
            if item and item.item_id == item_id:
                total += item.count
        
        return total
    
    def has_item(self, item_id: str, count: int = 1) -> bool:
        """
        Check if the bot has enough of an item.
        
        Args:
            item_id: Item ID to check
            count: Required count
            
        Returns:
            True if has enough
        """
        return self.count_item(item_id) >= count
    
    def find_item(self, item_id: str) -> Optional[ItemStack]:
        """
        Find an item across all inventories.
        
        Args:
            item_id: Item ID to find
            
        Returns:
            Item stack or None
        """
        # Check player inventory
        slot = self._player_inventory.find_item(item_id)
        if slot is not None:
            return self._player_inventory.get_item(slot)
        
        # Check equipment
        for item in self._equipment.values():
            if item and item.item_id == item_id:
                return item
        
        return None
    
    def get_armor_rating(self) -> int:
        """
        Calculate total armor rating.
        
        Returns:
            Total armor points
        """
        # TODO: Implement actual armor calculation based on item types
        rating = 0
        for slot in [EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET]:
            item = self._equipment[slot]
            if item:
                rating += 2  # Placeholder
        return rating
    
    def get_inventory_summary(self) -> Dict[str, any]:
        """
        Get a summary of all inventories.
        
        Returns:
            Dictionary with inventory summary
        """
        return {
            "player_inventory": {
                "size": self._player_inventory.get_size(),
                "used": self._player_inventory.get_used_slots(),
                "empty": self._player_inventory.get_empty_slots()
            },
            "equipment": {
                slot.value: str(item) if item else None
                for slot, item in self._equipment.items()
            },
            "selected_hotbar_slot": self._selected_hotbar_slot
        }
    
    def __repr__(self) -> str:
        return f"InventoryManager(inventory={self._player_inventory})"
