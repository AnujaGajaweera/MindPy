"""
Task manager for MindPy.

Manages task execution, scheduling, and lifecycle.
"""

import asyncio
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict
from datetime import datetime

from mindpy.tasks.task import Task, TaskStatus, TaskPriority
from mindpy.events import EventBus, Event, EventTypes
from mindpy.logging import get_logger


class TaskManager:
    """
    Manages task execution and lifecycle.
    
    Handles task scheduling, execution, interruption, suspension,
    cancellation, and retry logic.
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Initialize the task manager.
        
        Args:
            event_bus: The event bus for task events
        """
        self._event_bus = event_bus
        self._tasks: Dict[str, Task] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._task_queue: asyncio.Queue = asyncio.Queue()
        self._worker_tasks: List[asyncio.Task] = []
        self._num_workers = 4
        self._running = False
        self._logger = get_logger(__name__)
    
    async def start(self, num_workers: int = 4) -> None:
        """
        Start the task manager with worker tasks.
        
        Args:
            num_workers: Number of worker tasks
        """
        if self._running:
            return
        
        self._num_workers = num_workers
        self._running = True
        
        # Start worker tasks
        for i in range(num_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._worker_tasks.append(worker)
        
        self._logger.info(f"Task manager started with {num_workers} workers")
    
    async def stop(self) -> None:
        """Stop the task manager and all workers."""
        if not self._running:
            return
        
        self._running = False
        
        # Cancel all workers
        for worker in self._worker_tasks:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        self._worker_tasks.clear()
        
        # Cancel all running tasks
        for task_id, running_task in self._running_tasks.items():
            task = self._tasks.get(task_id)
            if task:
                await task.cancel()
            running_task.cancel()
        
        await asyncio.gather(*self._running_tasks.values(), return_exceptions=True)
        self._running_tasks.clear()
        
        self._logger.info("Task manager stopped")
    
    async def _worker(self, worker_name: str) -> None:
        """
        Worker task that processes tasks from the queue.
        
        Args:
            worker_name: Name of the worker
        """
        while self._running:
            try:
                task_id = await asyncio.wait_for(
                    self._task_queue.get(),
                    timeout=1.0
                )
                
                task = self._tasks.get(task_id)
                if not task:
                    continue
                
                await self._execute_task(task)
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Error in worker {worker_name}: {e}")
    
    async def _execute_task(self, task: Task) -> None:
        """
        Execute a task.
        
        Args:
            task: The task to execute
        """
        task.mark_started()
        
        # Publish event
        await self._event_bus.publish(Event(
            event_type=EventTypes.TASK_STARTED,
            data={
                "task_id": task.task_id,
                "task_type": task.task_type,
                "description": task.description
            },
            source="task_manager"
        ))
        
        try:
            context = {"task_id": task.task_id}
            result = await task.execute(context)
            
            task.mark_completed(result)
            
            # Publish event
            await self._event_bus.publish(Event(
                event_type=EventTypes.TASK_FINISHED,
                data={
                    "task_id": task.task_id,
                    "result": result
                },
                source="task_manager"
            ))
            
            self._logger.info(f"Task completed: {task.task_type}")
            
        except Exception as e:
            error_msg = str(e)
            task.mark_failed(error_msg)
            
            # Publish event
            await self._event_bus.publish(Event(
                event_type=EventTypes.TASK_FAILED,
                data={
                    "task_id": task.task_id,
                    "error": error_msg
                },
                source="task_manager"
            ))
            
            self._logger.error(f"Task failed: {task.task_type} - {error_msg}")
            
            # Retry if possible
            if task.can_retry():
                self._logger.info(f"Retrying task {task.task_id} (attempt {task.retry_count})")
                await self.enqueue_task(task.task_id)
    
    async def submit_task(self, task: Task) -> str:
        """
        Submit a new task for execution.
        
        Args:
            task: The task to submit
            
        Returns:
            Task ID
        """
        self._tasks[task.task_id] = task
        await self.enqueue_task(task.task_id)
        return task.task_id
    
    async def enqueue_task(self, task_id: str) -> None:
        """
        Enqueue an existing task for execution.
        
        Args:
            task_id: Task ID to enqueue
        """
        await self._task_queue.put(task_id)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task or None if not found
        """
        return self._tasks.get(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: Task ID to cancel
            
        Returns:
            True if cancelled, False if not found
        """
        task = self._tasks.get(task_id)
        if not task:
            return False
        
        await task.cancel()
        
        # Cancel running task if exists
        if task_id in self._running_tasks:
            self._running_tasks[task_id].cancel()
            del self._running_tasks[task_id]
        
        # Publish event
        await self._event_bus.publish(Event(
            event_type=EventTypes.TASK_CANCELLED,
            data={"task_id": task_id},
            source="task_manager"
        ))
        
        self._logger.info(f"Task cancelled: {task_id}")
        return True
    
    async def suspend_task(self, task_id: str) -> bool:
        """
        Suspend a task.
        
        Args:
            task_id: Task ID to suspend
            
        Returns:
            True if suspended, False if not found
        """
        task = self._tasks.get(task_id)
        if not task:
            return False
        
        checkpoint = await task.suspend()
        
        # Cancel running task if exists
        if task_id in self._running_tasks:
            self._running_tasks[task_id].cancel()
            del self._running_tasks[task_id]
        
        # Publish event
        await self._event_bus.publish(Event(
            event_type=EventTypes.TASK_SUSPENDED,
            data={"task_id": task_id, "checkpoint": checkpoint},
            source="task_manager"
        ))
        
        self._logger.info(f"Task suspended: {task_id}")
        return True
    
    async def resume_task(self, task_id: str) -> bool:
        """
        Resume a suspended task.
        
        Args:
            task_id: Task ID to resume
            
        Returns:
            True if resumed, False if not found
        """
        task = self._tasks.get(task_id)
        if not task or task.status != TaskStatus.SUSPENDED:
            return False
        
        if task.checkpoint:
            await task.resume(task.checkpoint)
        
        await self.enqueue_task(task_id)
        
        # Publish event
        await self._event_bus.publish(Event(
            event_type=EventTypes.TASK_RESUMED,
            data={"task_id": task_id},
            source="task_manager"
        ))
        
        self._logger.info(f"Task resumed: {task_id}")
        return True
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """
        Get all tasks with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of tasks
        """
        return [t for t in self._tasks.values() if t.status == status]
    
    def get_tasks_by_type(self, task_type: str) -> List[Task]:
        """
        Get all tasks of a specific type.
        
        Args:
            task_type: Task type to filter by
            
        Returns:
            List of tasks
        """
        return [t for t in self._tasks.values() if t.task_type == task_type]
    
    def get_tasks_by_priority(self, priority: TaskPriority) -> List[Task]:
        """
        Get all tasks with a specific priority.
        
        Args:
            priority: Priority to filter by
            
        Returns:
            List of tasks
        """
        return [t for t in self._tasks.values() if t.priority == priority]
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks."""
        return self.get_tasks_by_status(TaskStatus.PENDING)
    
    def get_running_tasks(self) -> List[Task]:
        """Get all running tasks."""
        return self.get_tasks_by_status(TaskStatus.RUNNING)
    
    def get_suspended_tasks(self) -> List[Task]:
        """Get all suspended tasks."""
        return self.get_tasks_by_status(TaskStatus.SUSPENDED)
    
    def remove_task(self, task_id: str) -> bool:
        """
        Remove a task from the manager.
        
        Args:
            task_id: Task ID to remove
            
        Returns:
            True if removed, False if not found
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False
    
    def get_task_count(self) -> int:
        """Get the total number of tasks."""
        return len(self._tasks)
    
    def get_queue_size(self) -> int:
        """Get the number of tasks in the queue."""
        return self._task_queue.qsize()
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get task statistics.
        
        Returns:
            Dictionary with task counts by status
        """
        stats = {
            "total": len(self._tasks),
            "pending": 0,
            "running": 0,
            "suspended": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0
        }
        
        for task in self._tasks.values():
            status = task.status.value
            if status in stats:
                stats[status] += 1
        
        stats["queued"] = self.get_queue_size()
        
        return stats
    
    def clear(self) -> None:
        """Clear all tasks."""
        self._tasks.clear()
    
    def __repr__(self) -> str:
        return f"TaskManager(tasks={self.get_task_count()}, queued={self.get_queue_size()})"
