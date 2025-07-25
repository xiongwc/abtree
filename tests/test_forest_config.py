import pytest
from abtree.forest.config import (
    ForestConfig, CommunicationConfig, NodeConfig, MiddlewareConfig,
    ForestConfigPresets, CommunicationType
)
from abtree.forest.core import ForestNodeType


class TestCommunicationConfig:
    """Test CommunicationConfig class"""
    
    def test_communication_config_creation(self):
        """Test communication config creation"""
        config = CommunicationConfig(
            pattern=CommunicationType.PUB_SUB,
            enabled=True,
            config={"max_subscribers": 100}
        )
        
        assert config.pattern == CommunicationType.PUB_SUB
        assert config.enabled is True
        assert config.config == {"max_subscribers": 100}
    
    def test_communication_config_defaults(self):
        """Test communication config defaults"""
        config = CommunicationConfig(pattern=CommunicationType.REQ_RESP)
        
        assert config.pattern == CommunicationType.REQ_RESP
        assert config.enabled is True
        assert config.config == {}


class TestNodeConfig:
    """Test NodeConfig class"""
    
    def test_node_config_creation(self):
        """Test node config creation"""
        config = NodeConfig(
            name="TestNode",
            node_type=ForestNodeType.WORKER,
            capabilities={"cap1", "cap2"},
            dependencies={"dep1"},
            metadata={"priority": 5}
        )
        
        assert config.name == "TestNode"
        assert config.node_type == ForestNodeType.WORKER
        assert config.capabilities == {"cap1", "cap2"}
        assert config.dependencies == {"dep1"}
        assert config.metadata == {"priority": 5}
    
    def test_node_config_defaults(self):
        """Test node config defaults"""
        config = NodeConfig(
            name="TestNode",
            node_type=ForestNodeType.WORKER
        )
        
        assert config.name == "TestNode"
        assert config.node_type == ForestNodeType.WORKER
        assert config.capabilities == set()
        assert config.dependencies == set()
        assert config.metadata == {}


