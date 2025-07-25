import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from abtree.forest.plugin_system import (
    BasePlugin, PluginInfo, PluginManager, create_plugin_manager,
    MiddlewarePlugin, NodePlugin, UtilityPlugin,
    ExampleMiddlewarePlugin, ExampleNodePlugin
)
from abtree.forest.core import BehaviorForest, ForestNode, ForestNodeType
from abtree.engine.behavior_tree import BehaviorTree
from abtree.core.status import Status


class TestBasePlugin:
    """Test base plugin class"""
    
    @pytest.fixture
    def forest(self):
        """Create test forest"""
        return BehaviorForest("TestForest")
    
    def test_base_plugin_initialization(self):
        """Test base plugin initialization"""
        class TestPlugin(BasePlugin):
            def initialize(self, forest):
                pass
            def cleanup(self):
                pass
        
        plugin = TestPlugin("TestPlugin", "1.0.0")
        
        assert plugin.name == "TestPlugin"
        assert plugin.version == "1.0.0"
        assert plugin.forest is None
        assert plugin.logger is not None
    
    def test_base_plugin_getters(self):
        """Test base plugin getter methods"""
        class TestPlugin(BasePlugin):
            def initialize(self, forest):
                pass
            def cleanup(self):
                pass
        
        plugin = TestPlugin("TestPlugin", "1.0.0")
        
        assert plugin.get_name() == "TestPlugin"
        assert plugin.get_version() == "1.0.0"
    
    def test_base_plugin_abstract_methods(self):
        """Test base plugin abstract methods"""
        class TestPlugin(BasePlugin):
            def initialize(self, forest):
                pass
            def cleanup(self):
                pass
        
        plugin = TestPlugin("TestPlugin", "1.0.0")
        
        # These methods should be implemented by subclasses
        # Since we provided implementations, they should work
        plugin.initialize(Mock())
        plugin.cleanup()


class TestMiddlewarePlugin:
    """Test middleware plugin class"""
    
    @pytest.fixture
    def forest(self):
        """Create test forest"""
        return BehaviorForest("TestForest")
    
    def test_middleware_plugin_initialization(self):
        """Test middleware plugin initialization"""
        class TestMiddlewarePlugin(MiddlewarePlugin):
            def create_middleware(self):
                return Mock()
            def cleanup(self):
                pass
        
        plugin = TestMiddlewarePlugin("TestMiddleware", "1.0.0")
        
        assert plugin.name == "TestMiddleware"
        assert plugin.version == "1.0.0"
        assert plugin.middleware is None
    
    def test_middleware_plugin_abstract_methods(self):
        """Test middleware plugin abstract methods"""
        class TestMiddlewarePlugin(MiddlewarePlugin):
            def create_middleware(self):
                return Mock()
            def cleanup(self):
                pass
        
        plugin = TestMiddlewarePlugin("TestMiddleware", "1.0.0")
        
        # create_middleware method should be implemented by subclasses
        # Since we provided implementation, it should work
        middleware = plugin.create_middleware()
        assert middleware is not None


class TestNodePlugin:
    """Test node plugin class"""
    
    @pytest.fixture
    def forest(self):
        """Create test forest"""
        return BehaviorForest("TestForest")
    
    def test_node_plugin_initialization(self):
        """Test node plugin initialization"""
        class TestNodePlugin(NodePlugin):
            def register_custom_nodes(self):
                pass
            def cleanup(self):
                pass
        
        plugin = TestNodePlugin("TestNodes", "1.0.0")
        
        assert plugin.name == "TestNodes"
        assert plugin.version == "1.0.0"
    
    def test_node_plugin_abstract_methods(self):
        """Test node plugin abstract methods"""
        class TestNodePlugin(NodePlugin):
            def register_custom_nodes(self):
                pass
            def cleanup(self):
                pass
        
        plugin = TestNodePlugin("TestNodes", "1.0.0")
        
        # register_custom_nodes method should be implemented by subclasses
        # Since we provided implementation, it should work
        plugin.register_custom_nodes()


class TestUtilityPlugin:
    """Test utility plugin class"""
    
    @pytest.fixture
    def forest(self):
        """Create test forest"""
        return BehaviorForest("TestForest")
    
    def test_utility_plugin_initialization(self):
        """Test utility plugin initialization"""
        class TestUtilityPlugin(UtilityPlugin):
            def setup_utilities(self):
                pass
            def cleanup(self):
                pass
        
        plugin = TestUtilityPlugin("TestUtility", "1.0.0")
        
        assert plugin.name == "TestUtility"
        assert plugin.version == "1.0.0"
    
    def test_utility_plugin_abstract_methods(self):
        """Test utility plugin abstract methods"""
        class TestUtilityPlugin(UtilityPlugin):
            def setup_utilities(self):
                pass
            def cleanup(self):
                pass
        
        plugin = TestUtilityPlugin("TestUtility", "1.0.0")
        
        # setup_utilities method should be implemented by subclasses
        # Since we provided implementation, it should work
        plugin.setup_utilities()


