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
import tempfile
import os
from typing import Dict, Any
from abtree import (
    BehaviorForest, ForestNode, ForestNodeType,
    PubSubMiddleware, SharedBlackboardMiddleware, TaskBoardMiddleware,
    BehaviorTree, Sequence, Selector, Action, Condition, Status,
    Log, Wait, register_node,
)
from abtree.parser.xml_parser import XMLParser


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


def create_advanced_forest_xml() -> str:
    """Create XML configuration for advanced forest features"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<BehaviorForest name="AdvancedFeaturesForest" description="Advanced Forest Features">
    
    <!-- Robot 01 Behavior Tree -->
    <BehaviorTree name="Robot_01" description="Robot 01 Service">
        <Selector name="Robot 01 Decision">
            <Sequence name="Emergency Response">
                <CustomCondition name="Check Emergency" check_key="emergency" expected_value="true" />
                <CustomRobotAction name="Emergency Stop" robot_id="01" action_type="emergency_stop" />
            </Sequence>
            <Sequence name="Battery Management">
                <CustomCondition name="Check Low Battery" check_key="low_battery" expected_value="true" />
                <CustomRobotAction name="Charge Battery" robot_id="01" action_type="charge" />
            </Sequence>
            <Sequence name="Normal Operation">
                <CustomCondition name="Check Task Available" check_key="task_available" expected_value="true" />
                <CustomRobotAction name="Execute Task" robot_id="01" action_type="task_execution" />
            </Sequence>
            <CustomRobotAction name="Patrol" robot_id="01" action_type="patrol" />
        </Selector>
    </BehaviorTree>
    
    <!-- Robot 02 Behavior Tree -->
    <BehaviorTree name="Robot_02" description="Robot 02 Service">
        <Selector name="Robot 02 Decision">
            <Sequence name="Emergency Response">
                <CustomCondition name="Check Emergency" check_key="emergency" expected_value="true" />
                <CustomRobotAction name="Emergency Stop" robot_id="02" action_type="emergency_stop" />
            </Sequence>
            <Sequence name="Battery Management">
                <CustomCondition name="Check Low Battery" check_key="low_battery" expected_value="true" />
                <CustomRobotAction name="Charge Battery" robot_id="02" action_type="charge" />
            </Sequence>
            <Sequence name="Normal Operation">
                <CustomCondition name="Check Task Available" check_key="task_available" expected_value="true" />
                <CustomRobotAction name="Execute Task" robot_id="02" action_type="task_execution" />
            </Sequence>
            <CustomRobotAction name="Patrol" robot_id="02" action_type="patrol" />
        </Selector>
    </BehaviorTree>
    
    <!-- Robot 03 Behavior Tree -->
    <BehaviorTree name="Robot_03" description="Robot 03 Service">
        <Selector name="Robot 03 Decision">
            <Sequence name="Emergency Response">
                <CustomCondition name="Check Emergency" check_key="emergency" expected_value="true" />
                <CustomRobotAction name="Emergency Stop" robot_id="03" action_type="emergency_stop" />
            </Sequence>
            <Sequence name="Battery Management">
                <CustomCondition name="Check Low Battery" check_key="low_battery" expected_value="true" />
                <CustomRobotAction name="Charge Battery" robot_id="03" action_type="charge" />
            </Sequence>
            <Sequence name="Normal Operation">
                <CustomCondition name="Check Task Available" check_key="task_available" expected_value="true" />
                <CustomRobotAction name="Execute Task" robot_id="03" action_type="task_execution" />
            </Sequence>
            <CustomRobotAction name="Patrol" robot_id="03" action_type="patrol" />
        </Selector>
    </BehaviorTree>
    
    <!-- Coordinator Behavior Tree -->
    <BehaviorTree name="Coordinator" description="Coordinator Service">
        <Sequence name="Coordinator Behavior">
            <Log name="Coordinator Active" message="Advanced features coordinator is active" />
            <Wait name="Coordinator Wait" duration="1.0" />
        </Sequence>
    </BehaviorTree>
    
    <!-- Communication Configuration -->
    <Communication>
        <!-- Pub/Sub Communication -->
        <ComTopic name="robot_events">
            <ComPublisher service="Robot_01" />
            <ComPublisher service="Robot_02" />
            <ComPublisher service="Robot_03" />
            <ComSubscriber service="Coordinator" />
        </ComTopic>
        <ComTopic name="system_events">
            <ComPublisher service="Coordinator" />
            <ComSubscriber service="Robot_01" />
            <ComSubscriber service="Robot_02" />
            <ComSubscriber service="Robot_03" />
        </ComTopic>
        
        <!-- Shared Blackboard -->
        <ComShared>
            <ComKey name="emergency" />
            <ComKey name="low_battery" />
            <ComKey name="task_available" />
            <ComKey name="system_status" />
            <ComKey name="performance_metrics" />
        </ComShared>
        
        <!-- Task Board -->
        <ComTask name="patrol_task">
            <ComPublisher service="Coordinator" />
            <ComClaimant service="Robot_01" />
            <ComClaimant service="Robot_02" />
            <ComClaimant service="Robot_03" />
        </ComTask>
        <ComTask name="maintenance_task">
            <ComPublisher service="Coordinator" />
            <ComClaimant service="Robot_01" />
            <ComClaimant service="Robot_02" />
            <ComClaimant service="Robot_03" />
        </ComTask>
    </Communication>
    
</BehaviorForest>'''


async def demonstrate_visualization():
    """Demonstrate visualization capabilities."""
    print("\n=== Visualization Capabilities ===")
    
    # Create XML configuration
    xml_config = create_advanced_forest_xml()
    
    # Create temporary XML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(xml_config)
        xml_file_path = f.name
    
    try:
        # Load forest from XML
        parser = XMLParser()
        forest = parser.parse_file(xml_file_path)
        
        # Simulate visualization
        print("📊 Forest structure visualization:")
        print("  └── Advanced Features Forest")
        for node_name, node in forest.nodes.items():
            print(f"      ├── {node_name} ({node.node_type.name})")
        
        # Simulate real-time monitoring
        print("📈 Real-time monitoring data:")
        for i in range(3):
            robot_id = f"Robot_{i+1:02d}"
            health = 85 + i * 5
            battery = 90 - i * 10
            print(f"  {robot_id}: Health={health}%, Battery={battery}%")
            
    finally:
        os.unlink(xml_file_path)


async def demonstrate_plugin_system():
    """Demonstrate plugin system."""
    print("\n=== Plugin System ===")
    
    # Create XML configuration
    xml_config = create_advanced_forest_xml()
    
    # Create temporary XML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(xml_config)
        xml_file_path = f.name
    
    try:
        # Load forest from XML
        parser = XMLParser()
        forest = parser.parse_file(xml_file_path)
        
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
        
    finally:
        os.unlink(xml_file_path)


async def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring."""
    print("\n=== Performance Monitoring ===")
    
    # Create XML configuration
    xml_config = create_advanced_forest_xml()
    
    # Create temporary XML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(xml_config)
        xml_file_path = f.name
    
    try:
        # Load forest from XML
        parser = XMLParser()
        forest = parser.parse_file(xml_file_path)
        
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
            "total_nodes": len(forest.nodes),
            "active_nodes": len(forest.nodes),
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
                
    finally:
        os.unlink(xml_file_path)


