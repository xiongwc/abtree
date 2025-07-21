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
    """State machine - manages complex state transitions"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.current_state = "idle"
        self.states = {
            "idle": self.idle_state,
            "working": self.working_state,
            "error": self.error_state,
            "recovery": self.recovery_state
        }
        self.transitions = {
            "idle": ["working"],
            "working": ["idle", "error"],
            "error": ["recovery", "idle"],
            "recovery": ["working", "idle"]
        }
    
    async def idle_state(self, blackboard):
        """Idle state"""
        print(f"State machine {self.name}: idle state")
        await asyncio.sleep(0.02)
        
        # Check if there's work to do
        if blackboard.get("has_work", False):
            self.current_state = "working"
            return Status.SUCCESS
        else:
            return Status.RUNNING
    
    async def working_state(self, blackboard):
        """Working state"""
        print(f"State machine {self.name}: working state")
        await asyncio.sleep(0.03)
        
        # Simulate work process
        work_progress = blackboard.get("work_progress", 0)
        work_progress += random.randint(10, 30)
        blackboard.set("work_progress", work_progress)
        
        # Check for errors
        if random.random() < 0.1:  # 10% error probability
            self.current_state = "error"
            blackboard.set("error_count", blackboard.get("error_count", 0) + 1)
            return Status.FAILURE
        
        # Check if work is completed
        if work_progress >= 100:
            self.current_state = "idle"
            blackboard.set("work_completed", True)
            blackboard.set("work_progress", 0)
            return Status.SUCCESS
        
        return Status.RUNNING
    
    async def error_state(self, blackboard):
        """Error state"""
        print(f"State machine {self.name}: error state")
        await asyncio.sleep(0.02)
        
        # Attempt recovery
        if random.random() < 0.8:  # 80% recovery success
            self.current_state = "recovery"
            return Status.SUCCESS
        else:
            self.current_state = "idle"
            return Status.FAILURE
    
    async def recovery_state(self, blackboard):
        """Recovery state"""
        print(f"State machine {self.name}: recovery state")
        await asyncio.sleep(0.03)
        
        self.current_state = "working"
        return Status.SUCCESS
    
    async def tick(self, blackboard):
        """Execute current state"""
        if self.current_state in self.states:
            return await self.states[self.current_state](blackboard)
        else:
            return Status.FAILURE


class EventDrivenController(BaseNode):
    """Event-driven controller - handles different types of events"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.events = []
        self.event_handlers = {
            "emergency": self.handle_emergency,
            "normal": self.handle_normal,
            "maintenance": self.handle_maintenance
        }
    
    def add_event(self, event_type, priority=1):
        """Add event to queue"""
        self.events.append((event_type, priority))
        self.events.sort(key=lambda x: x[1], reverse=True)  # Sort by priority
    
    async def handle_emergency(self, blackboard):
        """Handle emergency event"""
        print(f"Event controller {self.name}: handling emergency")
        await asyncio.sleep(0.02)
        return Status.SUCCESS
    
    async def handle_normal(self, blackboard):
        """Handle normal event"""
        print(f"Event controller {self.name}: handling normal event")
        await asyncio.sleep(0.01)
        return Status.SUCCESS
    
    async def handle_maintenance(self, blackboard):
        """Handle maintenance event"""
        print(f"Event controller {self.name}: handling maintenance")
        await asyncio.sleep(0.03)
        return Status.SUCCESS
    
    async def tick(self, blackboard):
        """Process events"""
        if not self.events:
            return Status.RUNNING
        
        event_type, priority = self.events.pop(0)
        if event_type in self.event_handlers:
            return await self.event_handlers[event_type](blackboard)
        else:
            return Status.FAILURE


class PriorityQueue(BaseNode):
    """Priority queue - manages tasks with priorities"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.tasks = []
    
    def add_task(self, task, priority=1):
        """Add task to queue"""
        self.tasks.append((task, priority))
        self.tasks.sort(key=lambda x: x[1], reverse=True)  # Sort by priority
    
    async def tick(self, blackboard):
        """Process highest priority task"""
        if not self.tasks:
            return Status.RUNNING
        
        task, priority = self.tasks.pop(0)
        print(f"Priority queue {self.name}: processing task '{task}' (priority={priority})")
        await asyncio.sleep(0.02)
        return Status.SUCCESS


class DynamicDecisionMaker(BaseNode):
    """Dynamic decision maker - adapts decisions based on context"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.decision_history = []
        self.context_factors = ["battery_level", "workload", "time_of_day"]
    
    async def tick(self, blackboard):
        """Make dynamic decision"""
        print(f"Dynamic decision maker {self.name}: analyzing context")
        
        # Analyze context factors
        battery_level = blackboard.get("battery_level", 50)
        workload = blackboard.get("workload", 0)
        time_of_day = blackboard.get("time_of_day", 12)
        
        # Make decision based on context
        if battery_level < 20:
            decision = "charge"
        elif workload > 80:
            decision = "optimize"
        elif time_of_day < 6 or time_of_day > 22:
            decision = "maintenance"
        else:
            decision = "normal"
        
        print(f"Dynamic decision maker {self.name}: decided '{decision}'")
        self.decision_history.append(decision)
        
        # Set decision in blackboard
        blackboard.set("current_decision", decision)
        
        await asyncio.sleep(0.01)
        return Status.SUCCESS


class ChargeAction(Action):
    """Charge action"""
    
    async def execute(self, blackboard):
        print("Executing charge action...")
        await asyncio.sleep(0.05)
        
        current_battery = blackboard.get("battery_level", 0)
        new_battery = min(100, current_battery + 30)
        blackboard.set("battery_level", new_battery)
        
        print(f"Battery charged to {new_battery}%")
        return Status.SUCCESS


class OptimizeAction(Action):
    """Optimize action"""
    
    async def execute(self, blackboard):
        print("Executing optimize action...")
        await asyncio.sleep(0.04)
        
        current_workload = blackboard.get("work_load", 100)
        optimized_workload = max(0, current_workload - 20)
        blackboard.set("work_load", optimized_workload)
        
        print(f"Workload optimized to {optimized_workload}%")
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