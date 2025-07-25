#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 10: Advanced Control Flow – Complex Control Flow Patterns

Demonstrates more advanced control flow patterns, including state machines, event-driven execution, and priority queues.
These patterns are highly useful in real-world applications.

Key Learning Points:

    State machine patterns

    Event-driven control flow

    Priority queues

    Dynamic decision-making

    Complex branching logic

    How to configure advanced control flows using XML strings
"""

import asyncio
import random
import time
from abtree import BehaviorTree, Sequence, Selector, Action, Condition, register_node
from abtree.core import Status
from abtree.nodes.base import BaseNode
from abtree.parser.xml_parser import XMLParser


# Register custom node types
def register_custom_nodes():
    """Register custom node types"""
    register_node("ChargeAction", ChargeAction)
    register_node("OptimizeAction", OptimizeAction)
    register_node("MaintenanceAction", MaintenanceAction)
    register_node("StateMachine", StateMachine)
    register_node("EventDrivenController", EventDrivenController)
    register_node("PriorityQueue", PriorityQueue)
    register_node("DynamicDecisionMaker", DynamicDecisionMaker)


class StateMachine(BaseNode):
    """State machine - manage complex state transitions"""
    
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
        print(f"State machine {self.name}: Idle state")
        await asyncio.sleep(0.01)  # Fast simulation
        
        # Check if there is work to do
        if blackboard.get("has_work", False):
            self.current_state = "working"
            return Status.SUCCESS
        else:
            return Status.RUNNING
    
    async def working_state(self, blackboard):
        """Working state"""
        print(f"State machine {self.name}: Working state")
        await asyncio.sleep(0.01)  # Fast simulation
        
        # Simulate work process
        work_progress = blackboard.get("work_progress", 0)
        work_progress += random.randint(10, 30)
        blackboard.set("work_progress", work_progress)
        
        # Check if error occurs
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
        print(f"State machine {self.name}: Error state")
        await asyncio.sleep(0.01)  # Fast simulation
        
        # Attempt recovery
        if random.random() < 0.8:  # 80% recovery success
            self.current_state = "recovery"
            return Status.SUCCESS
        else:
            self.current_state = "idle"
            return Status.FAILURE
    
    async def recovery_state(self, blackboard):
        """Recovery state"""
        print(f"State machine {self.name}: Recovery state")
        await asyncio.sleep(0.01)  # Fast simulation
        
        self.current_state = "working"
        return Status.SUCCESS
    
    async def tick(self):
        """Execute current state"""
        if not self.blackboard:
            return Status.FAILURE
            
        if self.current_state in self.states:
            return await self.states[self.current_state](self.blackboard)
        return Status.FAILURE


class EventDrivenController(BaseNode):
    """Event-driven controller"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.event_queue = []
        self.event_handlers = {
            "emergency": self.handle_emergency,
            "normal": self.handle_normal,
            "maintenance": self.handle_maintenance
        }
    
    def add_event(self, event_type, priority=1):
        """Add event to queue"""
        self.event_queue.append((priority, time.time(), event_type))
        self.event_queue.sort(key=lambda x: (-x[0], x[1]))  # Sort by priority and time
    
    async def handle_emergency(self, blackboard):
        """Handle emergency event"""
        print(f"Event controller {self.name}: Handle emergency event")
        await asyncio.sleep(0.01)  # Fast simulation
        
        # Set emergency state
        blackboard.set("emergency_mode", True)
        blackboard.set("last_emergency", time.time())
        
        return Status.SUCCESS
    
    async def handle_normal(self, blackboard):
        """Handle normal event"""
        print(f"Event controller {self.name}: Handle normal event")
        await asyncio.sleep(0.01)  # Fast simulation
        
        # Update normal state
        blackboard.set("normal_events_processed", blackboard.get("normal_events_processed", 0) + 1)
        
        return Status.SUCCESS
    
    async def handle_maintenance(self, blackboard):
        """Handle maintenance event"""
        print(f"Event controller {self.name}: Handle maintenance event")
        await asyncio.sleep(0.01)  # Fast simulation
        
        # Execute maintenance
        blackboard.set("maintenance_done", True)
        blackboard.set("last_maintenance", time.time())
        
        return Status.SUCCESS
    
    async def tick(self):
        """Handle event queue"""
        if not self.blackboard:
            return Status.FAILURE
            
        if not self.event_queue:
            return Status.SUCCESS
        
        # Get highest priority event
        priority, timestamp, event_type = self.event_queue.pop(0)
        
        if event_type in self.event_handlers:
            return await self.event_handlers[event_type](self.blackboard)
        
        return Status.FAILURE


