"""
Tests for the navigation system.
"""

import pytest
from mindpy.navigation import Position, MovementController, PathFinder, WaypointManager, Waypoint, WaypointType


class TestPosition:
    """Test cases for Position."""
    
    @pytest.mark.unit
    def test_position_creation(self):
        """Test creating a position."""
        pos = Position(x=10.5, y=64.0, z=-5.3)
        
        assert pos.x == 10.5
        assert pos.y == 64.0
        assert pos.z == -5.3
    
    @pytest.mark.unit
    def test_position_distance_to(self):
        """Test calculating distance between positions."""
        pos1 = Position(x=0, y=0, z=0)
        pos2 = Position(x=3, y=4, z=0)
        
        distance = pos1.distance_to(pos2)
        
        assert distance == 5.0
    
    @pytest.mark.unit
    def test_position_add(self):
        """Test adding positions."""
        pos1 = Position(x=1, y=2, z=3)
        pos2 = Position(x=4, y=5, z=6)
        
        result = pos1 + pos2
        
        assert result.x == 5
        assert result.y == 7
        assert result.z == 9
    
    @pytest.mark.unit
    def test_position_subtract(self):
        """Test subtracting positions."""
        pos1 = Position(x=5, y=7, z=9)
        pos2 = Position(x=1, y=2, z=3)
        
        result = pos1 - pos2
        
        assert result.x == 4
        assert result.y == 5
        assert result.z == 6


class TestMovementController:
    """Test cases for MovementController."""
    
    @pytest.fixture
    def movement_controller(self):
        """Create a fresh movement controller for each test."""
        return MovementController()
    
    @pytest.mark.unit
    def test_movement_controller_creation(self, movement_controller):
        """Test creating a movement controller."""
        assert movement_controller is not None
        assert movement_controller.get_position() == Position(0, 0, 0)
    
    @pytest.mark.unit
    async def test_move_to(self, movement_controller):
        """Test moving to a position."""
        target = Position(x=10, y=64, z=10)
        success = await movement_controller.move_to(target)
        
        assert success is True
        assert movement_controller.get_position() == target
    
    @pytest.mark.unit
    def test_get_position(self, movement_controller):
        """Test getting current position."""
        pos = movement_controller.get_position()
        
        assert pos is not None
        assert isinstance(pos, Position)
    
    @pytest.mark.unit
    def test_set_position(self, movement_controller):
        """Test setting position."""
        new_pos = Position(x=5, y=70, z=5)
        movement_controller.set_position(new_pos)
        
        assert movement_controller.get_position() == new_pos
    
    @pytest.mark.unit
    def test_is_moving(self, movement_controller):
        """Test checking if moving."""
        assert not movement_controller.is_moving()


class TestPathFinder:
    """Test cases for PathFinder."""
    
    @pytest.fixture
    def path_finder(self):
        """Create a fresh path finder for each test."""
        return PathFinder()
    
    @pytest.mark.unit
    def test_path_finder_creation(self, path_finder):
        """Test creating a path finder."""
        assert path_finder is not None
    
    @pytest.mark.unit
    async def test_find_path(self, path_finder):
        """Test finding a path."""
        start = Position(x=0, y=64, z=0)
        goal = Position(x=10, y=64, z=10)
        
        path = await path_finder.find_path(start, goal)
        
        # Should return a list (may be empty if no path found)
        assert isinstance(path, list)
    
    @pytest.mark.unit
    def test_smooth_path(self, path_finder):
        """Test smoothing a path."""
        path = [
            Position(0, 64, 0),
            Position(1, 64, 0),
            Position(2, 64, 0),
            Position(3, 64, 0),
            Position(10, 64, 10)
        ]
        
        smoothed = path_finder.smooth_path(path)
        
        assert isinstance(smoothed, list)
        assert len(smoothed) <= len(path)


class TestWaypointManager:
    """Test cases for WaypointManager."""
    
    @pytest.fixture
    def waypoint_manager(self):
        """Create a fresh waypoint manager for each test."""
        return WaypointManager()
    
    @pytest.mark.unit
    def test_waypoint_manager_creation(self, waypoint_manager):
        """Test creating a waypoint manager."""
        assert waypoint_manager is not None
    
    @pytest.mark.unit
    def test_add_waypoint(self, waypoint_manager):
        """Test adding a waypoint."""
        waypoint = waypoint_manager.add_waypoint(
            name="home",
            position=Position(x=0, y=64, z=0),
            waypoint_type=WaypointType.HOME
        )
        
        assert waypoint.name == "home"
        assert waypoint_manager.get_waypoint_count() == 1
    
    @pytest.mark.unit
    def test_get_waypoint(self, waypoint_manager):
        """Test getting a waypoint."""
        waypoint_manager.add_waypoint(
            name="test",
            position=Position(x=0, y=64, z=0)
        )
        
        waypoint = waypoint_manager.get_waypoint("test")
        
        assert waypoint is not None
        assert waypoint.name == "test"
    
    @pytest.mark.unit
    def test_remove_waypoint(self, waypoint_manager):
        """Test removing a waypoint."""
        waypoint_manager.add_waypoint(
            name="test",
            position=Position(x=0, y=64, z=0)
        )
        
        success = waypoint_manager.remove_waypoint("test")
        
        assert success is True
        assert waypoint_manager.get_waypoint("test") is None
    
    @pytest.mark.unit
    def test_find_nearest_waypoint(self, waypoint_manager):
        """Test finding nearest waypoint."""
        waypoint_manager.add_waypoint(
            name="near",
            position=Position(x=5, y=64, z=5)
        )
        waypoint_manager.add_waypoint(
            name="far",
            position=Position(x=100, y=64, z=100)
        )
        
        nearest = waypoint_manager.find_nearest_waypoint(Position(x=0, y=64, z=0))
        
        assert nearest is not None
        assert nearest.name == "near"
    
    @pytest.mark.unit
    def test_search_waypoints(self, waypoint_manager):
        """Test searching waypoints."""
        waypoint_manager.add_waypoint(
            name="home_base",
            position=Position(x=0, y=64, z=0)
        )
        waypoint_manager.add_waypoint(
            name="mine",
            position=Position(x=10, y=64, z=10)
        )
        
        results = waypoint_manager.search_waypoints("home")
        
        assert len(results) == 1
        assert results[0].name == "home_base"