async def demonstrate_real_time_dashboard():
    """Demonstrate real-time dashboard."""
    print("\n=== Real-Time Dashboard ===")
    
    # Create XML configuration
    xml_config = create_advanced_forest_xml()
    
    # Create temporary XML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(xml_config)
        xml_file_path = f.name
    
    try:
        # Load forest from XML
        parser = XMLParser()
        forest = parser.parse_file(xml_file_path)
        
        # Simulate dashboard data
        print("📊 Real-time dashboard:")
        print("  ┌─────────────────────────────────────┐")
        print("  │         Forest Dashboard            │")
        print("  ├─────────────────────────────────────┤")
        print("  │ Forest Status: 🟢 Running          │")
        print(f"  │ Active Nodes: {len(forest.nodes)}/{len(forest.nodes)}                  │")
        print("  │ Total Ticks: 1,250                 │")
        print("  │ Health Score: 93%                  │")
        print("  ├─────────────────────────────────────┤")
        print("  │ Node Status:                        │")
        for node_name, node in forest.nodes.items():
            print(f"  │  🤖 {node_name}: 🟢 Active           │")
        print("  └─────────────────────────────────────┘")
        
    finally:
        os.unlink(xml_file_path)


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
    
    # Create XML configuration
    xml_config = create_advanced_forest_xml()
    
    # Create temporary XML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(xml_config)
        xml_file_path = f.name
    
    try:
        # Load forest from XML
        parser = XMLParser()
        forest = parser.parse_file(xml_file_path)
        
        # Start forest
        await forest.start()
        
        # Run for a few ticks
        for i in range(3):
            print(f"\n--- Advanced Features Tick {i+1} ---")
            await asyncio.sleep(0.01)
        
        # Stop forest
        await forest.stop()
        
        print("\nAdvanced forest features demonstration completed!")
        
    finally:
        # Clean up temporary file
        os.unlink(xml_file_path)


if __name__ == "__main__":
    asyncio.run(main()) 