class PriorityQueue(BaseNode):
    """Priority queue"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.tasks = []
        self.current_task = None
    
    def add_task(self, task, priority=1):
        """Add task to queue"""
        self.tasks.append((priority, time.time(), task))
        self.tasks.sort(key=lambda x: (-x[0], x[1]))
    
    async def tick(self):
        """Execute highest priority task"""
        if not self.blackboard:
            return Status.FAILURE
            
        if self.current_task:
            # Continue executing current task
            result = await self.current_task.tick()
            if result != Status.RUNNING:
                self.current_task = None
            return result
        
        if not self.tasks:
            return Status.SUCCESS
        
        # Start executing new task
        priority, timestamp, task = self.tasks.pop(0)
        self.current_task = task
        return await self.current_task.tick()


class DynamicDecisionMaker(BaseNode):
    """Dynamic decision maker"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.decision_history = []
        self.adaptation_factor = 1.0
    
    async def tick(self):
        """Make dynamic decision based on current state"""
        print(f"Dynamic decision maker {self.name}: Analyze current state")
        
        # Get current state information
        battery_level = self.blackboard.get("battery_level", 100)
        workload = self.blackboard.get("workload", 0)
        error_rate = self.blackboard.get("error_rate", 0)
        
        # Calculate decision weights
        battery_weight = max(0, (100 - battery_level) / 100)
        workload_weight = workload / 100
        error_weight = error_rate / 100
        
        # Dynamic adjustment of adaptation factor
        if error_rate > 0.5:
            self.adaptation_factor *= 0.9  # Decrease adaptation factor
        elif error_rate < 0.1:
            self.adaptation_factor *= 1.1  # Increase adaptation factor
        
        self.adaptation_factor = max(0.1, min(2.0, self.adaptation_factor))
        
        # Make decision based on weights
        if battery_weight > 0.7:
            decision = "charge"
        elif workload_weight > 0.8:
            decision = "optimize"
        elif error_weight > 0.6:
            decision = "maintenance"
        else:
            decision = "normal"
        
        # Record decision history
        self.decision_history.append({
            "timestamp": time.time(),
            "decision": decision,
            "factors": {
                "battery": battery_level,
                "workload": workload,
                "error_rate": error_rate
            }
        })
        
        # Limit history length
        if len(self.decision_history) > 10:
            self.decision_history.pop(0)
        
        # Set decision result
        self.blackboard.set("current_decision", decision)
        self.blackboard.set("adaptation_factor", self.adaptation_factor)
        
        print(f"Dynamic decision maker {self.name}: Decision: {decision}, Adaptation factor: {self.adaptation_factor:.2f}")
        
        return Status.SUCCESS


# Test action nodes
class ChargeAction(Action):
    """Charge action"""
    
    async def execute(self, blackboard):
        print("Executing charge action...")
        await asyncio.sleep(0.01)  # Fast simulation
        
        current_battery = blackboard.get("battery_level", 0)
        new_battery = min(100, current_battery + 30)
        blackboard.set("battery_level", new_battery)
        
        print(f"Charge completed, battery level: {new_battery}%")
        return Status.SUCCESS


class OptimizeAction(Action):
    """Optimize action"""
    
    async def execute(self, blackboard):
        print("Executing optimize action...")
        await asyncio.sleep(0.01)  # Fast simulation
        
        current_workload = blackboard.get("workload", 0)
        new_workload = max(0, current_workload - 20)
        blackboard.set("workload", new_workload)
        
        print(f"Optimize completed, workload: {new_workload}%")
        return Status.SUCCESS


