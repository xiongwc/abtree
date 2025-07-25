#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 10: Advanced Control Flow - XML Configuration Version

This is the XML configuration version of the Advanced Control Flow example.
It demonstrates how to configure advanced control flow patterns using XML.

Key Learning Points:
    - How to define state machine patterns using XML
    - How to configure event-driven control flow in XML
    - How to implement priority queues with XML
    - Understanding dynamic decision-making in XML
    - Complex branching logic in XML configuration
"""

import asyncio
import random
import time
from abtree import BehaviorTree, Action, register_node
from abtree.core import Status
from abtree.nodes.base import BaseNode


class StateMachine(BaseNode):
    """State machine node for advanced control flow"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.current_state = "idle"
        self.state_transitions = {
            "idle": self.idle_state,
            "working": self.working_state,
            "error": self.error_state,
            "recovery": self.recovery_state
        }
    
    async def idle_state(self, blackboard):
        """Idle state logic"""
        print("State Machine: In idle state")
        battery_level = blackboard.get("battery_level", 100)
        
        if battery_level < 30:
            self.current_state = "error"
            return Status.RUNNING
        elif blackboard.get("has_work", False):
            self.current_state = "working"
            return Status.RUNNING
        else:
            return Status.SUCCESS
    
    async def working_state(self, blackboard):
        """Working state logic"""
        print("State Machine: In working state")
        battery_level = blackboard.get("battery_level", 100)
        work_progress = blackboard.get("work_progress", 0)
        
        # Simulate work progress
        work_progress += 10
        blackboard.set("work_progress", min(100, work_progress))
        
        if battery_level < 20:
            self.current_state = "error"
            return Status.RUNNING
        elif work_progress >= 100:
            self.current_state = "idle"
            blackboard.set("has_work", False)
            return Status.SUCCESS
        else:
            return Status.RUNNING
    
    async def error_state(self, blackboard):
        """Error state logic"""
        print("State Machine: In error state")
        self.current_state = "recovery"
        return Status.RUNNING
    
    async def recovery_state(self, blackboard):
        """Recovery state logic"""
        print("State Machine: In recovery state")
        self.current_state = "idle"
        return Status.SUCCESS
    
    async def tick(self):
        """Execute state machine"""
        if not self.blackboard:
            return Status.FAILURE
            
        current_state_func = self.state_transitions.get(self.current_state)
        if current_state_func:
            return await current_state_func(self.blackboard)
        return Status.FAILURE


class EventDrivenController(BaseNode):
    """Event-driven controller node"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.events = []
        self.event_handlers = {
            "emergency": self.handle_emergency,
            "normal": self.handle_normal,
            "maintenance": self.handle_maintenance
        }
    
    def add_event(self, event_type, priority=1):
        """Add event to queue"""
        self.events.append((event_type, priority))
        self.events.sort(key=lambda x: x[1], reverse=True)
    
    async def handle_emergency(self, blackboard):
        """Handle emergency event"""
        print("Event Controller: Handling emergency event")
        return Status.SUCCESS
    
    async def handle_normal(self, blackboard):
        """Handle normal event"""
        print("Event Controller: Handling normal event")
        return Status.SUCCESS
    
    async def handle_maintenance(self, blackboard):
        """Handle maintenance event"""
        print("Event Controller: Handling maintenance event")
        return Status.SUCCESS
    
    async def tick(self):
        """Execute event-driven controller"""
        if not self.blackboard:
            return Status.FAILURE
            
        if not self.events:
            # Add some test events
            self.add_event("normal", 1)
            self.add_event("maintenance", 2)
        
        if self.events:
            event_type, priority = self.events.pop(0)
            handler = self.event_handlers.get(event_type)
            if handler:
                return await handler(self.blackboard)
        
        return Status.SUCCESS


class PriorityQueue(BaseNode):
    """Priority queue node for task management"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.tasks = []
    
    def add_task(self, task, priority=1):
        """Add task to priority queue"""
        self.tasks.append((task, priority))
        self.tasks.sort(key=lambda x: x[1], reverse=True)
    
    async def tick(self):
        """Execute priority queue"""
        if not self.blackboard:
            return Status.FAILURE
            
        if not self.tasks:
            # Add some test tasks
            self.add_task("Process data", 3)
            self.add_task("Update system", 2)
            self.add_task("Clean cache", 1)
        
        if self.tasks:
            task, priority = self.tasks.pop(0)
            print(f"Priority Queue: Executing task '{task}' with priority {priority}")
            tasks_completed = self.blackboard.get("tasks_completed", 0)
            self.blackboard.set("tasks_completed", tasks_completed + 1)
            return Status.SUCCESS
        
        return Status.SUCCESS