class TestForestConfig:
    """Test ForestConfig class"""
    
    def test_forest_config_creation(self):
        """Test forest config creation"""
        config = ForestConfig(
            name="TestForest",
            tick_rate=30.0,
            enabled_middleware=[CommunicationType.PUB_SUB, CommunicationType.REQ_RESP]
        )
        
        assert config.name == "TestForest"
        assert config.tick_rate == 30.0
        assert CommunicationType.PUB_SUB in config.enabled_middleware
        assert CommunicationType.REQ_RESP in config.enabled_middleware
    
    def test_forest_config_defaults(self):
        """Test forest config defaults"""
        config = ForestConfig()
        
        assert config.name == "BehaviorForest"
        assert config.tick_rate == 60.0
        assert len(config.enabled_middleware) == len(CommunicationType)
        assert len(config.communication_configs) == len(CommunicationType)
        assert config.node_configs == []
        assert config.global_settings == {}
    
    def test_forest_config_post_init(self):
        """Test forest config post init"""
        config = ForestConfig()
        
        # Verify all communication types are enabled
        for pattern in CommunicationType:
            assert pattern in config.enabled_middleware
            assert pattern in config.communication_configs
    
    def test_enable_middleware(self):
        """Test enable middleware"""
        config = ForestConfig()
        config.enabled_middleware = []  # Clear default values
        
        config.enable_middleware(CommunicationType.PUB_SUB)
        assert CommunicationType.PUB_SUB in config.enabled_middleware
        
        # Re-enabling should not add duplicates
        config.enable_middleware(CommunicationType.PUB_SUB)
        assert config.enabled_middleware.count(CommunicationType.PUB_SUB) == 1
    
    def test_disable_middleware(self):
        """Test disable middleware"""
        config = ForestConfig()
        
        config.disable_middleware(CommunicationType.PUB_SUB)
        assert CommunicationType.PUB_SUB not in config.enabled_middleware
    
    def test_is_middleware_enabled(self):
        """Test check middleware is enabled"""
        config = ForestConfig()
        config.enabled_middleware = []
        
        assert config.is_middleware_enabled(CommunicationType.PUB_SUB) is False
        
        config.enable_middleware(CommunicationType.PUB_SUB)
        assert config.is_middleware_enabled(CommunicationType.PUB_SUB) is True
    
    def test_configure_communication(self):
        """Test configure communication"""
        config = ForestConfig()
        
        config.configure_communication(CommunicationType.PUB_SUB, {"max_subscribers": 100})
        
        pubsub_config = config.communication_configs[CommunicationType.PUB_SUB]
        assert pubsub_config.config == {"max_subscribers": 100}
    
    def test_add_node_config(self):
        """Test add node config"""
        config = ForestConfig()
        
        node_config = NodeConfig("TestNode", ForestNodeType.WORKER)
        config.add_node_config(node_config)
        
        assert len(config.node_configs) == 1
        assert config.node_configs[0] == node_config
    
    def test_get_node_config(self):
        """Test get node config"""
        config = ForestConfig()
        
        # Add node config
        node_config = NodeConfig("TestNode", ForestNodeType.WORKER)
        config.add_node_config(node_config)
        
        # Get existing node config
        retrieved_config = config.get_node_config("TestNode")
        assert retrieved_config == node_config
        
        # Get nonexistent node config
        nonexistent_config = config.get_node_config("NonexistentNode")
        assert nonexistent_config is None
    
    def test_set_global_setting(self):
        """Test set global setting"""
        config = ForestConfig()
        
        config.set_global_setting("max_trees", 10)
        config.set_global_setting("debug_mode", True)
        
        assert config.global_settings["max_trees"] == 10
        assert config.global_settings["debug_mode"] is True
    
    def test_get_global_setting(self):
        """Test get global setting"""
        config = ForestConfig()
        
        config.set_global_setting("max_trees", 10)
        
        # Get existing setting
        max_trees = config.get_global_setting("max_trees")
        assert max_trees == 10
        
        # Get nonexistent setting
        debug_mode = config.get_global_setting("debug_mode", False)
        assert debug_mode is False
    
    def test_to_dict(self):
        """Test convert to dict"""
        config = ForestConfig(
            name="TestForest",
            tick_rate=30.0
        )
        
        config.enable_middleware(CommunicationType.PUB_SUB)
        config.configure_communication(CommunicationType.PUB_SUB, {"max_subscribers": 100})
        
        node_config = NodeConfig("TestNode", ForestNodeType.WORKER)
        config.add_node_config(node_config)
        
        config.set_global_setting("max_trees", 10)
        
        config_dict = config.to_dict()
        
        assert config_dict["name"] == "TestForest"
        assert config_dict["tick_rate"] == 30.0
        assert "PUB_SUB" in config_dict["enabled_middleware"]
        assert "PUB_SUB" in config_dict["communication_configs"]
        assert len(config_dict["node_configs"]) == 1
        assert config_dict["global_settings"]["max_trees"] == 10
    
    def test_from_dict(self):
        """Test create config from dict"""
        config_data = {
            "name": "TestForest",
            "tick_rate": 30.0,
            "enabled_middleware": ["PUB_SUB", "REQ_RESP"],
            "communication_configs": {
                "PUB_SUB": {
                    "enabled": True,
                    "config": {"max_subscribers": 100}
                }
            },
            "node_configs": [
                {
                    "name": "TestNode",
                    "node_type": "WORKER",
                    "capabilities": ["cap1", "cap2"],
                    "dependencies": ["dep1"],
                    "metadata": {"priority": 5}
                }
            ],
            "global_settings": {
                "max_trees": 10,
                "debug_mode": True
            }
        }
        
        config = ForestConfig.from_dict(config_data)
        
        assert config.name == "TestForest"
        assert config.tick_rate == 30.0
        assert CommunicationType.PUB_SUB in config.enabled_middleware
        assert CommunicationType.REQ_RESP in config.enabled_middleware
        
        pubsub_config = config.communication_configs[CommunicationType.PUB_SUB]
        assert pubsub_config.enabled is True
        assert pubsub_config.config == {"max_subscribers": 100}
        
        assert len(config.node_configs) == 1
        node_config = config.node_configs[0]
        assert node_config.name == "TestNode"
        assert node_config.node_type == ForestNodeType.WORKER
        assert node_config.capabilities == {"cap1", "cap2"}
        assert node_config.dependencies == {"dep1"}
        assert node_config.metadata == {"priority": 5}
        
        assert config.global_settings["max_trees"] == 10
        assert config.global_settings["debug_mode"] is True
    
    def test_validate_valid_config(self):
        """Test validate valid config"""
        config = ForestConfig(
            name="TestForest",
            tick_rate=30.0
        )
        
        node_config1 = NodeConfig("Node1", ForestNodeType.WORKER)
        node_config2 = NodeConfig("Node2", ForestNodeType.WORKER, dependencies={"Node1"})
        
        config.add_node_config(node_config1)
        config.add_node_config(node_config2)
        
        errors = config.validate()
        assert len(errors) == 0
    
    def test_validate_invalid_config(self):
        """Test validate invalid config"""
        config = ForestConfig(
            name="",  # Empty name
            tick_rate=-1.0  # Negative tick rate
        )
        
        node_config = NodeConfig("", ForestNodeType.WORKER)  # Empty node name
        config.add_node_config(node_config)
        
        errors = config.validate()
        
        assert len(errors) > 0
        assert any("name cannot be empty" in error for error in errors)
        assert any("Tick rate must be positive" in error for error in errors)
    
    def test_validate_duplicate_node_names(self):
        """Test validate duplicate node names"""
        config = ForestConfig()
        
        node_config1 = NodeConfig("TestNode", ForestNodeType.WORKER)
        node_config2 = NodeConfig("TestNode", ForestNodeType.WORKER)  # Duplicate name
        
        config.add_node_config(node_config1)
        config.add_node_config(node_config2)
        
        errors = config.validate()
        assert any("Duplicate node name" in error for error in errors)
    
    def test_validate_invalid_dependencies(self):
        """Test validate invalid dependencies"""
        config = ForestConfig()
        
        node_config = NodeConfig("TestNode", ForestNodeType.WORKER, dependencies={"NonexistentNode"})
        config.add_node_config(node_config)
        
        errors = config.validate()
        assert any("depends on unknown node" in error for error in errors)
    
    def test_repr(self):
        """Test string representation"""
        config = ForestConfig("TestForest")
        
        config.add_node_config(NodeConfig("Node1", ForestNodeType.WORKER))
        config.add_node_config(NodeConfig("Node2", ForestNodeType.WORKER))
        
        repr_str = repr(config)
        assert "TestForest" in repr_str
        assert "2" in repr_str  # Node count


