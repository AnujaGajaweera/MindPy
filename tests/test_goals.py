"""
Tests for the goal system.
"""

import pytest
from mindpy.goals import Goal, GoalStatus, GoalPriority, GoalManager, GoalDecomposer


class TestGoal:
    """Test cases for Goal class."""
    
    @pytest.mark.unit
    def test_goal_creation(self):
        """Test creating a goal."""
        goal = Goal(
            name="Test Goal",
            description="A test goal",
            priority=GoalPriority.NORMAL
        )
        
        assert goal.name == "Test Goal"
        assert goal.description == "A test goal"
        assert goal.priority == GoalPriority.NORMAL
        assert goal.status == GoalStatus.PENDING
    
    @pytest.mark.unit
    def test_goal_mark_started(self):
        """Test marking a goal as started."""
        goal = Goal(name="Test", description="Test")
        goal.mark_started()
        
        assert goal.status == GoalStatus.IN_PROGRESS
        assert goal.started_at is not None
    
    @pytest.mark.unit
    def test_goal_mark_completed(self):
        """Test marking a goal as completed."""
        goal = Goal(name="Test", description="Test")
        goal.mark_started()
        goal.mark_completed()
        
        assert goal.status == GoalStatus.COMPLETED
        assert goal.completed_at is not None
        assert goal.progress == 1.0
    
    @pytest.mark.unit
    def test_goal_add_sub_goal(self):
        """Test adding a sub-goal."""
        parent = Goal(name="Parent", description="Parent goal")
        child = Goal(name="Child", description="Child goal")
        
        parent.add_sub_goal(child.goal_id)
        
        assert child.goal_id in parent.sub_goal_ids
    
    @pytest.mark.unit
    def test_goal_is_root(self):
        """Test checking if a goal is a root goal."""
        goal = Goal(name="Test", description="Test")
        assert goal.is_root()
    
    @pytest.mark.unit
    def test_goal_is_leaf(self):
        """Test checking if a goal is a leaf goal."""
        goal = Goal(name="Test", description="Test")
        assert goal.is_leaf()


class TestGoalManager:
    """Test cases for GoalManager."""
    
    @pytest.fixture
    def goal_manager(self):
        """Create a fresh goal manager for each test."""
        from mindpy.events import EventBus
        return GoalManager(EventBus())
    
    @pytest.mark.unit
    def test_goal_manager_creation(self, goal_manager):
        """Test creating a goal manager."""
        assert goal_manager is not None
    
    @pytest.mark.unit
    def test_create_goal(self, goal_manager):
        """Test creating a goal."""
        goal = goal_manager.create_goal(
            name="Test Goal",
            description="A test goal"
        )
        
        assert goal.name == "Test Goal"
        assert goal.goal_id in goal_manager._goals
    
    @pytest.mark.unit
    def test_get_goal(self, goal_manager):
        """Test getting a goal by ID."""
        goal = goal_manager.create_goal("Test", "Test")
        retrieved = goal_manager.get_goal(goal.goal_id)
        
        assert retrieved is not None
        assert retrieved.goal_id == goal.goal_id
    
    @pytest.mark.unit
    def test_update_goal_status(self, goal_manager):
        """Test updating goal status."""
        goal = goal_manager.create_goal("Test", "Test")
        success = goal_manager.update_goal_status(goal.goal_id, GoalStatus.COMPLETED)
        
        assert success is True
        assert goal.status == GoalStatus.COMPLETED
    
    @pytest.mark.unit
    def test_get_goals_by_status(self, goal_manager):
        """Test getting goals by status."""
        goal1 = goal_manager.create_goal("Test1", "Test1")
        goal2 = goal_manager.create_goal("Test2", "Test2")
        
        goal_manager.update_goal_status(goal1.goal_id, GoalStatus.COMPLETED)
        
        completed = goal_manager.get_goals_by_status(GoalStatus.COMPLETED)
        
        assert len(completed) == 1
        assert completed[0].goal_id == goal1.goal_id


class TestGoalDecomposer:
    """Test cases for GoalDecomposer."""
    
    @pytest.fixture
    def decomposer(self):
        """Create a fresh goal decomposer for each test."""
        return GoalDecomposer()
    
    @pytest.mark.unit
    def test_decomposer_creation(self, decomposer):
        """Test creating a goal decomposer."""
        assert decomposer is not None
    
    @pytest.mark.unit
    async def test_decompose_goal(self, decomposer):
        """Test decomposing a goal."""
        goal = Goal(name="Test", description="Test")
        sub_goals = await decomposer.decompose(goal)
        
        # Should return list (may be empty if no strategy matches)
        assert isinstance(sub_goals, list)
