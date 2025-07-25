import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from abtree.forest.communication import (
    CommunicationMiddleware, CommunicationType, Message, Request, Response, Task,
    Message, Request, Response, Task
)
from abtree.forest.core import BehaviorForest, ForestNode, ForestNodeType
from abtree.engine.behavior_tree import BehaviorTree
from abtree.core.status import Status


class TestCommunicationMiddleware:
    """Test communication middleware functionality"""
    
    @pytest.fixture
    def forest(self):
        """Create test forest"""
        return BehaviorForest("TestForest")
    
    @pytest.fixture
    def middleware(self):
        """Create communication middleware"""
        return CommunicationMiddleware("TestMiddleware")
    
    @pytest.fixture
    def mock_callback(self):
        """Create mock callback function"""
        return Mock()
    
    def test_middleware_initialization(self, middleware):
        """Test middleware initialization"""
        assert middleware.name == "TestMiddleware"
        assert middleware.enabled is True
        assert middleware.forest is None
        assert middleware.shared_event_system is not None
    
    def test_middleware_initialize_with_forest(self, middleware, forest):
        """Test middleware initialization with forest"""
        middleware.initialize(forest)
        assert middleware.forest == forest
        assert middleware.shared_event_system is not None
    
    def test_pubsub_subscribe_unsubscribe(self, middleware, mock_callback):
        """Test publish-subscribe pattern"""
        # Test subscription
        middleware.subscribe("test_topic", mock_callback)
        subscribers = middleware.get_subscribers("test_topic")
        assert mock_callback in subscribers
        
        # Test unsubscription
        result = middleware.unsubscribe("test_topic", mock_callback)
        assert result is True
        subscribers = middleware.get_subscribers("test_topic")
        assert mock_callback not in subscribers
    
    @pytest.mark.asyncio
    async def test_pubsub_publish(self, middleware, mock_callback):
        """Test publish functionality"""
        middleware.subscribe("test_topic", mock_callback)
        
        # Publish message
        await middleware.publish("test_topic", {"data": "test"}, "source")
        
        # Verify callback was called
        mock_callback.assert_called_once()
        call_args = mock_callback.call_args[0][0]
        assert call_args["topic"] == "test_topic"
        assert call_args["data"] == {"data": "test"}
    
    def test_reqresp_register_unregister_service(self, middleware):
        """Test request-response service registration"""
        def test_handler(params):
            return {"result": "success"}
        
        # Register service
        middleware.register_service("test_service", test_handler)
        services = middleware.get_available_services()
        assert "test_service" in services
        
        # Unregister service
        result = middleware.unregister_service("test_service")
        assert result is True
        services = middleware.get_available_services()
        assert "test_service" not in services
    
    @pytest.mark.asyncio
    async def test_reqresp_request_response(self, middleware):
        """Test request-response functionality"""
        def test_handler(params, source):
            return {"result": params.get("input", "default")}
        
        middleware.register_service("test_service", test_handler)
        
        # Send request
        response = await middleware.request("test_service", {"input": "test_data"}, "source")
        assert response["result"] == "test_data"
    
    def test_shared_blackboard_set_get(self, middleware):
        """Test shared blackboard functionality"""
        # Set data
        middleware.set("test_key", "test_value", "source")
        
        # Get data
        value = middleware.get("test_key")
        assert value == "test_value"
        
        # Check data exists
        assert middleware.has("test_key") is True
    
    def test_shared_blackboard_remove(self, middleware):
        """Test shared blackboard remove functionality"""
        middleware.set("test_key", "test_value", "source")
        assert middleware.has("test_key") is True
        
        # Remove data
        result = middleware.remove("test_key", "source")
        assert result is True
        assert middleware.has("test_key") is False
    
    def test_shared_blackboard_access_log(self, middleware):
        """Test shared blackboard access log"""
        middleware.set("test_key", "test_value", "source")
        middleware.get("test_key")
        
        log = middleware.get_access_log()
        assert len(log) >= 2  # At least one set and one get operation
    
    def test_state_watching(self, middleware, mock_callback):
        """Test state monitoring functionality"""
        # Monitor state changes
        middleware.watch_state("test_key", mock_callback, "source")
        
        # Update state
        asyncio.run(middleware.update_state("test_key", "new_value", "source"))
        
        # Verify callback was called
        mock_callback.assert_called_once()
    
    def test_state_watching_unwatch(self, middleware, mock_callback):
        """Test unwatch state monitoring"""
        middleware.watch_state("test_key", mock_callback, "source")
        
        # Unwatch state
        result = middleware.unwatch_state("test_key", mock_callback)
        assert result is True
    
    def test_behavior_call_register_unregister(self, middleware):
        """Test behavior call registration"""
        def test_behavior(params):
            return Status.SUCCESS
        
        # Register behavior
        middleware.register_behavior("test_behavior", test_behavior)
        behaviors = middleware.get_registered_behaviors()
        assert "test_behavior" in behaviors
        
        # Unregister behavior
        result = middleware.unregister_behavior("test_behavior")
        assert result is True
        behaviors = middleware.get_registered_behaviors()
        assert "test_behavior" not in behaviors
    
    @pytest.mark.asyncio
    async def test_behavior_call_execution(self, middleware):
        """Test behavior call execution"""
        def test_behavior(params):
            return Status.SUCCESS
        
        middleware.register_behavior("test_behavior", test_behavior)
        
        # Call behavior
        result = await middleware.call_behavior("test_behavior", {"param": "value"}, "source")
        assert result == Status.SUCCESS
    
    def test_task_board_publish_task(self, middleware):
        """Test task board publish task"""
        task_id = middleware.publish_task(
            "Test Task",
            "Test Description",
            {"capability1", "capability2"},
            priority=5
        )
        assert task_id is not None
        
        # Get available tasks
        available_tasks = middleware.get_available_tasks({"capability1", "capability2"})
        assert len(available_tasks) >= 1
    
    def test_task_board_claim_task(self, middleware):
        """Test task board claim task"""
        task_id = middleware.publish_task(
            "Test Task",
            "Test Description",
            {"capability1"},
            priority=5
        )
        
        # Claim task
        success = middleware.claim_task(task_id, "worker1", {"capability1"})
        assert success is True
        
        # Check claimed tasks
        claimed_tasks = middleware.get_claimed_tasks("worker1")
        assert len(claimed_tasks) >= 1
    
    def test_task_board_complete_task(self, middleware):
        """Test task board complete task"""
        task_id = middleware.publish_task(
            "Test Task",
            "Test Description",
            {"capability1"},
            priority=5
        )
        
        middleware.claim_task(task_id, "worker1", {"capability1"})
        success = middleware.complete_task(task_id, {"result": "success"})
        assert success is True
    
    def test_task_board_fail_task(self, middleware):
        """Test task board fail task"""
        task_id = middleware.publish_task(
            "Test Task",
            "Test Description",
            {"capability1"},
            priority=5
        )
        
        middleware.claim_task(task_id, "worker1", {"capability1"})
        success = middleware.fail_task(task_id, "Task failed")
        assert success is True
    
    def test_task_board_stats(self, middleware):
        """Test task board statistics"""
        # Publish several tasks
        middleware.publish_task("Task 1", "Description 1", {"cap1"}, priority=1)
        middleware.publish_task("Task 2", "Description 2", {"cap2"}, priority=2)
        
        stats = middleware.get_task_stats()
        assert "total_tasks" in stats
        assert "pending_tasks" in stats
        assert "claimed_tasks" in stats
        assert "completed_tasks" in stats
        assert "failed_tasks" in stats
    
    def test_shared_event_system_integration(self, middleware, forest):
        """Test shared event system integration"""
        middleware.initialize(forest)
        
        # Add tree to shared event system
        tree = BehaviorTree("TestTree")
        middleware.add_tree_to_shared_event_system("test_tree", tree)
        
        # Check if tree is in shared event system
        trees = middleware.get_trees_with_shared_event_system()
        assert "test_tree" in trees
        
        # Remove tree
        result = middleware.remove_tree_from_shared_event_system("test_tree")
        assert result is True
    
    def test_shared_event_system_stats(self, middleware):
        """Test shared event system statistics"""
        stats = middleware.get_shared_event_system_stats()
        assert "event_system_stats" in stats
        assert "total_events" in stats["event_system_stats"]
        assert "shared_trees" in stats
        assert "tree_names" in stats
    
    @pytest.mark.asyncio
    async def test_pre_post_tick(self, middleware, forest):
        """Test pre and post tick hooks"""
        middleware.initialize(forest)
        
        # Test pre tick
        await middleware.pre_tick()
        
        # Test post tick
        results = {"tree1": Status.SUCCESS, "tree2": Status.FAILURE}
        await middleware.post_tick(results)
    
    def test_message_creation(self):
        """Test message creation"""
        message = Message(
            id="test_id",
            source="test_source",
            target="test_target",
            data={"test": "data"},
            priority=5
        )
        
        assert message.id == "test_id"
        assert message.source == "test_source"
        assert message.target == "test_target"
        assert message.data == {"test": "data"}
        assert message.priority == 5
    
    def test_request_creation(self):
        """Test request creation"""
        request = Request(
            id="test_id",
            source="test_source",
            method="test_method",
            params={"param": "value"}
        )
        
        assert request.method == "test_method"
        assert request.params == {"param": "value"}
    
    def test_response_creation(self):
        """Test response creation"""
        response = Response(
            id="test_id",
            source="test_source",
            request_id="req_id",
            success=True,
            error=None
        )
        
        assert response.request_id == "req_id"
        assert response.success is True
        assert response.error is None
    
    def test_task_creation(self):
        """Test task creation"""
        task = Task(
            id="task_id",
            title="Test Task",
            description="Test Description",
            requirements={"cap1", "cap2"},
            priority=5,
            status="pending"
        )
        
        assert task.id == "task_id"
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.requirements == {"cap1", "cap2"}
        assert task.priority == 5
        assert task.status == "pending"
    
    def test_communication_type_enum(self):
        """Test communication type enumeration"""
        assert CommunicationType.PUB_SUB == CommunicationType.PUB_SUB
        assert CommunicationType.REQ_RESP == CommunicationType.REQ_RESP
        assert CommunicationType.SHARED_BLACKBOARD == CommunicationType.SHARED_BLACKBOARD
        assert CommunicationType.STATE_WATCHING == CommunicationType.STATE_WATCHING
        assert CommunicationType.BEHAVIOR_CALL == CommunicationType.BEHAVIOR_CALL
        assert CommunicationType.TASK_BOARD == CommunicationType.TASK_BOARD 