class TestForestConfigPresets:
    """Test ForestConfigPresets class"""
    
    def test_basic_preset(self):
        """Test basic preset"""
        config = ForestConfigPresets.basic()
        
        assert config.name == "BasicForest"
        assert config.tick_rate == 60.0
        assert len(config.enabled_middleware) > 0
        assert len(config.node_configs) == 0
    
    def test_pubsub_only_preset(self):
        """Test pubsub only preset"""
        config = ForestConfigPresets.pubsub_only()
        
        assert config.name == "PubSubForest"
        assert CommunicationType.PUB_SUB in config.enabled_middleware
        assert len(config.enabled_middleware) == 1
    
    def test_task_oriented_preset(self):
        """Test task oriented preset"""
        config = ForestConfigPresets.task_oriented()
        
        assert config.name == "TaskOrientedForest"
        assert CommunicationType.TASK_BOARD in config.enabled_middleware
        assert CommunicationType.SHARED_BLACKBOARD in config.enabled_middleware
        assert len(config.node_configs) == 0  # No default nodes in preset
    
    def test_service_oriented_preset(self):
        """Test service oriented preset"""
        config = ForestConfigPresets.service_oriented()
        
        assert config.name == "ServiceOrientedForest"
        assert CommunicationType.REQ_RESP in config.enabled_middleware
        assert CommunicationType.BEHAVIOR_CALL in config.enabled_middleware
    
    def test_monitoring_preset(self):
        """Test monitoring preset"""
        config = ForestConfigPresets.monitoring()
        
        assert config.name == "MonitoringForest"
        assert CommunicationType.STATE_WATCHING in config.enabled_middleware
        assert CommunicationType.PUB_SUB in config.enabled_middleware


