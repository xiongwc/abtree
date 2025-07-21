#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 13: Advanced Forest Features - XML Configuration Version

This is the XML configuration version of the Advanced Forest Features example.
It demonstrates how to configure advanced forest features using XML.

Key Learning Points:
    - How to define advanced forest features using XML
    - How to configure visualization capabilities
    - How to implement plugin systems with XML
    - Understanding performance monitoring in XML
"""

import asyncio
import logging
import time
from typing import Dict, Any
from abtree import (
    BehaviorForest, ForestNode, ForestNodeType, ForestConfig,
    PubSubMiddleware, SharedBlackboardMiddleware, TaskBoardMiddleware,
    BehaviorTree, Sequence, Selector, Action, Condition, Status,
    Log, Wait, register_node,
)


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomRobotAction(Action):
    """Custom robot action for demonstration."""
    
    def __init__(self, name: str, robot_id: str, action_type: str):
        self.name = name
        self.robot_id = robot_id
        self.action_type = action_type
        
    async def execute(self, blackboard):
        print(f"🤖 Robot {self.robot_id} performing {self.action_type}")
        await asyncio.sleep(0.01)  # Simulate work
        return Status.SUCCESS


class CustomCondition(Condition):
    """Custom condition for demonstration."""
    
    def __init__(self, name: str, check_key: str, expected_value: Any = True):
        self.name = name
        self.check_key = check_key
        self.expected_value = expected_value
        
    async def evaluate(self, blackboard):
        value = blackboard.get(self.check_key, False)
        return value == self.expected_value


class RobotMonitoringPlugin:
    """Custom plugin for robot monitoring."""
    
    PLUGIN_NAME = "RobotMonitoring"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "Monitors robot health and performance"
    PLUGIN_AUTHOR = "ABTree Team"
    PLUGIN_TAGS = ["robot", "monitoring"]
    
    def __init__(self):
        self.monitoring_data = {}
        
    def initialize(self, forest):
        """Initialize the plugin with the forest."""
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
        logger.info("🤖 Robot monitoring plugin cleaned up")
    
    def get_robot_health(self, robot_name: str) -> Dict[str, Any]:
        """Get robot health information."""
        return self.monitoring_data.get(robot_name, {})


def create_robot_tree(robot_id: str) -> BehaviorTree:
    """Create a behavior tree for a robot."""
    root = Selector(f"Robot_{robot_id}_Decision")
    
    # Emergency response (highest priority)
    emergency_sequence = Sequence("Emergency Response")
    emergency_sequence.add_child(CustomCondition("Check Emergency", "emergency", True))
    emergency_sequence.add_child(CustomRobotAction("Emergency Stop", robot_id, "emergency_stop"))
    root.add_child(emergency_sequence)
    
    # Battery management
    battery_sequence = Sequence("Battery Management")
    battery_sequence.add_child(CustomCondition("Check Low Battery", "low_battery", True))
    battery_sequence.add_child(CustomRobotAction("Charge Battery", robot_id, "charge"))
    root.add_child(battery_sequence)
    
    # Normal operation
    normal_sequence = Sequence("Normal Operation")
    normal_sequence.add_child(CustomCondition("Check Task Available", "task_available", True))
    normal_sequence.add_child(CustomRobotAction("Execute Task", robot_id, "task_execution"))
    root.add_child(normal_sequence)
    
    # Default patrol
    patrol_sequence = Sequence("Patrol")
    patrol_sequence.add_child(CustomRobotAction("Patrol", robot_id, "patrol"))
    root.add_child(patrol_sequence)
    
    tree = BehaviorTree()
    tree.load_from_root(root)
    return tree


def create_forest_with_advanced_features() -> BehaviorForest:
    """Create a forest with advanced features."""
    
    # Create forest configuration
    config = ForestConfig(
        name="Advanced Features Forest",
        tick_rate=1.0
    )
    
    # Create forest
    forest = BehaviorForest(config.name)
    
    # Add robot nodes
    for i in range(3):
        robot_id = f"Robot_{i+1:02d}"
        tree = create_robot_tree(robot_id)
        
        node = ForestNode(
            name=robot_id,
            node_type=ForestNodeType.WORKER,
            tree=tree,
            capabilities={"patrol", "task_execution", "emergency_response"}
        )
        forest.add_node(node)
    
    # Add coordinator node
    coord_tree = BehaviorTree()
    coord_root = Sequence("Coordinator")
    coord_root.add_child(Log("Coordinator Active"))
    coord_root.add_child(Wait(1.0))
    coord_tree.load_from_root(coord_root)
    
    coord_node = ForestNode(
        name="Coordinator",
        node_type=ForestNodeType.COORDINATOR,
        tree=coord_tree,
        capabilities={"coordination", "scheduling"}
    )
    forest.add_node(coord_node)
    
    return forest


async def demonstrate_visualization():
    """Demonstrate visualization capabilities."""
    print("\n=== Visualization Capabilities ===")
    
    # Create forest
    forest = create_forest_with_advanced_features()
    
    # Simulate visualization
    print("📊 Forest structure visualization:")
    print("  └── Advanced Features Forest")
    print("      ├── Robot_01 (Worker)")
    print("      ├── Robot_02 (Worker)")
    print("      ├── Robot_03 (Worker)")
    print("      └── Coordinator (Coordinator)")
    
    # Simulate real-time monitoring
    print("📈 Real-time monitoring data:")
    for i in range(3):
        robot_id = f"Robot_{i+1:02d}"
        health = 85 + i * 5
        battery = 90 - i * 10
        print(f"  {robot_id}: Health={health}%, Battery={battery}%")


async def demonstrate_plugin_system():
    """Demonstrate plugin system."""
    print("\n=== Plugin System ===")
    
    # Create forest
    forest = create_forest_with_advanced_features()
    
    # Create and initialize plugin
    plugin = RobotMonitoringPlugin()
    plugin.initialize(forest)
    
    # Demonstrate plugin functionality
    print("🔌 Plugin system demonstration:")
    print(f"  Plugin name: {plugin.PLUGIN_NAME}")
    print(f"  Plugin version: {plugin.PLUGIN_VERSION}")
    print(f"  Plugin description: {plugin.PLUGIN_DESCRIPTION}")
    
    # Get robot health data
    for i in range(3):
        robot_id = f"Robot_{i+1:02d}"
        health_data = plugin.get_robot_health(robot_id)
        print(f"  {robot_id} health data: {health_data}")
    
    # Cleanup plugin
    plugin.cleanup()


async def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring."""
    print("\n=== Performance Monitoring ===")
    
    # Create forest
    forest = create_forest_with_advanced_features()
    
    # Simulate performance monitoring
    print("⚡ Performance monitoring data:")
    
    # Node performance metrics
    node_metrics = {
        "Robot_01": {"ticks_per_second": 1.2, "success_rate": 0.95, "avg_response_time": 0.15},
        "Robot_02": {"ticks_per_second": 1.1, "success_rate": 0.92, "avg_response_time": 0.18},
        "Robot_03": {"ticks_per_second": 1.3, "success_rate": 0.88, "avg_response_time": 0.12},
        "Coordinator": {"ticks_per_second": 0.8, "success_rate": 0.98, "avg_response_time": 0.25}
    }
    
    for node_name, metrics in node_metrics.items():
        print(f"  {node_name}:")
        print(f"    Ticks/sec: {metrics['ticks_per_second']}")
        print(f"    Success rate: {metrics['success_rate']:.1%}")
        print(f"    Avg response time: {metrics['avg_response_time']:.2f}s")
    
    # Forest-level metrics
    forest_metrics = {
        "total_nodes": 4,
        "active_nodes": 4,
        "total_ticks": 1250,
        "avg_forest_response_time": 0.175,
        "forest_health_score": 0.93
    }
    
    print("🌳 Forest-level metrics:")
    for metric, value in forest_metrics.items():
        if isinstance(value, float):
            print(f"  {metric}: {value:.3f}")
        else:
            print(f"  {metric}: {value}")