class MaintenanceAction(Action):
    """Maintenance action"""
    
    async def execute(self, blackboard):
        print("Executing maintenance action...")
        await asyncio.sleep(0.01)  # Fast simulation
        
        current_error_rate = blackboard.get("error_rate", 0)
        new_error_rate = max(0, current_error_rate - 0.3)
        blackboard.set("error_rate", new_error_rate)
        
        print(f"Maintenance completed, error rate: {new_error_rate:.2f}")
        return Status.SUCCESS


async def main():
    """Main function - demonstrate advanced control flow"""
    
    # Register custom node types
    register_custom_nodes()
    
    print("=== ABTree Advanced Control Flow Example ===\n")
    
    # 1. Create state machine
    state_machine = StateMachine("State Machine")
    
    # 2. Create event-driven controller
    event_controller = EventDrivenController("Event Controller")
    
    # 3. Create priority queue
    priority_queue = PriorityQueue("Task Queue")
    
    # 4. Create dynamic decision maker
    decision_maker = DynamicDecisionMaker("Decision Maker")
    
    # 5. Create behavior tree
    root = Selector("Advanced Control Flow")
    
    # State machine branch
    state_branch = Sequence("State Machine Branch")
    state_branch.add_child(state_machine)
    
    # Event handling branch
    event_branch = Sequence("Event Handling Branch")
    event_branch.add_child(event_controller)
    
    # Priority task branch
    priority_branch = Sequence("Priority Task Branch")
    priority_branch.add_child(priority_queue)
    
    # Dynamic decision branch
    decision_branch = Sequence("Dynamic Decision Branch")
    decision_branch.add_child(decision_maker)
    
    # 6. Assemble behavior tree
    root.add_child(state_branch)
    root.add_child(event_branch)
    root.add_child(priority_branch)
    root.add_child(decision_branch)
    
    # 3. Create behavior tree
    tree = BehaviorTree()
    tree.load_from_node(root)
    blackboard = tree.blackboard
    
    # 8. Initialize data
    blackboard.set("battery_level", 60)
    blackboard.set("workload", 80)
    blackboard.set("error_rate", 0.3)
    blackboard.set("has_work", True)
    blackboard.set("work_progress", 0)
    
    # 9. Add some events and tasks
    event_controller.add_event("normal", 1)
    event_controller.add_event("maintenance", 2)
    
    priority_queue.add_task(ChargeAction("Charge Task"), 3)
    priority_queue.add_task(OptimizeAction("Optimize Task"), 2)
    priority_queue.add_task(MaintenanceAction("Maintenance Task"), 1)
    
    print("Start executing advanced control flow...")
    print("=" * 50)
    
    # 10. Execute multiple tests
    for i in range(5):
        print(f"\n--- Test {i+1} ---")
        result = await tree.tick()
        print(f"Execution result: {result}")
        
        # Update state
        blackboard.set("battery_level", max(0, blackboard.get("battery_level", 100) - 10))
        blackboard.set("workload", min(100, blackboard.get("workload", 0) + 5))
        blackboard.set("error_rate", min(1.0, blackboard.get("error_rate", 0) + 0.1))
        
        # Add new events
        if i % 2 == 0:
            event_controller.add_event("normal", 1)
        if i % 3 == 0:
            event_controller.add_event("emergency", 3)
    
    print("\n=== Final State ===")
    print(f"Battery level: {blackboard.get('battery_level')}%")
    print(f"Workload: {blackboard.get('workload')}%")
    print(f"Error rate: {blackboard.get('error_rate'):.2f}")
    print(f"Current decision: {blackboard.get('current_decision')}")
    print(f"Adaptation factor: {blackboard.get('adaptation_factor', 1.0):.2f}")  



if __name__ == "__main__":
    asyncio.run(main()) 