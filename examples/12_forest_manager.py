"""
Forest Manager Example - Multi-Forest Coordination

This example demonstrates the Forest Manager for coordinating multiple
behavior forests with cross-forest communication.
"""

import asyncio
import random
from typing import Any, Dict, Set

from abtree import (
    # Core components
    BehaviorTree, Blackboard, EventSystem, Status,
    # Node types
    Sequence, Selector, Action, Condition, Log, Wait, SetBlackboard, CheckBlackboard,
    # Forest components
    BehaviorForest, ForestNode, ForestNodeType, ForestManager, ForestConfig,
)
from abtree.forest.communication import (
    CommunicationMiddleware,
    CommunicationType,
    Message,
    Request,
    Response,
    Task,
)


# ==================== Custom Node Definitions ====================

class SystemAction(Action):
    """Base system action node"""
    
    def __init__(self, name: str, system_id: str):
        super().__init__(name)
        self.system_id = system_id
    
    async def execute(self, blackboard):
        print(f"🏢 {self.system_id}: {self.name}")
        return Status.SUCCESS


class DataProcessingAction(SystemAction):
    """Data processing action"""
    
    async def execute(self, blackboard):
        await super().execute(blackboard)
        print(f"   📊 {self.system_id} processing data")
        await asyncio.sleep(0.01)
        return Status.SUCCESS


class AlertAction(SystemAction):
    """Alert action"""
    
    async def execute(self, blackboard):
        await super().execute(blackboard)
        print(f"   ⚠️ {self.system_id} sending alert")
        await asyncio.sleep(0.01)
        return Status.SUCCESS


class MaintenanceAction(SystemAction):
    """Maintenance action"""
    
    async def execute(self, blackboard):
        await super().execute(blackboard)
        print(f"   🔧 {self.system_id} performing maintenance")
        await asyncio.sleep(0.01)
        return Status.SUCCESS


class SystemCheckCondition(Condition):
    """System health check condition"""
    
    def __init__(self, name: str, system_id: str):
        super().__init__(name)
        self.system_id = system_id
    
    async def evaluate(self, blackboard):
        health_status = blackboard.get("system_health", "good")
        is_healthy = health_status in ["good", "excellent"]
        print(f"   🏥 {self.system_id} health check: {health_status} (healthy: {is_healthy})")
        return is_healthy


class AlertCheckCondition(Condition):
    """Check for alerts condition"""
    
    def __init__(self, name: str, system_id: str):
        super().__init__(name)
        self.system_id = system_id
    
    async def evaluate(self, blackboard):
        has_alerts = blackboard.get("has_alerts", False)
        print(f"   ⚠️ {self.system_id} alert check: {has_alerts}")
        return has_alerts


class MaintenanceCheckCondition(Condition):
    """Check if maintenance is needed"""
    
    def __init__(self, name: str, system_id: str):
        super().__init__(name)
        self.system_id = system_id
    
    async def evaluate(self, blackboard):
        needs_maintenance = blackboard.get("needs_maintenance", False)
        print(f"   🔧 {self.system_id} maintenance check: {needs_maintenance}")
        return needs_maintenance


# ==================== Forest Builders ====================

def create_production_forest() -> BehaviorForest:
    """Create production system forest"""
    
    # Create behavior tree
    root = Selector("Production System Decision")
    
    # Alert handling branch
    alert_branch = Sequence("Alert Handling")
    alert_branch.add_child(AlertCheckCondition("Check Alerts", "Production"))
    alert_branch.add_child(AlertAction("Send Alert", "Production"))
    
    # Maintenance branch
    maintenance_branch = Sequence("Maintenance")
    maintenance_branch.add_child(MaintenanceCheckCondition("Check Maintenance", "Production"))
    maintenance_branch.add_child(MaintenanceAction("Perform Maintenance", "Production"))
    
    # Data processing branch
    data_branch = Sequence("Data Processing")
    data_branch.add_child(SystemCheckCondition("Check System Health", "Production"))
    data_branch.add_child(DataProcessingAction("Process Data", "Production"))
    
    # Assemble tree
    root.add_child(alert_branch)
    root.add_child(maintenance_branch)
    root.add_child(data_branch)
    
    # Create behavior tree
    tree = BehaviorTree()
    tree.load_from_node(root)
    
    # Initialize blackboard
    blackboard = tree.blackboard
    blackboard.set("system_health", "good")
    blackboard.set("has_alerts", False)
    blackboard.set("needs_maintenance", False)
    
    # Create forest
    forest = BehaviorForest(
        name="ProductionForest",
        forest_blackboard=Blackboard(),
        forest_event_system=EventSystem()
    )
    
    # Add middleware
    forest.add_middleware(CommunicationMiddleware("ProductionCommunication"))
    
    # Create and add forest node
    node = ForestNode(
        name="ProductionSystem",
        tree=tree,
        node_type=ForestNodeType.WORKER,
        capabilities={"production", "data_processing", "maintenance"}
    )
    forest.add_node(node)
    
    return forest


