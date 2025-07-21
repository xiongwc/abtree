#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 09: Control Flow Basics – Understanding Basic Control Flow Concepts

Demonstrates the basic control flow concepts in behavior trees, including sequence, conditional branching, and loops.
This is the foundation for understanding complex control flows.

Key Learning Points:

    Sequential control flow

    Conditional branching control

    Looping control

    State management

    Error handling workflows

    How to configure control flows using XML strings
"""

import asyncio
import random
from abtree import BehaviorTree, Sequence, Selector, Action, Condition, register_node
from abtree.core import Status
from abtree.parser.xml_parser import XMLParser


# Register custom node types
def register_custom_nodes():
    """Register custom node types"""
    register_node("InitializeSystemAction", InitializeSystemAction)
    register_node("CheckSystemStatusCondition", CheckSystemStatusCondition)
    register_node("LoadConfigurationAction", LoadConfigurationAction)
    register_node("CheckConfigCondition", CheckConfigCondition)
    register_node("StartServicesAction", StartServicesAction)
    register_node("CheckServicesCondition", CheckServicesCondition)
    register_node("HealthCheckAction", HealthCheckAction)
    register_node("RetryAction", RetryAction)
    register_node("FallbackAction", FallbackAction)
    register_node("SystemReadyCondition", SystemReadyCondition)
    register_node("LogStatusAction", LogStatusAction)


class InitializeSystemAction(Action):
    """Initialize system"""
    
    async def execute(self, blackboard):
        print("Step 1: Initializing system...")
        await asyncio.sleep(0.01)
        
        # Set system status
        blackboard.set("system_initialized", True)
        blackboard.set("init_step", 1)
        
        print("System initialization completed")
        return Status.SUCCESS


class CheckSystemStatusCondition(Condition):
    """Check system status"""
    
    async def evaluate(self, blackboard):
        initialized = blackboard.get("system_initialized", False)
        print(f"Checking system status: {'Initialized' if initialized else 'Not initialized'}")
        return initialized


class LoadConfigurationAction(Action):
    """Load configuration"""
    
    async def execute(self, blackboard):
        print("Step 2: Loading configuration file...")
        await asyncio.sleep(0.01)
        
        # Simulate loading configuration
        config_loaded = random.random() > 0.2  # 80% success rate
        
        if config_loaded:
            blackboard.set("config_loaded", True)
            blackboard.set("init_step", 2)
            print("Configuration loaded successfully")
            return Status.SUCCESS
        else:
            print("Configuration loading failed")
            return Status.FAILURE


class CheckConfigCondition(Condition):
    """Check configuration status"""
    
    async def evaluate(self, blackboard):
        config_loaded = blackboard.get("config_loaded", False)
        print(f"Checking configuration status: {'Loaded' if config_loaded else 'Not loaded'}")
        return config_loaded


class StartServicesAction(Action):
    """Start services"""
    
    async def execute(self, blackboard):
        print("Step 3: Starting system services...")
        await asyncio.sleep(0.01)
        
        # Simulate starting services
        services_started = random.random() > 0.1  # 90% success rate
        
        if services_started:
            blackboard.set("services_running", True)
            blackboard.set("init_step", 3)
            print("Services started successfully")
            return Status.SUCCESS
        else:
            print("Services failed to start")
            return Status.FAILURE


class CheckServicesCondition(Condition):
    """Check services status"""
    
    async def evaluate(self, blackboard):
        services_running = blackboard.get("services_running", False)
        print(f"Checking services status: {'Running' if services_running else 'Not running'}")
        return services_running


class HealthCheckAction(Action):
    """Health check"""
    
    async def execute(self, blackboard):
        print("Step 4: Performing health check...")
        await asyncio.sleep(0.01)
        
        # Simulate health check
        health_ok = random.random() > 0.05  # 95% success rate
        
        if health_ok:
            blackboard.set("health_check_passed", True)
            blackboard.set("init_step", 4)
            print("Health check passed")
            return Status.SUCCESS
        else:
            print("Health check failed")
            return Status.FAILURE


class RetryAction(Action):
    """Retry operation"""
    
    def __init__(self, name, max_retries=3):
        super().__init__(name)
        self.max_retries = max_retries
        self.retry_count = 0
    
    async def execute(self, blackboard):
        self.retry_count += 1
        print(f"Retry operation {self.name}: {self.retry_count}/{self.max_retries} times")
        
        # Simulate retry operation
        await asyncio.sleep(0.01)
        success = random.random() > 0.5  # 50% success rate
        
        if success:
            print(f"Retry operation {self.name}: success")
            self.retry_count = 0
            return Status.SUCCESS
        elif self.retry_count >= self.max_retries:
            print(f"Retry operation {self.name}: reached maximum retries, failed")
            self.retry_count = 0
            return Status.FAILURE
        else:
            print(f"Retry operation {self.name}: failed, preparing to retry")
            return Status.RUNNING


class FallbackAction(Action):
    """Fallback operation"""
    
    async def execute(self, blackboard):
        print("Executing fallback operation...")
        await asyncio.sleep(0.01)
        
        # Set fallback state
        blackboard.set("fallback_used", True)
        blackboard.set("system_status", "fallback_mode")
        
        print("Fallback operation completed")
        return Status.SUCCESS


class SystemReadyCondition(Condition):
    """Check if system is ready"""
    
    async def evaluate(self, blackboard):
        step = blackboard.get("init_step", 0)
        ready = step >= 4
        
        print(f"Checking system readiness: step {step}/4, {'Ready' if ready else 'Not ready'}")
        return ready


class LogStatusAction(Action):
    """Log status"""
    
    async def execute(self, blackboard):
        step = blackboard.get("init_step", 0)
        fallback_used = blackboard.get("fallback_used", False)
        
        print(f"Logging system status: step {step}, fallback mode: {fallback_used}")
        await asyncio.sleep(0.01)
        
        return Status.SUCCESS


async def main():
    """Main function - demonstrate basic control flow"""
    
    # Register custom node types
    register_custom_nodes()
    
    print("=== ABTree Control Flow Basic Example ===\n")
    
    # 1. Create root control flow
    root = Selector("System Startup Control Flow")
    
    # 2. Create normal startup flow
    normal_startup = Sequence("Normal Startup Flow")
    
    # Initialize sequence
    init_sequence = Sequence("Initialize Sequence")
    init_sequence.add_child(InitializeSystemAction("Initialize"))
    init_sequence.add_child(CheckSystemStatusCondition("Check System"))
    init_sequence.add_child(LoadConfigurationAction("Load Configuration"))
    init_sequence.add_child(CheckConfigCondition("Check Configuration"))
    init_sequence.add_child(StartServicesAction("Start Services"))
    init_sequence.add_child(CheckServicesCondition("Check Services"))
    init_sequence.add_child(HealthCheckAction("Health Check"))
    
    # Retry mechanism
    retry_sequence = Sequence("Retry Mechanism")
    retry_sequence.add_child(RetryAction("Retry Operation", 3))
    
    # Fallback flow
    fallback_sequence = Sequence("Fallback Flow")
    fallback_sequence.add_child(FallbackAction("Fallback Operation"))
    
    # Status recording
    status_sequence = Sequence("Status Recording")
    status_sequence.add_child(SystemReadyCondition("Check Ready"))
    status_sequence.add_child(LogStatusAction("Log Status"))
    
    # 3. Assemble control flow
    normal_startup.add_child(init_sequence)
    normal_startup.add_child(retry_sequence)
    normal_startup.add_child(status_sequence)
    
    # 4. Add to root node
    root.add_child(normal_startup)
    root.add_child(fallback_sequence)
    
    # 3. Create behavior tree
    tree = BehaviorTree()
    tree.load_from_root(root)
    blackboard = tree.blackboard
    
    # 6. Initialize blackboard data
    blackboard.set("system_initialized", False)
    blackboard.set("config_loaded", False)
    blackboard.set("services_running", False)
    blackboard.set("health_check_passed", False)
    blackboard.set("fallback_used", False)
    blackboard.set("init_step", 0)
    
    print("Start executing system startup control flow...")
    print("=" * 50)
    
    # 7. Execute behavior tree
    result = await tree.tick()
    
    # 8. Display final status
    print("=" * 50)
    print(f"Control flow execution result: {result}")
    print(f"Initialization step: {blackboard.get('init_step')}/4")
    print(f"System status: {blackboard.get('system_status', 'normal')}")
    print(f"Fallback mode used: {blackboard.get('fallback_used')}")
    
    # 9. Demonstrate error handling flow
    print("\n=== Demonstrate Error Handling Flow ===")
    
    # Reset state
    blackboard.set("system_initialized", False)
    blackboard.set("config_loaded", False)
    blackboard.set("services_running", False)
    blackboard.set("health_check_passed", False)
    blackboard.set("fallback_used", False)
    blackboard.set("init_step", 0)
    
    print("Simulate configuration loading failure...")
    result2 = await tree.tick()
    print(f"Error handling result: {result2}")
       



if __name__ == "__main__":
    asyncio.run(main()) 