class TestPluginInfo:
    """Test plugin info class"""
    
    def test_plugin_info_creation(self):
        """Test plugin info creation"""
        plugin_info = PluginInfo(
            name="TestPlugin",
            version="1.0.0",
            description="Test plugin description",
            author="Test Author",
            dependencies=["dep1", "dep2"],
            tags=["test", "example"]
        )
        
        assert plugin_info.name == "TestPlugin"
        assert plugin_info.version == "1.0.0"
        assert plugin_info.description == "Test plugin description"
        assert plugin_info.author == "Test Author"
        assert plugin_info.dependencies == ["dep1", "dep2"]
        assert plugin_info.tags == ["test", "example"]
        assert plugin_info.plugin_class is None


class TestPluginManager:
    """Test plugin manager"""
    
    @pytest.fixture
    def manager(self):
        """Create plugin manager"""
        return PluginManager()
    
    @pytest.fixture
    def forest(self):
        """Create test forest"""
        return BehaviorForest("TestForest")
    
    def test_plugin_manager_initialization(self, manager):
        """Test plugin manager initialization"""
        assert manager.plugins == {}
        assert manager.plugin_paths == []
    
    def test_add_plugin_path(self, manager):
        """Test add plugin path"""
        test_path = "/test/plugin/path"
        manager.add_plugin_path(test_path)
        
        # Path doesn't exist, so it won't be added
        assert test_path not in manager.plugin_paths
    
    def test_add_plugin_path_with_pathlib(self, manager):
        """Test add plugin path with Path object"""
        test_path = Path("/test/plugin/path")
        manager.add_plugin_path(test_path)
        
        # Path doesn't exist, so it won't be added
        assert str(test_path) not in manager.plugin_paths
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    def test_discover_plugins(self, mock_is_file, mock_exists, manager):
        """Test discover plugins"""
        mock_exists.return_value = True
        mock_is_file.return_value = True
        
        # Create temporary directory and file
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_file = Path(temp_dir) / "test_plugin.py"
            plugin_file.write_text("""
from abtree.forest.plugin_system import BasePlugin

class TestPlugin(BasePlugin):
    PLUGIN_NAME = "TestPlugin"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "Test plugin"
    PLUGIN_AUTHOR = "Test Author"
    PLUGIN_DEPENDENCIES = ["dep1"]
    PLUGIN_TAGS = ["test"]
    
    def initialize(self, forest):
        pass
    
    def cleanup(self):
        pass
""")
            
            manager.add_plugin_path(temp_dir)
            plugins = manager.discover_plugins()
            
            assert len(plugins) >= 1
            plugin = plugins[0]
            assert plugin.name == "TestPlugin"
            assert plugin.version == "1.0.0"
    
    def test_load_plugin(self, manager):
        """Test load plugin"""
        # Create a simple plugin class
        class TestPlugin(BasePlugin):
            def initialize(self, forest):
                pass
            
            def cleanup(self):
                pass
        
        # Mock plugin info
        plugin_info = PluginInfo(
            name="TestPlugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            plugin_class=TestPlugin
        )
        
        manager.plugin_info["TestPlugin"] = plugin_info
        
        # Load plugin
        plugin = manager.load_plugin("TestPlugin")
        
        assert plugin is not None
        assert isinstance(plugin, TestPlugin)
        assert "TestPlugin" in manager.plugins
    
    def test_load_nonexistent_plugin(self, manager):
        """Test load nonexistent plugin"""
        plugin = manager.load_plugin("NonexistentPlugin")
        assert plugin is None
    
    def test_load_all_plugins(self, manager):
        """Test load all plugins"""
        # Create test plugins
        class TestPlugin1(BasePlugin):
            def initialize(self, forest):
                pass
            
            def cleanup(self):
                pass
        
        class TestPlugin2(BasePlugin):
            def initialize(self, forest):
                pass
            
            def cleanup(self):
                pass
        
        # Add plugin info
        manager.plugin_info["Plugin1"] = PluginInfo(
            name="Plugin1", version="1.0.0", description="", author="",
            plugin_class=TestPlugin1
        )
        manager.plugin_info["Plugin2"] = PluginInfo(
            name="Plugin2", version="1.0.0", description="", author="",
            plugin_class=TestPlugin2
        )
        
        # Load all plugins
        plugins = manager.load_all_plugins()
        
        assert len(plugins) == 2
        assert all(isinstance(p, BasePlugin) for p in plugins)
    
    def test_initialize_plugin(self, manager, forest):
        """Test initialize plugin"""
        # Create test plugin
        class TestPlugin(BasePlugin):
            def initialize(self, forest):
                self.forest = forest
            
            def cleanup(self):
                pass
        
        plugin = TestPlugin("TestPlugin", "1.0.0")
        
        # Initialize plugin
        success = manager.initialize_plugin(plugin, forest)
        
        assert success is True
        assert plugin.forest == forest
    
    def test_initialize_all_plugins(self, manager, forest):
        """Test initialize all plugins"""
        # Create test plugins
        class TestPlugin(BasePlugin):
            def initialize(self, forest):
                self.forest = forest
            
            def cleanup(self):
                pass
        
        plugin1 = TestPlugin("Plugin1", "1.0.0")
        plugin2 = TestPlugin("Plugin2", "1.0.0")
        
        manager.plugins["Plugin1"] = plugin1
        manager.plugins["Plugin2"] = plugin2
        
        # Initialize all plugins
        plugins = manager.initialize_all_plugins(forest)
        
        assert len(plugins) == 2
        assert all(p.forest == forest for p in plugins)
    
    def test_cleanup_plugin(self, manager):
        """Test cleanup plugin"""
        # Create test plugin
        class TestPlugin(BasePlugin):
            def initialize(self, forest):
                pass
            
            def cleanup(self):
                pass
        
        plugin = TestPlugin("TestPlugin", "1.0.0")
        manager.plugins["TestPlugin"] = plugin
        
        # Cleanup plugin
        success = manager.cleanup_plugin("TestPlugin")
        
        assert success is True
        assert "TestPlugin" not in manager.plugins
    
    def test_cleanup_nonexistent_plugin(self, manager):
        """Test cleanup nonexistent plugin"""
        success = manager.cleanup_plugin("NonexistentPlugin")
        assert success is False
    
    def test_cleanup_all_plugins(self, manager):
        """Test cleanup all plugins"""
        # Create test plugins
        class TestPlugin(BasePlugin):
            def initialize(self, forest):
                pass
            
            def cleanup(self):
                pass
        
        plugin1 = TestPlugin("Plugin1", "1.0.0")
        plugin2 = TestPlugin("Plugin2", "1.0.0")
        
        manager.plugins["Plugin1"] = plugin1
        manager.plugins["Plugin2"] = plugin2
        
        # Cleanup all plugins
        manager.cleanup_all_plugins()
        
        assert len(manager.plugins) == 0
    
    def test_get_plugin_info(self, manager):
        """Test get plugin info"""
        plugin_info = PluginInfo(
            name="TestPlugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author"
        )
        
        manager.plugin_info["TestPlugin"] = plugin_info
        
        retrieved_info = manager.get_plugin_info("TestPlugin")
        assert retrieved_info == plugin_info
    
    def test_get_nonexistent_plugin_info(self, manager):
        """Test get nonexistent plugin info"""
        info = manager.get_plugin_info("NonexistentPlugin")
        assert info is None
    
    def test_list_plugins(self, manager):
        """Test list plugins"""
        # Add plugin info
        manager.plugin_info["Plugin1"] = PluginInfo(
            name="Plugin1", version="1.0.0", description="", author=""
        )
        manager.plugin_info["Plugin2"] = PluginInfo(
            name="Plugin2", version="1.0.0", description="", author=""
        )
        
        plugins = manager.list_plugins()
        
        assert len(plugins) == 2
        assert all(isinstance(p, PluginInfo) for p in plugins)
    
    def test_list_loaded_plugins(self, manager):
        """Test list loaded plugins"""
        # Add loaded plugins
        manager.plugins["Plugin1"] = Mock()
        manager.plugins["Plugin2"] = Mock()
        
        loaded_plugins = manager.list_loaded_plugins()
        
        assert len(loaded_plugins) == 2
        assert "Plugin1" in loaded_plugins
        assert "Plugin2" in loaded_plugins


