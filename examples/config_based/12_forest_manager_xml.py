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
import tempfile
import os
from typing import Any, Dict, Set
from abtree import (
    BehaviorTree, Blackboard, EventSystem, Status,
    Sequence, Selector, Action, Condition, Log, Wait, SetBlackboard, CheckBlackboard,
    BehaviorForest, ForestNode, ForestNodeType, ForestManager,
    PubSubMiddleware, ReqRespMiddleware, SharedBlackboardMiddleware,
    StateWatchingMiddleware, BehaviorCallMiddleware, TaskBoardMiddleware,
    register_node,
)
from abtree.parser.xml_parser import XMLParser


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


def create_production_forest_xml() -> str:
    """Create XML configuration for production forest"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<BehaviorForest name="ProductionForest" description="Production System Forest">
    
    <!-- Production System Behavior Tree -->
    <BehaviorTree name="Production_System" description="Production System Service">
        <Selector name="Production System Decision">
            <Sequence name="Alert Handling">
                <AlertCheckCondition name="Check Alerts" system_id="PROD" />
                <AlertAction name="Send Alert" system_id="PROD" />
            </Sequence>
            <Sequence name="Maintenance">
                <MaintenanceCheckCondition name="Check Maintenance" system_id="PROD" />
                <MaintenanceAction name="Perform Maintenance" system_id="PROD" />
            </Sequence>
            <Sequence name="Normal Operation">
                <SystemCheckCondition name="Check Health" system_id="PROD" />
                <DataProcessingAction name="Process Data" system_id="PROD" />
            </Sequence>
        </Selector>
    </BehaviorTree>
    
    <!-- Communication Configuration -->
    <Communication>
        <!-- Pub/Sub Communication -->
        <ComTopic name="production_events">
            <ComPublisher service="Production_System" />
            <ComSubscriber service="Monitoring_System" />
        </ComTopic>
        
        <!-- Shared Blackboard -->
        <ComShared>
            <ComKey name="system_health" />
            <ComKey name="has_alerts" />
            <ComKey name="needs_maintenance" />
        </ComShared>
        
        <!-- State Watching -->
        <ComState name="production_state">
            <ComWatcher service="Monitoring_System" />
            <ComWatcher service="Coordination_System" />
        </ComState>
    </Communication>
    
</BehaviorForest>'''


def create_monitoring_forest_xml() -> str:
    """Create XML configuration for monitoring forest"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<BehaviorForest name="MonitoringForest" description="Monitoring System Forest">
    
    <!-- Monitoring System Behavior Tree -->
    <BehaviorTree name="Monitoring_System" description="Monitoring System Service">
        <Sequence name="Monitoring Behavior">
            <Log name="Monitor Active" message="Monitoring system is active" />
            <Wait name="Monitor Wait" duration="2.0" />
        </Sequence>
    </BehaviorTree>
    
    <!-- Communication Configuration -->
    <Communication>
        <!-- Pub/Sub Communication -->
        <ComTopic name="monitoring_events">
            <ComPublisher service="Monitoring_System" />
            <ComSubscriber service="Coordination_System" />
        </ComTopic>
        
        <!-- Shared Blackboard -->
        <ComShared>
            <ComKey name="monitoring_status" />
            <ComKey name="alert_level" />
        </ComShared>
        
        <!-- State Watching -->
        <ComState name="monitoring_state">
            <ComWatcher service="Coordination_System" />
        </ComState>
    </Communication>
    
</BehaviorForest>'''


def create_coordination_forest_xml() -> str:
    """Create XML configuration for coordination forest"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<BehaviorForest name="CoordinationForest" description="Coordination System Forest">
    
    <!-- Coordination System Behavior Tree -->
    <BehaviorTree name="Coordination_System" description="Coordination System Service">
        <Sequence name="Coordination Behavior">
            <Log name="Coordinator Active" message="Coordination system is active" />
            <Wait name="Coordinator Wait" duration="1.5" />
        </Sequence>
    </BehaviorTree>
    
    <!-- Communication Configuration -->
    <Communication>
        <!-- Pub/Sub Communication -->
        <ComTopic name="coordination_events">
            <ComPublisher service="Coordination_System" />
            <ComSubscriber service="Production_System" />
            <ComSubscriber service="Monitoring_System" />
        </ComTopic>
        
        <!-- Request/Response Communication -->
        <ComService name="system_status">
            <ComServer service="Coordination_System" />
            <ComClient service="Production_System" />
            <ComClient service="Monitoring_System" />
        </ComService>
        
        <!-- Shared Blackboard -->
        <ComShared>
            <ComKey name="coordination_status" />
            <ComKey name="system_status" />
        </ComShared>
        
        <!-- Task Board -->
        <ComTask name="maintenance_task">
            <ComPublisher service="Coordination_System" />
            <ComClaimant service="Production_System" />
        </ComTask>
    </Communication>
    
</BehaviorForest>'''


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
    await manager.global_pubsub.publish("get_system_status", {}, "Manager")
    print("🌐 Cross-forest request sent")


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
    
    # Create XML configurations
    production_xml = create_production_forest_xml()
    monitoring_xml = create_monitoring_forest_xml()
    coordination_xml = create_coordination_forest_xml()
    
    # Create temporary XML files
    xml_files = []
    try:
        # Create temporary files for each forest
        for i, (xml_content, forest_name) in enumerate([
            (production_xml, "production_forest.xml"),
            (monitoring_xml, "monitoring_forest.xml"),
            (coordination_xml, "coordination_forest.xml")
        ]):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                f.write(xml_content)
                xml_files.append(f.name)
        
        # Initialize XML parser
        parser = XMLParser()
        
        # Load forests from XML
        forests = []
        forest_names = ["Production Forest", "Monitoring Forest", "Coordination Forest"]
        
        for i, xml_file in enumerate(xml_files):
            print(f"Loading {forest_names[i]} from XML...")
            forest = parser.parse_file(xml_file)
            forests.append(forest)
            print(f"  Loaded: {forest.name} with {len(forest.nodes)} nodes")
        
        # Create forest manager
        manager = ForestManager("MultiForestManager")
        
        # Add forests to manager
        for forest in forests:
            manager.add_forest(forest)
        
        print(f"\nForest manager configured with {len(forests)} XML-based forests:")
        for forest in forests:
            print(f"  - {forest.name}")
        
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
        
    finally:
        # Clean up temporary files
        for xml_file in xml_files:
            try:
                os.unlink(xml_file)
            except:
                pass


if __name__ == "__main__":
    asyncio.run(main()) 