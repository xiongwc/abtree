#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Behavior Forest Features Example (XML Configuration)

This example demonstrates the advanced features of the behavior forest system:
- How to configure plugin system
- How to configure performance monitoring
- How to configure real-time dashboard
"""

import asyncio
import logging
import time
from typing import Dict, Any

from abtree import (
    BehaviorForest, ForestNode, ForestNodeType,
    BehaviorTree, Sequence, Selector, Action, Condition, Status
)
from abtree.forest.plugin_system import PluginManager, BasePlugin
from abtree.forest.performance import PerformanceMonitor, create_performance_monitor
from abtree.forest.communication import (
    CommunicationMiddleware,
    CommunicationType,
    Message,
    Request,
    Response,
    Task,
)


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomRobotAction(Action):
    """Custom robot action for demonstration."""
    
    def __init__(self, name: str, robot_id: str, action_type: str):
        super().__init__(name)
        self.robot_id = robot_id
        self.action_type = action_type
        
    async def execute(self, blackboard):
        print(f"🤖 Robot {self.robot_id} performing {self.action_type}")
        await asyncio.sleep(0.01)  # Fast simulation
        return Status.SUCCESS


class CustomCondition(Condition):
    """Custom condition for demonstration."""
    
    def __init__(self, name: str, check_key: str, expected_value: Any = True):
        super().__init__(name)
        self.check_key = check_key
        self.expected_value = expected_value
        
    async def evaluate(self, blackboard):
        value = blackboard.get(self.check_key, False)
        return value == self.expected_value


# Custom Plugin Example
class RobotMonitoringPlugin(BasePlugin):
    """Custom plugin for robot monitoring."""
    
    PLUGIN_NAME = "RobotMonitoring"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "Monitors robot health and performance"
    PLUGIN_AUTHOR = "ABTree Team"
    PLUGIN_TAGS = ["robot", "monitoring"]
    
    def __init__(self):
        super().__init__("RobotMonitoring", "1.0.0")
        self.monitoring_data = {}
        
    def initialize(self, forest):
        """Initialize the plugin with the forest."""
        super().initialize(forest)
        logger.info("🤖 Robot monitoring plugin initialized")
        
        # Add monitoring nodes to the forest
        for node_name, node in forest.nodes.items():
            if "robot" in node_name.lower():
                self.monitoring_data[node_name] = {
                    'health': 100,
                    'battery': 100,
                    'last_check': time.time()
                }
    
    def cleanup(self):
        """Clean up plugin resources."""
        super().cleanup()
        logger.info("🤖 Robot monitoring plugin cleaned up")
    
    def get_robot_health(self, robot_name: str) -> Dict[str, Any]:
        """Get robot health information."""
        return self.monitoring_data.get(robot_name, {})


def create_robot_tree(robot_id: str) -> BehaviorTree:
    """Create a behavior tree for a robot."""
    root = Selector(f"Robot_{robot_id}_Decision")
    
    # Emergency response (highest priority)
    emergency = Sequence("Emergency Response")
    emergency.add_child(CustomCondition("Check Emergency", f"emergency_{robot_id}"))
    emergency.add_child(CustomRobotAction("Emergency Response", robot_id, "emergency"))
    
    # Task execution
    task = Sequence("Task Execution")
    task.add_child(CustomCondition("Check Tasks", f"task_available_{robot_id}"))
    task.add_child(CustomRobotAction("Execute Task", robot_id, "task"))
    
    # Patrol (lowest priority)
    patrol = Sequence("Patrol")
    patrol.add_child(CustomRobotAction("Patrol Area", robot_id, "patrol"))
    
    root.add_child(emergency)
    root.add_child(task)
    root.add_child(patrol)
    
    tree = BehaviorTree()
    tree.load_from_node(root)
    return tree


async def demonstrate_plugin_system():
    """Demonstrate the plugin system."""
    print("\n" + "="*60)
    print("🔌 PLUGIN SYSTEM DEMONSTRATION")
    print("="*60)
    
    # Create plugin manager
    plugin_manager = PluginManager()
    
    # Create forest
    forest = BehaviorForest("PluginDemo")
    
    # Add some nodes
    for robot_id in ["R1", "R2"]:
        tree = create_robot_tree(robot_id)
        node = ForestNode(
            name=f"Robot_{robot_id}",
            tree=tree,
            node_type=ForestNodeType.WORKER
        )
        forest.add_node(node)
    
    # Create and load custom plugin
    robot_plugin = RobotMonitoringPlugin()
    plugin_manager.plugins["RobotMonitoring"] = robot_plugin
    
    # Initialize plugin with forest
    plugin_manager.initialize_plugin(robot_plugin, forest)
    
    # Demonstrate plugin functionality
    health_data = robot_plugin.get_robot_health("Robot_R1")
    print(f"🤖 Robot R1 Health: {health_data}")
    
    # List plugins
    plugins = plugin_manager.list_plugins()
    print(f"📋 Available Plugins: {len(plugins)}")
    for plugin in plugins:
        print(f"   - {plugin.name} v{plugin.version}: {plugin.description}")
    
    # Cleanup
    plugin_manager.cleanup_plugin("RobotMonitoring")
    print("✅ Plugin system demonstration completed")


async def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring."""
    print("\n" + "="*60)
    print("📊 PERFORMANCE MONITORING DEMONSTRATION")
    print("="*60)
    
    # Create forest
    forest = BehaviorForest("PerformanceDemo")
    
    # Add middleware
    forest.add_middleware(CommunicationMiddleware("Communication"))
    
    # Add robot nodes
    for robot_id in ["R1", "R2", "R3"]:
        tree = create_robot_tree(robot_id)
        node = ForestNode(
            name=f"Robot_{robot_id}",
            tree=tree,
            node_type=ForestNodeType.WORKER
        )
        forest.add_node(node)
    
    # Create performance monitor
    monitor = create_performance_monitor(forest)
    
    # Start monitoring
    await monitor.start_monitoring(interval=0.5)
    
    # Start forest
    await forest.start()
    
    # Run forest for a few ticks
    for i in range(5):
        start_time = time.time()
        results = await forest.tick()
        execution_time = time.time() - start_time
        
        # Record performance
        monitor.record_forest_execution(execution_time, True)
        
        print(f"Tick {i+1}: {len(results)} nodes executed in {execution_time:.3f}s")
        await asyncio.sleep(0.01)
    
    # Stop monitoring and forest
    await monitor.stop_monitoring()
    await forest.stop()
    
    # Get performance report
    report = monitor.get_forest_performance_report()
    print(f"\n📈 Performance Report:")
    print(f"   Total Executions: {report['forest_metrics']['total_executions']}")
    print(f"   Success Rate: {report['forest_metrics']['success_rate']:.1f}%")
    print(f"   Average Execution Time: {report['forest_metrics']['average_execution_time']:.3f}s")
    print(f"   Throughput: {report['forest_metrics']['throughput']:.2f} exec/s")
    
    # Get performance summary
    summary = monitor.get_performance_summary()
    print(f"\n📋 Performance Summary:")
    print(summary)
    
    print("✅ Performance monitoring demonstration completed")