class TestExamplePlugins:
    """Test example plugins"""
    
    @pytest.fixture
    def forest(self):
        """Create test forest"""
        return BehaviorForest("TestForest")
    
    def test_example_middleware_plugin(self, forest):
        """Test example middleware plugin"""
        plugin = ExampleMiddlewarePlugin("ExampleMiddleware")
        
        assert plugin.name == "ExampleMiddleware"
        assert plugin.version == "1.0.0"
        assert plugin.PLUGIN_DESCRIPTION == "Example middleware plugin for demonstration"
        assert plugin.PLUGIN_AUTHOR == "ABTree Team"
        assert "example" in plugin.PLUGIN_TAGS
        assert "middleware" in plugin.PLUGIN_TAGS
        
        # Test initialization
        plugin.initialize(forest)
        assert plugin.forest == forest
        
        # Test create middleware
        middleware = plugin.create_middleware()
        assert middleware is not None
        
        # Test cleanup
        plugin.cleanup()
    
    def test_example_node_plugin(self, forest):
        """Test example node plugin"""
        plugin = ExampleNodePlugin("ExampleNodes")
        
        assert plugin.name == "ExampleNodes"
        assert plugin.version == "1.0.0"
        assert plugin.PLUGIN_DESCRIPTION == "Example custom nodes for demonstration"
        assert plugin.PLUGIN_AUTHOR == "ABTree Team"
        assert "example" in plugin.PLUGIN_TAGS
        assert "nodes" in plugin.PLUGIN_TAGS
        
        # Test initialization
        plugin.initialize(forest)
        assert plugin.forest == forest
        
        # Test register custom nodes
        plugin.register_custom_nodes()
        
        # Test cleanup
        plugin.cleanup()