def create_monitoring_forest() -> BehaviorForest:
    """Create monitoring system forest"""
    
    # Create behavior tree
    root = Sequence("Monitoring System Main")
    
    # System monitoring
    system_monitoring = Sequence("System Monitoring")
    system_monitoring.add_child(Log(name="Monitor Systems", message="Monitoring all systems"))
    system_monitoring.add_child(Wait(name="Monitor Wait", duration=1.0))
    
    # Performance tracking
    performance_tracking = Sequence("Performance Tracking")
    performance_tracking.add_child(Log(name="Track Performance", message="Tracking performance metrics"))
    performance_tracking.add_child(Wait(name="Performance Wait", duration=0.8))
    
    # Health reporting
    health_reporting = Sequence("Health Reporting")
    health_reporting.add_child(Log(name="Report Health", message="Reporting system health"))
    health_reporting.add_child(Wait(name="Health Wait", duration=1.2))
    
    # Assemble tree
    root.add_child(system_monitoring)
    root.add_child(performance_tracking)
    root.add_child(health_reporting)
    
    # Create behavior tree
    tree = BehaviorTree()
    tree.load_from_node(root)
    
    # Create forest
    forest = BehaviorForest(
        name="MonitoringForest",
        forest_blackboard=Blackboard(),
        forest_event_system=EventSystem()
    )
    
    # Add middleware
    forest.add_middleware(CommunicationMiddleware("MonitoringCommunication"))
    
    # Create and add forest node
    node = ForestNode(
        name="MonitoringSystem",
        tree=tree,
        node_type=ForestNodeType.MONITOR,
        capabilities={"monitoring", "performance_tracking", "health_check"}
    )
    forest.add_node(node)
    
    return forest


def create_coordination_forest() -> BehaviorForest:
    """Create coordination system forest"""
    
    # Create behavior tree
    root = Selector("Coordination System Decision")
    
    # Task coordination
    task_coordination = Sequence("Task Coordination")
    task_coordination.add_child(Log(name="Coordinate Tasks", message="Coordinating tasks across systems"))
    task_coordination.add_child(Wait(name="Task Wait", duration=0.5))
    
    # Resource management
    resource_management = Sequence("Resource Management")
    resource_management.add_child(Log(name="Manage Resources", message="Managing system resources"))
    resource_management.add_child(Wait(name="Resource Wait", duration=0.7))
    
    # Communication
    communication = Sequence("Communication")
    communication.add_child(Log(name="Communicate", message="Facilitating inter-system communication"))
    communication.add_child(Wait(name="Communication Wait", duration=0.3))
    
    # Assemble tree
    root.add_child(task_coordination)
    root.add_child(resource_management)
    root.add_child(communication)
    
    # Create behavior tree
    tree = BehaviorTree()
    tree.load_from_node(root)
    
    # Create forest
    forest = BehaviorForest(
        name="CoordinationForest",
        forest_blackboard=Blackboard(),
        forest_event_system=EventSystem()
    )
    
    # Add middleware
    forest.add_middleware(CommunicationMiddleware("CoordinationCommunication"))
    
    # Create and add forest node
    node = ForestNode(
        name="CoordinationSystem",
        tree=tree,
        node_type=ForestNodeType.COORDINATOR,
        capabilities={"coordination", "resource_management", "communication"}
    )
    forest.add_node(node)
    
    return forest


# ==================== Cross-Forest Communication Examples ====================