class DynamicDecisionMaker(BaseNode):
    """Dynamic decision maker node"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.decision_count = 0
    
    async def tick(self):
        """Execute dynamic decision maker"""
        if not self.blackboard:
            return Status.FAILURE
            
        self.decision_count += 1
        battery_level = self.blackboard.get("battery_level", 100)
        work_load = self.blackboard.get("work_load", 0)
        error_count = self.blackboard.get("error_count", 0)
        
        # Dynamic decision logic
        if error_count > 2:
            decision = "maintenance"
            reason = "High error count"
        elif battery_level < 30:
            decision = "charge"
            reason = "Low battery"
        elif work_load > 80:
            decision = "optimize"
            reason = "High work load"
        else:
            decision = "continue"
            reason = "Normal operation"
        
        self.blackboard.set("last_decision", decision)
        self.blackboard.set("decision_reason", reason)
        self.blackboard.set("decision_count", self.decision_count)
        
        print(f"Dynamic Decision: {decision} - {reason}")
        return Status.SUCCESS


class ChargeAction(Action):
    """Charge action"""
    
    async def execute(self, blackboard):
        print("Executing charge action...")
        await asyncio.sleep(0.05)
        
        current_battery = blackboard.get("battery_level", 100)
        blackboard.set("battery_level", min(100, current_battery + 15))
        
        print("Battery charged")
        return Status.SUCCESS


class OptimizeAction(Action):
    """Optimize action"""
    
    async def execute(self, blackboard):
        print("Executing optimize action...")
        await asyncio.sleep(0.04)
        
        current_work_load = blackboard.get("work_load", 0)
        blackboard.set("work_load", max(0, current_work_load - 10))
        
        print("System optimized")
        return Status.SUCCESS


class MaintenanceAction(Action):
    """Maintenance action"""
    
    async def execute(self, blackboard):
        print("Executing maintenance action...")
        await asyncio.sleep(0.06)
        
        current_errors = blackboard.get("error_count", 0)
        blackboard.set("error_count", max(0, current_errors - 1))
        
        print("Maintenance completed, errors reduced")
        return Status.SUCCESS


def register_custom_nodes():
    """Register custom node types for XML parsing"""
    register_node("StateMachine", StateMachine)
    register_node("EventDrivenController", EventDrivenController)
    register_node("PriorityQueue", PriorityQueue)
    register_node("DynamicDecisionMaker", DynamicDecisionMaker)
    register_node("ChargeAction", ChargeAction)
    register_node("OptimizeAction", OptimizeAction)
    register_node("MaintenanceAction", MaintenanceAction)


async def main():
    """Main function - demonstrate XML-based advanced control flow configuration"""
    
    print("=== ABTree Advanced Control Flow XML Configuration Example ===\n")
    
    # Register custom node types for XML parsing
    register_custom_nodes()
    
    # XML string configuration
    xml_config = '''
    <BehaviorTree name="AdvancedControlFlowXML" description="Advanced control flow example with XML configuration">
        <Sequence name="Root Sequence">
            <Sequence name="State Machine Test">
                <StateMachine name="System State Machine" />
            </Sequence>
            <Sequence name="Event Driven Test">
                <EventDrivenController name="Event Controller" />
            </Sequence>
            <Sequence name="Priority Queue Test">
                <PriorityQueue name="Task Queue" />
            </Sequence>
            <Sequence name="Dynamic Decision Test">
                <DynamicDecisionMaker name="Decision Maker" />
            </Sequence>
            <Selector name="Action Selection">
                <Sequence name="Charge Strategy">
                    <ChargeAction name="Charge Battery" />
                </Sequence>
                <Sequence name="Optimize Strategy">
                    <OptimizeAction name="Optimize System" />
                </Sequence>
                <Sequence name="Maintenance Strategy">
                    <MaintenanceAction name="Perform Maintenance" />
                </Sequence>
            </Selector>
        </Sequence>
    </BehaviorTree>
    '''
    
    # Parse XML configuration
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    xml_blackboard = xml_tree.blackboard
    
    # Initialize blackboard data
    xml_blackboard.set("battery_level", 75)
    xml_blackboard.set("work_load", 60)
    xml_blackboard.set("error_count", 2)
    xml_blackboard.set("has_work", True)
    xml_blackboard.set("work_progress", 0)
    xml_blackboard.set("decision_count", 0)
    xml_blackboard.set("tasks_completed", 0)
    
    print("Behavior tree configured by XML string:")
    print(xml_config.strip())
    print("\nStarting execution of XML-configured behavior tree...")
    
    # Execute behavior tree
    xml_result = await xml_tree.tick()
    
    print(f"\nXML configuration execution completed! Result: {xml_result}")
    print(f"Battery level: {xml_blackboard.get('battery_level')}%")
    print(f"Work load: {xml_blackboard.get('work_load')}%")
    print(f"Error count: {xml_blackboard.get('error_count')}")
    print(f"Work progress: {xml_blackboard.get('work_progress')}%")
    print(f"Last decision: {xml_blackboard.get('last_decision', 'None')}")
    print(f"Decision reason: {xml_blackboard.get('decision_reason', 'None')}")
    print(f"Decision count: {xml_blackboard.get('decision_count')}")
    print(f"Tasks completed: {xml_blackboard.get('tasks_completed')}")


if __name__ == "__main__":
    asyncio.run(main()) 