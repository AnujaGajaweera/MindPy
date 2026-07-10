"""
Chest interaction for MindPy.

Provides chest opening, item transfer, and storage management.
"""

from typing import Optional, List, Tuple
from mindpy.inventory.inventory import Inventory, ItemStack
from mindpy.logging import get_logger


class ChestInteraction:
    """
    Manages chest interactions for the bot.
    
    Handles opening chests, transferring items, and managing storage.
    """
    
    def __init__(self):
        """Initialize the chest interaction manager."""
        self._current_chest: Optional[Inventory] = None
        self._chest_position: Optional[tuple] = None
        self._is_open = False
        self._logger = get_logger(__name__)
    
    async def open_chest(self, position: tuple) -> bool:
        """
        Open a chest at a specific position.
        
        Args:
            position: Chest position (x, y, z)
            
        Returns:
            True if successful
        """
        if self._is_open:
            await self.close_chest()
        
        self._chest_position = position
        self._current_chest = Inventory(size=54)  # Large chest
        self._is_open = True
        
        # TODO: Implement actual chest opening via PyCraft
        self._logger.info(f"Opened chest at {position}")
        
        return True
    
    async def close_chest(self) -> bool:
        """
        Close the currently open chest.
        
        Returns:
            True if successful
        """
        if not self._is_open:
            return False
        
        self._current_chest = None
        self._chest_position = None
        self._is_open = False
        
        # TODO: Implement actual chest closing via PyCraft
        self._logger.info("Closed chest")
        
        return True
    
    def get_chest_inventory(self) -> Optional[Inventory]:
        """Get the currently open chest's inventory."""
        return self._current_chest
    
    def is_chest_open(self) -> bool:
        """Check if a chest is currently open."""
        return self._is_open
    
    def get_chest_position(self) -> Optional[tuple]:
        """Get the position of the currently open chest."""
        return self._chest_position
    
    async def transfer_to_chest(
        self,
        item_stack: ItemStack,
        player_inventory: Inventory
    ) -> Tuple[int, int]:
        """
        Transfer items from player inventory to chest.
        
        Args:
            item_stack: Item stack to transfer
            player_inventory: Player's inventory
            
        Returns:
            Tuple of (transferred_count, remaining_count)
        """
        if not self._is_open or not self._current_chest:
            return (0, item_stack.count)
        
        # Remove from player inventory
        remaining, _ = player_inventory.remove_item(item_stack.item_id, item_stack.count)
        transferred = item_stack.count - remaining
        
        # Add to chest
        if transferred > 0:
            transfer_stack = ItemStack(
                item_id=item_stack.item_id,
                count=transferred,
                max_count=item_stack.max_count,
                display_name=item_stack.display_name,
                nbt=item_stack.nbt.copy()
            )
            chest_remaining, _ = self._current_chest.add_item(transfer_stack)
            transferred -= chest_remaining
        
        # Return overflow to player
        if chest_remaining > 0:
            return_stack = ItemStack(
                item_id=item_stack.item_id,
                count=chest_remaining,
                max_count=item_stack.max_count,
                display_name=item_stack.display_name,
                nbt=item_stack.nbt.copy()
            )
            player_inventory.add_item(return_stack)
        
        self._logger.info(f"Transferred {transferred} {item_stack.item_id} to chest")
        return (transferred, item_stack.count - transferred)
    
    async def transfer_from_chest(
        self,
        item_id: str,
        count: int,
        player_inventory: Inventory
    ) -> Tuple[int, int]:
        """
        Transfer items from chest to player inventory.
        
        Args:
            item_id: Item ID to transfer
            count: Number of items to transfer
            player_inventory: Player's inventory
            
        Returns:
            Tuple of (transferred_count, remaining_count)
        """
        if not self._is_open or not self._current_chest:
            return (0, count)
        
        # Remove from chest
        remaining, _ = self._current_chest.remove_item(item_id, count)
        transferred = count - remaining
        
        # Add to player inventory
        if transferred > 0:
            transfer_stack = ItemStack(
                item_id=item_id,
                count=transferred
            )
            player_remaining, _ = player_inventory.add_item(transfer_stack)
            transferred -= player_remaining
            
            # Return overflow to chest
            if player_remaining > 0:
                return_stack = ItemStack(
                    item_id=item_id,
                    count=player_remaining
                )
                self._current_chest.add_item(return_stack)
        
        self._logger.info(f"Transferred {transferred} {item_id} from chest")
        return (transferred, remaining)
    
    async def deposit_all(
        self,
        player_inventory: Inventory,
        item_id: Optional[str] = None
    ) -> int:
        """
        Deposit all items (or specific item) from player to chest.
        
        Args:
            item_id: Optional item ID to filter by
            player_inventory: Player's inventory
            
        Returns:
            Number of items deposited
        """
        if not self._is_open or not self._current_chest:
            return 0
        
        total_deposited = 0
        
        if item_id:
            # Deposit specific item
            count = player_inventory.count_item(item_id)
            if count > 0:
                transferred, _ = await self.transfer_to_chest(
                    ItemStack(item_id=item_id, count=count),
                    player_inventory
                )
                total_deposited = transferred
        else:
            # Deposit all items
            for slot_index in range(player_inventory.get_size()):
                item = player_inventory.get_item(slot_index)
                if item:
                    transferred, _ = await self.transfer_to_chest(item, player_inventory)
                    total_deposited += transferred
        
        return total_deposited
    
    async def withdraw(
        self,
        item_id: str,
        count: int,
        player_inventory: Inventory
    ) -> int:
        """
        Withdraw items from chest to player inventory.
        
        Args:
            item_id: Item ID to withdraw
            count: Number of items to withdraw
            player_inventory: Player's inventory
            
        Returns:
            Number of items withdrawn
        """
        transferred, _ = await self.transfer_from_chest(item_id, count, player_inventory)
        return transferred
    
    def count_in_chest(self, item_id: str) -> int:
        """
        Count items in the chest.
        
        Args:
            item_id: Item ID to count
            
        Returns:
            Total count
        """
        if not self._current_chest:
            return 0
        return self._current_chest.count_item(item_id)
    
    def has_in_chest(self, item_id: str, count: int = 1) -> bool:
        """
        Check if chest has enough of an item.
        
        Args:
            item_id: Item ID to check
            count: Required count
            
        Returns:
            True if has enough
        """
        return self.count_in_chest(item_id) >= count
    
    def get_chest_contents(self) -> List[ItemStack]:
        """
        Get all items in the chest.
        
        Returns:
            List of item stacks
        """
        if not self._current_chest:
            return []
        
        contents = []
        for slot_index in range(self._current_chest.get_size()):
            item = self._current_chest.get_item(slot_index)
            if item:
                contents.append(item)
        
        return contents
    
    def sort_chest(self) -> None:
        """Sort items in the chest by item ID."""
        if not self._current_chest:
            return
        
        # Collect all items
        items = []
        for slot_index in range(self._current_chest.get_size()):
            item = self._current_chest.get_item(slot_index)
            if item:
                items.append(item)
                self._current_chest.clear_slot(slot_index)
        
        # Sort by item ID
        items.sort(key=lambda x: x.item_id)
        
        # Place back in sorted order
        for item in items:
            self._current_chest.add_item(item)
        
        self._logger.info("Sorted chest contents")
    
    def __repr__(self) -> str:
        return f"ChestInteraction(open={self._is_open}, position={self._chest_position})"