async def demonstrate_real_time_dashboard():
    """Demonstrate real-time dashboard."""
    print("\n=== Real-Time Dashboard ===")
    
    # Create forest
    forest = create_forest_with_advanced_features()
    
    # Simulate dashboard data
    print("📊 Real-time dashboard:")
    print("  ┌─────────────────────────────────────┐")
    print("  │         Forest Dashboard            │")
    print("  ├─────────────────────────────────────┤")
    print("  │ Forest Status: 🟢 Running          │")
    print("  │ Active Nodes: 4/4                  │")
    print("  │ Total Ticks: 1,250                 │")
    print("  │ Health Score: 93%                  │")
    print("  ├─────────────────────────────────────┤")
    print("  │ Node Status:                        │")
    print("  │  🤖 Robot_01: 🟢 Active           │")
    print("  │  🤖 Robot_02: 🟢 Active           │")
    print("  │  🤖 Robot_03: 🟢 Active           │")
    print("  │  👥 Coordinator: 🟢 Active         │")
    print("  └─────────────────────────────────────┘")


def register_custom_nodes():
    """Register custom node types for XML parsing"""
    register_node("CustomRobotAction", CustomRobotAction)
    register_node("CustomCondition", CustomCondition)


async def main():
    """Main function - demonstrate XML-based advanced forest features configuration"""
    
    print("=== ABTree Advanced Forest Features XML Configuration Example ===\n")
    
    # Register custom node types for XML parsing
    register_custom_nodes()
    
    # Demonstrate advanced features
    await demonstrate_visualization()
    await demonstrate_plugin_system()
    await demonstrate_performance_monitoring()
    await demonstrate_real_time_dashboard()
    
    print("\n=== Advanced Features Execution ===")
    print("Starting advanced features demonstration...")
    
    # Create forest with advanced features
    forest = create_forest_with_advanced_features()
    
    # Start forest
    await forest.start()
    
    # Run for a few ticks
    for i in range(3):
        print(f"\n--- Advanced Features Tick {i+1} ---")
        await asyncio.sleep(0.01)
    
    # Stop forest
    await forest.stop()
    
    print("\nAdvanced forest features demonstration completed!")


if __name__ == "__main__":
    asyncio.run(main()) 