class TestMiddlewareConfig:
    """Test MiddlewareConfig class"""
    
    def test_middleware_config_enum(self):
        """Test middleware config enum"""
        assert MiddlewareConfig.ENABLED == MiddlewareConfig.ENABLED
        assert MiddlewareConfig.DISABLED == MiddlewareConfig.DISABLED
        assert MiddlewareConfig.CUSTOM == MiddlewareConfig.CUSTOM


class TestForestConfigIntegration:
    """Test ForestConfigIntegration class"""
    
    def test_complete_config_lifecycle(self):
        """Test complete config lifecycle"""
        # Create config
        config = ForestConfig("TestForest", tick_rate=30.0)
        
        # Configure middleware
        config.enable_middleware(CommunicationType.PUB_SUB)
        config.enable_middleware(CommunicationType.REQ_RESP)
        config.disable_middleware(CommunicationType.TASK_BOARD)
        
        # Configure communication mode
        config.configure_communication(CommunicationType.PUB_SUB, {"max_subscribers": 100})
        config.configure_communication(CommunicationType.REQ_RESP, {"timeout": 5.0})
        
        # Add node config
        node_config1 = NodeConfig("Worker1", ForestNodeType.WORKER, capabilities={"task_processing"})
        node_config2 = NodeConfig("Worker2", ForestNodeType.WORKER, capabilities={"task_processing"})
        
        config.add_node_config(node_config1)
        config.add_node_config(node_config2)
        
        # Set global settings
        config.set_global_setting("max_workers", 5)
        config.set_global_setting("debug_mode", True)
        
        # Verify config
        errors = config.validate()
        assert len(errors) == 0
        
        # Convert to dict
        config_dict = config.to_dict()
        
        # Create from dict
        new_config = ForestConfig.from_dict(config_dict)
        
        # Verify recreated config
        assert new_config.name == config.name
        assert new_config.tick_rate == config.tick_rate
        assert len(new_config.enabled_middleware) == len(config.enabled_middleware)
        assert len(new_config.node_configs) == len(config.node_configs)
        assert new_config.global_settings == config.global_settings
    
    def test_config_with_all_communication_types(self):
        """Test config with all communication types"""
        config = ForestConfig("AllCommunicationForest")
        
        # Enable all communication types
        for comm_type in CommunicationType:
            config.enable_middleware(comm_type)
            config.configure_communication(comm_type, {"enabled": True})
        
        # Verify all communication types are enabled
        for comm_type in CommunicationType:
            assert config.is_middleware_enabled(comm_type)
            assert comm_type in config.communication_configs
        
        # Verify config is valid
        errors = config.validate()
        assert len(errors) == 0
    
    def test_config_with_complex_dependencies(self):
        """Test config with complex dependencies"""
        config = ForestConfig("ComplexDependencyForest")
        
        # Create nodes with dependencies
        node_config1 = NodeConfig("Coordinator", ForestNodeType.COORDINATOR)
        node_config2 = NodeConfig("Worker1", ForestNodeType.WORKER, dependencies={"Coordinator"})
        node_config3 = NodeConfig("Worker2", ForestNodeType.WORKER, dependencies={"Coordinator"})
        node_config4 = NodeConfig("Monitor", ForestNodeType.MONITOR, dependencies={"Worker1", "Worker2"})
        
        config.add_node_config(node_config1)
        config.add_node_config(node_config2)
        config.add_node_config(node_config3)
        config.add_node_config(node_config4)
        
        # Verify config is valid
        errors = config.validate()
        assert len(errors) == 0
        
        # Verify dependencies
        coordinator_config = config.get_node_config("Coordinator")
        worker1_config = config.get_node_config("Worker1")
        monitor_config = config.get_node_config("Monitor")
        
        assert coordinator_config is not None
        assert worker1_config is not None
        assert monitor_config is not None
        assert "Coordinator" in worker1_config.dependencies
        assert "Worker1" in monitor_config.dependencies
        assert "Worker2" in monitor_config.dependencies 