"""
Inventory implementation for MindPy.

Provides inventory management and item stack operations.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple
from enum import Enum


class EquipmentSlot(Enum):
    """Equipment slots for armor and held items."""
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    HEAD = "head"
    CHEST = "chest"
    LEGS = "legs"
    FEET = "feet"


@dataclass
class ItemStack:
    """
    A stack of items in an inventory.
    
    Represents a quantity of a specific item type.
    """
    item_id: str
    count: int = 1
    max_count: int = 64
    display_name: str = ""
    nbt: Optional[Dict] = None
    
    def __post_init__(self):
        """Validate item stack after initialization."""
        if not self.display_name:
            self.display_name = self.item_id
        if self.nbt is None:
            self.nbt = {}
        self.count = max(0, min(self.count, self.max_count))
    
    def add(self, amount: int) -> int:
        """
        Add items to the stack.
        
        Args:
            amount: Number of items to add
            
        Returns:
            Number of items that couldn't be added (overflow)
        """
        space = self.max_count - self.count
        to_add = min(space, amount)
        self.count += to_add
        return amount - to_add
    
    def remove(self, amount: int) -> int:
        """
        Remove items from the stack.
        
        Args:
            amount: Number of items to remove
            
        Returns:
            Number of items that couldn't be removed (underflow)
        """
        to_remove = min(self.count, amount)
        self.count -= to_remove
        return amount - to_remove
    
    def is_empty(self) -> bool:
        """Check if the stack is empty."""
        return self.count <= 0
    
    def is_full(self) -> bool:
        """Check if the stack is full."""
        return self.count >= self.max_count
    
    def can_merge(self, other: 'ItemStack') -> bool:
        """
        Check if this stack can merge with another.
        
        Args:
            other: Other item stack
            
        Returns:
            True if mergeable
        """
        return (
            self.item_id == other.item_id and
            self.nbt == other.nbt and
            not self.is_full()
        )
    
    def merge(self, other: 'ItemStack') -> int:
        """
        Merge another stack into this one.
        
        Args:
            other: Other item stack
            
        Returns:
            Number of items that couldn't be merged
        """
        if not self.can_merge(other):
            return other.count
        
        overflow = self.add(other.count)
        other.count = overflow
        return overflow
    
    def split(self, amount: int) -> 'ItemStack':
        """
        Split the stack.
        
        Args:
            amount: Number of items to split off
            
        Returns:
            New item stack with split items
        """
        to_split = min(self.count, amount)
        self.count -= to_split
        
        return ItemStack(
            item_id=self.item_id,
            count=to_split,
            max_count=self.max_count,
            display_name=self.display_name,
            nbt=self.nbt.copy()
        )
    
    def __repr__(self) -> str:
        return f"ItemStack({self.display_name} x{self.count})"
    
    def __eq__(self, other: 'ItemStack') -> bool:
        return (
            self.item_id == other.item_id and
            self.count == other.count and
            self.nbt == other.nbt
        )


@dataclass
class Slot:
    """
    An inventory slot.
    
    Contains an item stack and slot metadata.
    """
    slot_index: int
    item_stack: Optional[ItemStack] = None
    
    def is_empty(self) -> bool:
        """Check if the slot is empty."""
        return self.item_stack is None or self.item_stack.is_empty()
    
    def get_item(self) -> Optional[ItemStack]:
        """Get the item stack in the slot."""
        if self.item_stack and not self.item_stack.is_empty():
            return self.item_stack
        return None
    
    def set_item(self, item_stack: Optional[ItemStack]) -> None:
        """
        Set the item stack in the slot.
        
        Args:
            item_stack: Item stack to set
        """
        if item_stack and item_stack.is_empty():
            self.item_stack = None
        else:
            self.item_stack = item_stack
    
    def clear(self) -> Optional[ItemStack]:
        """
        Clear the slot and return the item stack.
        
        Returns:
            Previous item stack or None
        """
        previous = self.item_stack
        self.item_stack = None
        return previous
    
    def __repr__(self) -> str:
        return f"Slot({self.slot_index}, {self.item_stack})"


class Inventory:
    """
    Represents a Minecraft inventory.
    
    Manages slots, item stacks, and inventory operations.
    """
    
    def __init__(self, size: int = 36):
        """
        Initialize the inventory.
        
        Args:
            size: Number of slots in the inventory
        """
        self._size = size
        self._slots: Dict[int, Slot] = {i: Slot(i) for i in range(size)}
    
    def get_slot(self, slot_index: int) -> Optional[Slot]:
        """
        Get a slot by index.
        
        Args:
            slot_index: Slot index
            
        Returns:
            Slot or None if invalid index
        """
        return self._slots.get(slot_index)
    
    def set_slot(self, slot_index: int, item_stack: Optional[ItemStack]) -> bool:
        """
        Set a slot's item stack.
        
        Args:
            slot_index: Slot index
            item_stack: Item stack to set
            
        Returns:
            True if successful, False if invalid index
        """
        if slot_index not in self._slots:
            return False
        
        self._slots[slot_index].set_item(item_stack)
        return True
    
    def get_item(self, slot_index: int) -> Optional[ItemStack]:
        """
        Get the item stack in a slot.
        
        Args:
            slot_index: Slot index
            
        Returns:
            Item stack or None
        """
        slot = self.get_slot(slot_index)
        if slot:
            return slot.get_item()
        return None
    
    def add_item(self, item_stack: ItemStack) -> Tuple[int, List[int]]:
        """
        Add an item stack to the inventory.
        
        Args:
            item_stack: Item stack to add
            
        Returns:
            Tuple of (remaining_count, affected_slots)
        """
        remaining = item_stack.count
        affected_slots = []
        
        # First, try to merge with existing stacks
        for slot_index in range(self._size):
            slot = self._slots[slot_index]
            existing = slot.get_item()
            
            if existing and existing.can_merge(item_stack):
                overflow = existing.merge(item_stack)
                affected_slots.append(slot_index)
                remaining = overflow
                
                if remaining == 0:
                    break
        
        # If still items remaining, find empty slots
        if remaining > 0:
            for slot_index in range(self._size):
                slot = self._slots[slot_index]
                
                if slot.is_empty():
                    new_stack = ItemStack(
                        item_id=item_stack.item_id,
                        count=remaining,
                        max_count=item_stack.max_count,
                        display_name=item_stack.display_name,
                        nbt=item_stack.nbt.copy()
                    )
                    slot.set_item(new_stack)
                    affected_slots.append(slot_index)
                    remaining = 0
                    break
        
        return (remaining, affected_slots)
    
    def remove_item(self, item_id: str, count: int = 1) -> Tuple[int, List[int]]:
        """
        Remove items from the inventory.
        
        Args:
            item_id: Item ID to remove
            count: Number of items to remove
            
        Returns:
            Tuple of (remaining_count, affected_slots)
        """
        remaining = count
        affected_slots = []
        
        for slot_index in range(self._size):
            if remaining <= 0:
                break
            
            slot = self._slots[slot_index]
            existing = slot.get_item()
            
            if existing and existing.item_id == item_id:
                removed = existing.remove(remaining)
                remaining -= (count - removed)
                affected_slots.append(slot_index)
                
                if existing.is_empty():
                    slot.clear()
        
        return (remaining, affected_slots)
    
    def count_item(self, item_id: str) -> int:
        """
        Count the total number of an item in the inventory.
        
        Args:
            item_id: Item ID to count
            
        Returns:
            Total count
        """
        total = 0
        for slot in self._slots.values():
            item = slot.get_item()
            if item and item.item_id == item_id:
                total += item.count
        return total
    
    def has_item(self, item_id: str, count: int = 1) -> bool:
        """
        Check if the inventory has enough of an item.
        
        Args:
            item_id: Item ID to check
            count: Required count
            
        Returns:
            True if has enough
        """
        return self.count_item(item_id) >= count
    
    def find_item(self, item_id: str) -> Optional[int]:
        """
        Find the first slot containing an item.
        
        Args:
            item_id: Item ID to find
            
        Returns:
            Slot index or None if not found
        """
        for slot_index, slot in self._slots.items():
            item = slot.get_item()
            if item and item.item_id == item_id:
                return slot_index
        return None
    
    def find_empty_slot(self) -> Optional[int]:
        """
        Find the first empty slot.
        
        Returns:
            Slot index or None if no empty slots
        """
        for slot_index, slot in self._slots.items():
            if slot.is_empty():
                return slot_index
        return None
    
    def swap_slots(self, slot_a: int, slot_b: int) -> bool:
        """
        Swap items between two slots.
        
        Args:
            slot_a: First slot index
            slot_b: Second slot index
            
        Returns:
            True if successful
        """
        if slot_a not in self._slots or slot_b not in self._slots:
            return False
        
        item_a = self._slots[slot_a].get_item()
        item_b = self._slots[slot_b].get_item()
        
        self._slots[slot_a].set_item(item_b)
        self._slots[slot_b].set_item(item_a)
        
        return True
    
    def clear_slot(self, slot_index: int) -> bool:
        """
        Clear a slot.
        
        Args:
            slot_index: Slot index to clear
            
        Returns:
            True if successful
        """
        if slot_index not in self._slots:
            return False
        
        self._slots[slot_index].clear()
        return True
    
    def clear(self) -> None:
        """Clear all slots."""
        for slot in self._slots.values():
            slot.clear()
    
    def get_size(self) -> int:
        """Get the inventory size."""
        return self._size
    
    def is_empty(self) -> bool:
        """Check if the inventory is empty."""
        return all(slot.is_empty() for slot in self._slots.values())
    
    def is_full(self) -> bool:
        """Check if the inventory is full."""
        return not any(slot.is_empty() for slot in self._slots.values())
    
    def get_used_slots(self) -> int:
        """Get the number of used slots."""
        return sum(1 for slot in self._slots.values() if not slot.is_empty())
    
    def get_empty_slots(self) -> int:
        """Get the number of empty slots."""
        return sum(1 for slot in self._slots.values() if slot.is_empty())
    
    def __repr__(self) -> str:
        return f"Inventory(size={self._size}, used={self.get_used_slots()})"
