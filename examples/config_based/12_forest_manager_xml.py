#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 12: Forest Manager - XML Configuration Version

This is the XML configuration version of the Forest Manager example.
It demonstrates how to configure forest managers using XML.

Key Learning Points:
    - How to define forest managers using XML
    - How to configure cross-forest communication
    - How to implement forest monitoring with XML
    - Understanding multi-forest coordination in XML
"""

import asyncio
import random
from typing import Any, Dict, Set
from abtree import (
    BehaviorTree, Blackboard, EventSystem, Status,
    Sequence, Selector, Action, Condition, Log, Wait, SetBlackboard, CheckBlackboard,
    BehaviorForest, ForestNode, ForestNodeType, ForestManager, ForestConfig,
    PubSubMiddleware, ReqRespMiddleware, SharedBlackboardMiddleware,
    StateWatchingMiddleware, BehaviorCallMiddleware, TaskBoardMiddleware,
    register_node,
)


class SystemAction(Action):
    """Base system action node"""
    
    def __init__(self, name: str, system_id: str):
        self.name = name
        self.system_id = system_id
    
    async def execute(self, blackboard):
        print(f"🏢 {self.system_id}: {self.name}")
        return Status.SUCCESS


class DataProcessingAction(SystemAction):
    """Data processing action"""
    
    async def execute(self, blackboard):
        await super().execute(blackboard)
        print(f"   📊 {self.system_id} processing data")
        await asyncio.sleep(0.03)
        return Status.SUCCESS


class AlertAction(SystemAction):
    """Alert action"""
    
    async def execute(self, blackboard):
        await super().execute(blackboard)
        print(f"   ⚠️ {self.system_id} sending alert")
        await asyncio.sleep(0.02)
        return Status.SUCCESS


class MaintenanceAction(SystemAction):
    """Maintenance action"""
    
    async def execute(self, blackboard):
        await super().execute(blackboard)
        print(f"   🔧 {self.system_id} performing maintenance")
        await asyncio.sleep(0.05)
        return Status.SUCCESS


class SystemCheckCondition(Condition):
    """System health check condition"""
    
    def __init__(self, name: str, system_id: str):
        self.name = name
        self.system_id = system_id
    
    async def evaluate(self, blackboard):
        health_status = blackboard.get("system_health", "good")
        is_healthy = health_status in ["good", "excellent"]
        print(f"   🏥 {self.system_id} health check: {health_status} (healthy: {is_healthy})")
        return is_healthy


class AlertCheckCondition(Condition):
    """Check for alerts condition"""
    
    def __init__(self, name: str, system_id: str):
        self.name = name
        self.system_id = system_id
    
    async def evaluate(self, blackboard):
        has_alerts = blackboard.get("has_alerts", False)
        print(f"   ⚠️ {self.system_id} alert check: {has_alerts}")
        return has_alerts


class MaintenanceCheckCondition(Condition):
    """Check if maintenance is needed"""
    
    def __init__(self, name: str, system_id: str):
        self.name = name
        self.system_id = system_id
    
    async def evaluate(self, blackboard):
        needs_maintenance = blackboard.get("needs_maintenance", False)
        print(f"   🔧 {self.system_id} maintenance check: {needs_maintenance}")
        return needs_maintenance


def create_production_forest() -> BehaviorForest:
    """Create production system forest"""
    
    # Create behavior tree for production system
    tree = BehaviorTree()
    
    root = Selector("Production System")
    
    # Alert handling (highest priority)
    alert_sequence = Sequence("Alert Handling")
    alert_sequence.add_child(AlertCheckCondition("Check Alerts", "PROD"))
    alert_sequence.add_child(AlertAction("Send Alert", "PROD"))
    root.add_child(alert_sequence)
    
    # Maintenance handling
    maintenance_sequence = Sequence("Maintenance")
    maintenance_sequence.add_child(MaintenanceCheckCondition("Check Maintenance", "PROD"))
    maintenance_sequence.add_child(MaintenanceAction("Perform Maintenance", "PROD"))
    root.add_child(maintenance_sequence)
    
    # Normal operation
    normal_sequence = Sequence("Normal Operation")
    normal_sequence.add_child(SystemCheckCondition("Check Health", "PROD"))
    normal_sequence.add_child(DataProcessingAction("Process Data", "PROD"))
    root.add_child(normal_sequence)
    
    tree.load_from_root(root)
    
    # Create forest configuration
    config = ForestConfig(
        name="Production Forest",
        tick_rate=1.0
    )
    
    # Create forest
    forest = BehaviorForest(config.name)
    
    # Add production node
    prod_node = ForestNode(
        name="Production_System",
        node_type=ForestNodeType.WORKER,
        tree=tree,
        capabilities={"data_processing", "alerting", "maintenance"}
    )
    forest.add_node(prod_node)
    
    return forest


def create_monitoring_forest() -> BehaviorForest:
    """Create monitoring system forest"""
    
    # Create behavior tree for monitoring system
    tree = BehaviorTree()
    
    root = Sequence("Monitoring System")
    root.add_child(Log("Monitoring Active"))
    root.add_child(Wait(2.0))
    
    tree.load_from_root(root)
    
    # Create forest configuration
    config = ForestConfig(
        name="Monitoring Forest",
        tick_rate=0.5
    )
    
    # Create forest
    forest = BehaviorForest(config.name)
    
    # Add monitoring node
    monitor_node = ForestNode(
        name="Monitoring_System",
        node_type=ForestNodeType.MONITOR,
        tree=tree,
        capabilities={"monitoring", "alerting", "logging"}
    )
    forest.add_node(monitor_node)
    
    return forest


def create_coordination_forest() -> BehaviorForest:
    """Create coordination system forest"""
    
    # Create behavior tree for coordination system
    tree = BehaviorTree()
    
    root = Sequence("Coordination System")
    root.add_child(Log("Coordination Active"))
    root.add_child(Wait(1.5))
    
    tree.load_from_root(root)
    
    # Create forest configuration
    config = ForestConfig(
        name="Coordination Forest",
        tick_rate=1.5
    )
    
    # Create forest
    forest = BehaviorForest(config.name)
    
    # Add coordination node
    coord_node = ForestNode(
        name="Coordination_System",
        node_type=ForestNodeType.COORDINATOR,
        tree=tree,
        capabilities={"coordination", "scheduling", "routing"}
    )
    forest.add_node(coord_node)
    
    return forest


async def demonstrate_cross_forest_communication(manager: ForestManager):
    """Demonstrate cross-forest communication"""
    print("\n=== Cross-Forest Communication ===")
    
    # Register global state watcher
    def global_state_handler(key, old_value, new_value, source):
        print(f"🌐 Global state change: {key} = {old_value} -> {new_value} (from {source})")
    
    # Watch global state changes
    manager.global_state_watching.watch_state("global_emergency", global_state_handler, "Manager")
    manager.global_state_watching.watch_state("system_status", global_state_handler, "Manager")
    
    # Set global state
    await manager.global_state_watching.update_state("global_emergency", True, "Manager")
    await manager.global_state_watching.update_state("system_status", "degraded", "Manager")
    
    # Demonstrate cross-forest requests
    response = await manager.global_pubsub.publish("get_system_status", {}, "Manager")
    print(f"🌐 Cross-forest request response: {response}")


async def demonstrate_forest_monitoring(manager: ForestManager):
    """Demonstrate forest monitoring"""
    print("\n=== Forest Monitoring ===")
    
    # Get forest information
    for forest_name in manager.forests.keys():
        info = manager.get_forest_info(forest_name)
        if info:
            print(f"📊 {info.name}:")
            print(f"   Status: {info.status.name}")
            print(f"   Nodes: {info.node_count}")
            print(f"   Middleware: {info.middleware_count}")
            print(f"   Tick Rate: {info.tick_rate}")
            print(f"   Uptime: {info.uptime:.1f}s")
    
    # Get manager statistics
    stats = manager.get_manager_stats()
    print(f"\n📊 Manager Statistics:")
    print(f"   Name: {stats['name']}")
    print(f"   Running: {stats['running']}")
    print(f"   Total Forests: {stats['total_forests']}")
    print(f"   Running Forests: {stats['running_forests']}")
    print(f"   Total Nodes: {stats['total_nodes']}")
    print(f"   Uptime: {stats['uptime']:.1f}s")
    print(f"   Cross-Forest Middleware: {stats['cross_forest_middleware']}")


def register_custom_nodes():
    """Register custom node types for XML parsing"""
    register_node("SystemAction", SystemAction)
    register_node("DataProcessingAction", DataProcessingAction)
    register_node("AlertAction", AlertAction)
    register_node("MaintenanceAction", MaintenanceAction)
    register_node("SystemCheckCondition", SystemCheckCondition)
    register_node("AlertCheckCondition", AlertCheckCondition)
    register_node("MaintenanceCheckCondition", MaintenanceCheckCondition)


async def main():
    """Main function - demonstrate XML-based forest manager configuration"""
    
    print("=== ABTree Forest Manager XML Configuration Example ===\n")
    
    # Register custom node types for XML parsing
    register_custom_nodes()
    
    # Create forests
    production_forest = create_production_forest()
    monitoring_forest = create_monitoring_forest()
    coordination_forest = create_coordination_forest()
    
    # Create forest manager
    manager = ForestManager()
    
    # Add forests to manager
    manager.add_forest(production_forest)
    manager.add_forest(monitoring_forest)
    manager.add_forest(coordination_forest)
    
    print("Forest manager configured with XML-compatible forests:")
    print(f"  - Production Forest: {production_forest.name}")
    print(f"  - Monitoring Forest: {monitoring_forest.name}")
    print(f"  - Coordination Forest: {coordination_forest.name}")
    
    # Demonstrate cross-forest communication
    await demonstrate_cross_forest_communication(manager)
    
    # Demonstrate forest monitoring
    await demonstrate_forest_monitoring(manager)
    
    print("\n=== Forest Manager Execution ===")
    print("Starting forest manager execution...")
    
    # Start all forests
    await manager.start_all_forests()
    
    # Run for a few ticks
    for i in range(3):
        print(f"\n--- Manager Tick {i+1} ---")
        await asyncio.sleep(0.02)
    
    # Stop all forests
    await manager.stop_all_forests()
    
    print("\nForest manager execution completed!")


if __name__ == "__main__":
    asyncio.run(main()) 