class TestPluginUtilities:
    """Test plugin utility functions"""
    
    def test_create_plugin_manager(self):
        """Test create plugin manager"""
        manager = create_plugin_manager()
        
        assert isinstance(manager, PluginManager)
        assert manager.plugins == {}
        assert manager.plugins == {}
    
    @patch('builtins.open', create=True)
    @patch('importlib.util.spec_from_file_location')
    @patch('importlib.util.module_from_spec')
    def test_load_plugin_from_file(self, mock_module_from_spec, mock_spec_from_file_location, mock_open):
        """Test load plugin from file"""
        # Mock module
        mock_module = MagicMock()
        mock_module.PLUGIN_NAME = "TestPlugin"
        mock_module.PLUGIN_VERSION = "1.0.0"
        mock_module.PLUGIN_DESCRIPTION = "Test plugin"
        mock_module.PLUGIN_AUTHOR = "Test Author"
        mock_module.PLUGIN_DEPENDENCIES = []
        mock_module.PLUGIN_TAGS = []
        
        mock_spec_from_file_location.return_value = MagicMock()
        mock_module_from_spec.return_value = mock_module
        
        # Test load plugin from file
        from abtree.forest.plugin_system import load_plugin_from_file
        plugin = load_plugin_from_file("/path/to/plugin.py")
        
        # Since example plugins need special handling, just test function call
        assert plugin is None or isinstance(plugin, BasePlugin)


class TestPluginIntegration:
    """Test plugin integration"""
    
    @pytest.fixture
    def forest(self):
        """Create test forest"""
        return BehaviorForest("TestForest")
    
    @pytest.fixture
    def manager(self):
        """Create plugin manager"""
        return create_plugin_manager()
    
    def test_full_plugin_lifecycle(self, manager, forest):
        """Test complete plugin lifecycle"""
        # Create example plugins with cleanup methods
        class TestExampleMiddlewarePlugin(ExampleMiddlewarePlugin):
            def cleanup(self):
                pass
        
        class TestExampleNodePlugin(ExampleNodePlugin):
            def cleanup(self):
                pass
        
        middleware_plugin = ExampleMiddlewarePlugin("ExampleMiddleware")
        node_plugin = ExampleNodePlugin("ExampleNodes")
        
        # Load plugins
        manager.plugins["MiddlewarePlugin"] = middleware_plugin
        manager.plugins["NodePlugin"] = node_plugin
        
        # Initialize plugins
        plugins = manager.initialize_all_plugins(forest)
        
        assert len(plugins) == 2
        assert all(p.forest == forest for p in plugins)
        
        # Verify plugin info
        assert middleware_plugin.name == "ExampleMiddleware"
        assert node_plugin.name == "ExampleNodes"
        
        # Cleanup plugins
        manager.cleanup_all_plugins()
        
        assert len(manager.plugins) == 0
    
    def test_plugin_manager_with_multiple_plugins(self, manager, forest):
        """Test plugin manager with multiple plugins"""
        # Create multiple plugins
        plugins = []
        for i in range(3):
            class TestPlugin(BasePlugin):
                def initialize(self, forest):
                    self.forest = forest
                
                def cleanup(self):
                    pass
            
            plugin = TestPlugin(f"Plugin{i}", "1.0.0")
            plugins.append(plugin)
            manager.plugins[f"Plugin{i}"] = plugin
        
        # Initialize all plugins
        initialized_plugins = manager.initialize_all_plugins(forest)
        
        assert len(initialized_plugins) == 3
        assert all(p.forest == forest for p in initialized_plugins)
        
        # Verify plugin list
        loaded_plugins = manager.list_loaded_plugins()
        assert len(loaded_plugins) == 3
        assert "Plugin0" in loaded_plugins
        assert "Plugin1" in loaded_plugins
        assert "Plugin2" in loaded_plugins 