async def demonstrate_real_time_dashboard():
    """Demonstrate real-time dashboard."""
    print("\n" + "="*60)
    print("🖥️ REAL-TIME DASHBOARD DEMONSTRATION")
    print("="*60)
    
    # Create multiple forests
    forests = []
    
    for i in range(2):
        forest = BehaviorForest(f"DashboardDemo_{i+1}")
        
        # Add middleware
        forest.add_middleware(CommunicationMiddleware(f"Communication_{i+1}"))
        
        # Add robot nodes
        for robot_id in [f"R{i+1}_{j+1}" for j in range(2)]:
            tree = create_robot_tree(robot_id)
            node = ForestNode(
                name=f"Robot_{robot_id}",
                tree=tree,
                node_type=ForestNodeType.WORKER
            )
            forest.add_node(node)
        
        forests.append(forest)
    
    # Start forests
    for forest in forests:
        await forest.start()
    
    # Run forests for a few ticks
    for i in range(3):
        for forest in forests:
            await forest.tick()
        await asyncio.sleep(0.01)
    
    # Stop forests
    for forest in forests:
        await forest.stop()
    
    print("✅ Real-time dashboard demonstration completed")


async def main():
    """Main demonstration function."""
    print("🚀 ADVANCED BEHAVIOR FOREST FEATURES DEMONSTRATION (XML)")
    print("="*60)
    
    try:
        # Demonstrate plugin system
        await demonstrate_plugin_system()
        
        # Demonstrate performance monitoring
        await demonstrate_performance_monitoring()
        
        # Demonstrate real-time dashboard
        await demonstrate_real_time_dashboard()
        
        print("\n" + "="*60)
        print("🎉 ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Demonstration error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 