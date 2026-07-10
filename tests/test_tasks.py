"""
Tests for the task system.
"""

import pytest
import asyncio
from mindpy.tasks import Task, TaskStatus, TaskPriority, TaskManager


class TestTask:
    """Test cases for Task class."""
    
    @pytest.mark.unit
    def test_task_creation(self):
        """Test creating a task."""
        task = Task(
            task_type="test_task",
            description="A test task",
            priority=TaskPriority.NORMAL
        )
        
        assert task.task_type == "test_task"
        assert task.description == "A test task"
        assert task.priority == TaskPriority.NORMAL
        assert task.status == TaskStatus.PENDING
    
    @pytest.mark.unit
    def test_task_mark_started(self):
        """Test marking a task as started."""
        task = Task(task_type="test", description="Test")
        task.mark_started()
        
        assert task.status == TaskStatus.RUNNING
        assert task.started_at is not None
    
    @pytest.mark.unit
    def test_task_mark_completed(self):
        """Test marking a task as completed."""
        task = Task(task_type="test", description="Test")
        task.mark_started()
        task.mark_completed(result="test_result")
        
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
        assert task.result == "test_result"
    
    @pytest.mark.unit
    def test_task_mark_failed(self):
        """Test marking a task as failed."""
        task = Task(task_type="test", description="Test")
        task.mark_failed("Test error")
        
        assert task.status == TaskStatus.FAILED
        assert task.error == "Test error"
    
    @pytest.mark.unit
    def test_task_update_progress(self):
        """Test updating task progress."""
        task = Task(task_type="test", description="Test")
        task.update_progress(0.5)
        
        assert task.progress == 0.5
    
    @pytest.mark.unit
    def test_task_to_dict(self):
        """Test serializing task to dictionary."""
        task = Task(task_type="test", description="Test")
        task_dict = task.to_dict()
        
        assert task_dict["task_type"] == "test"
        assert task_dict["status"] == "pending"


class TestTaskManager:
    """Test cases for TaskManager."""
    
    @pytest.fixture
    def task_manager(self):
        """Create a fresh task manager for each test."""
        from mindpy.events import EventBus
        manager = TaskManager(EventBus())
        asyncio.run(manager.start(num_workers=2))
        yield manager
        asyncio.run(manager.stop())
    
    @pytest.mark.unit
    async def test_task_manager_creation(self, task_manager):
        """Test creating a task manager."""
        assert task_manager is not None
        assert task_manager._running is True
    
    @pytest.mark.unit
    async def test_submit_task(self, task_manager):
        """Test submitting a task."""
        from mindpy.tasks import BaseTask
        
        class SimpleTask(BaseTask):
            @property
            def name(self):
                return "simple"
            
            @property
            def description(self):
                return "Simple task"
            
            async def execute(self, context):
                return "completed"
        
        task = SimpleTask(task_type="simple", description="Test")
        task_id = await task_manager.submit_task(task)
        
        assert task_id is not None
        assert task_id in task_manager._tasks
    
    @pytest.mark.unit
    async def test_get_task(self, task_manager):
        """Test getting a task by ID."""
        from mindpy.tasks import BaseTask
        
        class SimpleTask(BaseTask):
            @property
            def name(self):
                return "simple"
            
            @property
            def description(self):
                return "Simple task"
            
            async def execute(self, context):
                return "completed"
        
        task = SimpleTask(task_type="simple", description="Test")
        task_id = await task_manager.submit_task(task)
        retrieved = task_manager.get_task(task_id)
        
        assert retrieved is not None
        assert retrieved.task_id == task_id
    
    @pytest.mark.unit
    async def test_cancel_task(self, task_manager):
        """Test cancelling a task."""
        from mindpy.tasks import BaseTask
        
        class SimpleTask(BaseTask):
            @property
            def name(self):
                return "simple"
            
            @property
            def description(self):
                return "Simple task"
            
            async def execute(self, context):
                await asyncio.sleep(1)
                return "completed"
        
        task = SimpleTask(task_type="simple", description="Test")
        task_id = await task_manager.submit_task(task)
        
        success = await task_manager.cancel_task(task_id)
        
        assert success is True
    
    @pytest.mark.unit
    def test_get_statistics(self, task_manager):
        """Test getting task statistics."""
        stats = task_manager.get_statistics()
        
        assert "total" in stats
        assert "pending" in stats
        assert "running" in stats
