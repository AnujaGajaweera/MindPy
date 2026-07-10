"""
Tests for the memory system.
"""

import pytest
from mindpy.memory import (
    WorkingMemory,
    ShortTermMemory,
    LongTermMemory,
    ConversationMemory,
    MemoryManager
)


class TestWorkingMemory:
    """Test cases for WorkingMemory."""
    
    @pytest.fixture
    def working_memory(self):
        """Create a fresh working memory for each test."""
        return WorkingMemory(capacity=10)
    
    @pytest.mark.unit
    def test_working_memory_creation(self, working_memory):
        """Test creating working memory."""
        assert working_memory is not None
        assert working_memory.capacity == 10
    
    @pytest.mark.unit
    def test_add_entry(self, working_memory):
        """Test adding an entry to working memory."""
        working_memory.add("test_key", "test_value")
        assert "test_key" in working_memory._data
    
    @pytest.mark.unit
    def test_get_entry(self, working_memory):
        """Test getting an entry from working memory."""
        working_memory.add("test_key", "test_value")
        value = working_memory.get("test_key")
        assert value == "test_value"
    
    @pytest.mark.unit
    def test_capacity_eviction(self, working_memory):
        """Test that entries are evicted when capacity is exceeded."""
        for i in range(15):
            working_memory.add(f"key_{i}", f"value_{i}")
        
        # Should only have capacity entries
        assert len(working_memory._data) <= working_memory.capacity


class TestShortTermMemory:
    """Test cases for ShortTermMemory."""
    
    @pytest.fixture
    def short_term_memory(self):
        """Create a fresh short term memory for each test."""
        return ShortTermMemory(capacity=20, max_age_seconds=3600)
    
    @pytest.mark.unit
    def test_short_term_memory_creation(self, short_term_memory):
        """Test creating short term memory."""
        assert short_term_memory is not None
        assert short_term_memory.capacity == 20
    
    @pytest.mark.unit
    def test_add_and_retrieve(self, short_term_memory):
        """Test adding and retrieving from short term memory."""
        short_term_memory.add("test", {"data": "value"})
        entry = short_term_memory.get("test")
        assert entry is not None
        assert entry.data == {"data": "value"}


class TestLongTermMemory:
    """Test cases for LongTermMemory."""
    
    @pytest.fixture
    def long_term_memory(self):
        """Create a fresh long term memory for each test."""
        return LongTermMemory(storage_path="/tmp/test_memory.json")
    
    @pytest.mark.unit
    def test_long_term_memory_creation(self, long_term_memory):
        """Test creating long term memory."""
        assert long_term_memory is not None
    
    @pytest.mark.unit
    def test_store_fact(self, long_term_memory):
        """Test storing a fact in long term memory."""
        long_term_memory.store_fact("test_fact", "test_value")
        assert "test_fact" in long_term_memory._facts


class TestConversationMemory:
    """Test cases for ConversationMemory."""
    
    @pytest.fixture
    def conversation_memory(self):
        """Create a fresh conversation memory for each test."""
        return ConversationMemory(max_messages=100)
    
    @pytest.mark.unit
    def test_conversation_memory_creation(self, conversation_memory):
        """Test creating conversation memory."""
        assert conversation_memory is not None
        assert conversation_memory.max_messages == 100
    
    @pytest.mark.unit
    def test_add_message(self, conversation_memory):
        """Test adding a message to conversation memory."""
        conversation_memory.add_message("user", "Hello")
        assert len(conversation_memory._messages) == 1
    
    @pytest.mark.unit
    def test_get_recent_messages(self, conversation_memory):
        """Test getting recent messages."""
        for i in range(10):
            conversation_memory.add_message("user", f"Message {i}")
        
        recent = conversation_memory.get_recent_messages(5)
        assert len(recent) == 5


class TestMemoryManager:
    """Test cases for MemoryManager."""
    
    @pytest.fixture
    def memory_manager(self):
        """Create a fresh memory manager for each test."""
        return MemoryManager()
    
    @pytest.mark.unit
    def test_memory_manager_creation(self, memory_manager):
        """Test creating memory manager."""
        assert memory_manager is not None
        assert memory_manager.working_memory is not None
        assert memory_manager.short_term_memory is not None
        assert memory_manager.long_term_memory is not None
    
    @pytest.mark.unit
    def test_get_memory(self, memory_manager):
        """Test getting a specific memory type."""
        working = memory_manager.get_memory("working")
        assert working is not None
        assert isinstance(working, WorkingMemory)
