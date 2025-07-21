#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 09: Control Flow Basics - XML Configuration Version

This is the XML configuration version of the Control Flow Basics example.
It demonstrates how to configure basic control flow concepts using XML.

Key Learning Points:
    - How to define sequential control flow using XML
    - How to configure conditional branching in XML
    - How to implement looping control with XML
    - Understanding state management in XML configuration
    - Error handling workflows in XML
"""

import asyncio
import random
from abtree import BehaviorTree, Action, Condition, register_node
from abtree.core import Status


class InitializeSystemAction(Action):
    """Initialize system"""
    
    async def execute(self, blackboard):
        print("Step 1: Initializing system...")
        await asyncio.sleep(0.05)
        
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
        await asyncio.sleep(0.03)
        
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
        await asyncio.sleep(0.04)
        
        # Simulate starting services
        services_started = random.random() > 0.1  # 90% success rate
        
        if services_started:
            blackboard.set("services_started", True)
            blackboard.set("init_step", 3)
            print("Services started successfully")
            return Status.SUCCESS
        else:
            print("Service startup failed")
            return Status.FAILURE


class CheckServicesCondition(Condition):
    """Check services status"""
    
    async def evaluate(self, blackboard):
        services_started = blackboard.get("services_started", False)
        print(f"Checking services status: {'Started' if services_started else 'Not started'}")
        return services_started


class HealthCheckAction(Action):
    """Perform health check"""
    
    async def execute(self, blackboard):
        print("Step 4: Performing health check...")
        await asyncio.sleep(0.03)
        
        # Simulate health check
        health_ok = random.random() > 0.15  # 85% success rate
        
        if health_ok:
            blackboard.set("health_check_passed", True)
            blackboard.set("init_step", 4)
            print("Health check passed")
            return Status.SUCCESS
        else:
            print("Health check failed")
            return Status.FAILURE


class RetryAction(Action):
    """Retry action with multiple attempts"""
    
    def __init__(self, name, max_retries=3):
        self.name = name
        self.max_retries = max_retries
        self.retry_count = 0
    
    async def execute(self, blackboard):
        self.retry_count += 1
        print(f"Retry action {self.name}: attempt {self.retry_count}/{self.max_retries}")
        
        # Simulate retry logic
        success = random.random() > 0.5  # 50% success rate
        
        if success:
            print(f"Retry action {self.name}: succeeded on attempt {self.retry_count}")
            return Status.SUCCESS
        elif self.retry_count >= self.max_retries:
            print(f"Retry action {self.name}: failed after {self.max_retries} attempts")
            return Status.FAILURE
        else:
            print(f"Retry action {self.name}: failed, will retry")
            await asyncio.sleep(0.02)
            return Status.RUNNING


class FallbackAction(Action):
    """Fallback action when primary action fails"""
    
    async def execute(self, blackboard):
        print("Executing fallback action...")
        await asyncio.sleep(0.03)
        
        blackboard.set("fallback_executed", True)
        print("Fallback action completed")
        return Status.SUCCESS


class SystemReadyCondition(Condition):
    """Check if system is ready"""
    
    async def evaluate(self, blackboard):
        system_initialized = blackboard.get("system_initialized", False)
        config_loaded = blackboard.get("config_loaded", False)
        services_started = blackboard.get("services_started", False)
        health_check_passed = blackboard.get("health_check_passed", False)
        
        ready = system_initialized and config_loaded and services_started and health_check_passed
        print(f"System ready check: {ready}")
        return ready


class LogStatusAction(Action):
    """Log system status"""
    
    async def execute(self, blackboard):
        print("Logging system status...")
        await asyncio.sleep(0.02)
        
        init_step = blackboard.get("init_step", 0)
        print(f"System initialization step: {init_step}/4")
        
        blackboard.set("status_logged", True)
        print("Status logged successfully")
        return Status.SUCCESS


def register_custom_nodes():
    """Register custom node types for XML parsing"""
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


async def main():
    """Main function - demonstrate XML-based control flow configuration"""
    
    print("=== ABTree Control Flow Basics XML Configuration Example ===\n")
    
    # Register custom node types for XML parsing
    register_custom_nodes()
    
    # XML string configuration
    xml_config = '''
    <BehaviorTree name="ControlFlowBasicXML" description="Control flow basics example with XML configuration">
        <Sequence name="Root Sequence">
            <Sequence name="System Initialization">
                <InitializeSystemAction name="Initialize System" />
                <CheckSystemStatusCondition name="Check System Status" />
                <LoadConfigurationAction name="Load Configuration" />
                <CheckConfigCondition name="Check Config Status" />
                <StartServicesAction name="Start Services" />
                <CheckServicesCondition name="Check Services Status" />
                <HealthCheckAction name="Health Check" />
            </Sequence>
            <Selector name="Error Handling">
                <Sequence name="Retry Strategy">
                    <RetryAction name="Retry Failed Operation" max_retries="3" />
                </Sequence>
                <FallbackAction name="Fallback Strategy" />
            </Selector>
            <Sequence name="System Ready Check">
                <SystemReadyCondition name="Check System Ready" />
                <LogStatusAction name="Log Status" />
            </Sequence>
        </Sequence>
    </BehaviorTree>
    '''
    
    # Parse XML configuration
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    xml_blackboard = xml_tree.blackboard
    
    # Initialize blackboard data
    xml_blackboard.set("system_initialized", False)
    xml_blackboard.set("config_loaded", False)
    xml_blackboard.set("services_started", False)
    xml_blackboard.set("health_check_passed", False)
    xml_blackboard.set("init_step", 0)
    
    print("Behavior tree configured by XML string:")
    print(xml_config.strip())
    print("\nStarting execution of XML-configured behavior tree...")
    
    # Execute behavior tree
    xml_result = await xml_tree.tick()
    
    print(f"\nXML configuration execution completed! Result: {xml_result}")
    print(f"System initialized: {xml_blackboard.get('system_initialized')}")
    print(f"Config loaded: {xml_blackboard.get('config_loaded')}")
    print(f"Services started: {xml_blackboard.get('services_started')}")
    print(f"Health check passed: {xml_blackboard.get('health_check_passed')}")
    print(f"Init step: {xml_blackboard.get('init_step')}")
    print(f"Fallback executed: {xml_blackboard.get('fallback_executed', False)}")
    print(f"Status logged: {xml_blackboard.get('status_logged', False)}")


if __name__ == "__main__":
    asyncio.run(main()) 