async def demonstrate_cross_forest_communication(manager: ForestManager):
    """Demonstrate cross-forest communication"""
    print("\n=== 🌐 Cross-Forest Communication ===")
    
    # Publish global events
    manager.publish_global_event("system_alert", {
        "level": "high",
        "message": "Critical system failure detected",
        "timestamp": asyncio.get_event_loop().time()
    })
    
    # Set global data
    manager.set_global_data("total_systems", 3)
    manager.set_global_data("system_status", "operational")
    manager.set_global_data("alert_count", 0)
    
    # Watch global state
    def global_state_handler(key, old_value, new_value, source):
        print(f"🌐 Global state change: {key} = {old_value} -> {new_value} (from {source})")
    
    manager.watch_global_state("system_status", global_state_handler)
    manager.watch_global_state("alert_count", global_state_handler)
    
    # Publish global tasks
    task1_id = manager.publish_global_task(
        "System Health Check",
        "Perform comprehensive health check on all systems",
        {"monitoring", "health_check"},
        priority=4
    )
    
    task2_id = manager.publish_global_task(
        "Performance Optimization",
        "Optimize system performance across all forests",
        {"optimization", "performance"},
        priority=3
    )
    
    print(f"🌐 Published global tasks: {task1_id}, {task2_id}")
    
    await asyncio.sleep(0.01)


async def demonstrate_forest_monitoring(manager: ForestManager):
    """Demonstrate forest monitoring capabilities"""
    print("\n=== 📊 Forest Monitoring ===")
    
    # Get forest information
    for forest_name in ["ProductionForest", "MonitoringForest", "CoordinationForest"]:
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


# ==================== Main Function ====================

async def main():
    """Main function - demonstrate forest manager"""
    
    print("=== 🌳 Forest Manager Example ===")
    print("Demonstrating multi-forest coordination and cross-forest communication")
    
    # 1. Create forest manager
    manager = ForestManager("EnterpriseManager")
    print(f"🏢 Created forest manager: {manager.name}")
    
    # 2. Create forests
    production_forest = create_production_forest()
    monitoring_forest = create_monitoring_forest()
    coordination_forest = create_coordination_forest()
    
    print("🏭 Created production forest")
    print("📊 Created monitoring forest")
    print("🎯 Created coordination forest")
    
    # 3. Add forests to manager
    manager.add_forest(production_forest)
    manager.add_forest(monitoring_forest)
    manager.add_forest(coordination_forest)
    
    print("✅ Added all forests to manager")
    
    # 4. Start manager
    print("\n🚀 Starting forest manager...")
    await manager.start()
    
    # 5. Demonstrate cross-forest communication
    await demonstrate_cross_forest_communication(manager)
    
    # 6. Run forests for a few ticks
    print("\n=== 🌳 Running Forests ===")
    for i in range(8):
        print(f"\n--- Tick {i+1} ---")
        
        # Simulate some events
        if i == 2:
            # Trigger system alert
            manager.set_global_data("alert_count", 1)
            manager.publish_global_event("system_alert", {
                "level": "critical",
                "message": "Production system failure",
                "timestamp": asyncio.get_event_loop().time()
            })
            print("🚨 System alert triggered!")
        
        elif i == 4:
            # Update system status
            manager.set_global_data("system_status", "degraded")
            print("⚠️ System status degraded!")
        
        elif i == 6:
            # Restore system status
            manager.set_global_data("system_status", "operational")
            manager.set_global_data("alert_count", 0)
            print("✅ System status restored!")
        
        # Wait for next tick
        await asyncio.sleep(0.01)
    
    # 7. Demonstrate monitoring
    await demonstrate_forest_monitoring(manager)
    
    # 8. Stop manager
    print("\n🛑 Stopping forest manager...")
    await manager.stop()
    
    # 9. Display final statistics
    final_stats = manager.get_manager_stats()
    print(f"\n📊 Final Statistics:")
    print(f"   Total Forests: {final_stats['total_forests']}")
    print(f"   Total Nodes: {final_stats['total_nodes']}")
    print(f"   Cross-Forest Middleware: {final_stats['cross_forest_middleware']}")
    
    print("\n✅ Forest Manager example completed!")


if __name__ == "__main__":
    asyncio.run(main()) 