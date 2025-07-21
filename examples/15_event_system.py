#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 15: Event System – Event-Driven Behavior Trees

Demonstrates how to use the event system to drive the execution of behavior trees.
The event system allows behavior trees to respond to external events, enabling more flexible decision logic.

Key Learning Points:

    Event listening mechanisms

    Event handling workflows

    Asynchronous event system

    Event prioritization

    Event filtering

    How to configure the event system using XML strings
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
    register_node("EventSystem", EventSystem)
    register_node("EventDrivenAction", EventDrivenAction)
    register_node("EventCondition", EventCondition)
    register_node("EmergencyResponseAction", EmergencyResponseAction)
    register_node("SensorDataProcessingAction", SensorDataProcessingAction)
    register_node("UserCommandAction", UserCommandAction)


class EventSystem(BaseNode):
    """Event System - Manage event publishing and subscription"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.subscribers = {}
        self.event_queue = []
        self.event_history = []
    
    def subscribe(self, event_type, handler, priority=1):
        """Subscribe to event"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append({
            'handler': handler,
            'priority': priority,
            'timestamp': time.time()
        })
        
        # Sort by priority
        self.subscribers[event_type].sort(key=lambda x: (-x['priority'], x['timestamp']))
    
    def publish(self, event_type, data=None, priority=1):
        """Publish event"""
        event = {
            'type': event_type,
            'data': data,
            'priority': priority,
            'timestamp': time.time()
        }
        
        self.event_queue.append(event)
        self.event_history.append(event)
        
        # Limit history length
        if len(self.event_history) > 100:
            self.event_history.pop(0)
        
        print(f"Event System {self.name}: Published event {event_type} (priority: {priority})")
    
    async def process_events(self, blackboard):
        """Process event queue"""
        if not self.event_queue:
            return Status.SUCCESS
        
        # Sort events by priority
        self.event_queue.sort(key=lambda x: (-x['priority'], x['timestamp']))
        
        # Process highest priority event
        event = self.event_queue.pop(0)
        event_type = event['type']
        
        if event_type in self.subscribers:
            for subscriber in self.subscribers[event_type]:
                try:
                    result = await subscriber['handler'](event, blackboard)
                    if result == Status.SUCCESS:
                        print(f"Event System {self.name}: Event {event_type} processed successfully")
                        return Status.SUCCESS
                except Exception as e:
                    print(f"Event System {self.name}: Event processing error: {e}")
        
        return Status.FAILURE
    
    async def tick(self, blackboard):
        """Execute event system"""
        return await self.process_events(blackboard)


class EmergencyEventHandler:
    """Emergency event handler"""
    
    async def handle(self, event, blackboard):
        print(f"Processing emergency event: {event['data']}")
        await asyncio.sleep(0.01)  # Fast simulation
        
        # Set emergency state
        blackboard.set("emergency_mode", True)
        blackboard.set("last_emergency", event['timestamp'])
        blackboard.set("emergency_count", blackboard.get("emergency_count", 0) + 1)
        
        return Status.SUCCESS


class SensorEventHandler:
    """Sensor event handler"""
    
    async def handle(self, event, blackboard):
        sensor_data = event['data']
        print(f"Processing sensor event: {sensor_data}")
        await asyncio.sleep(0.01)  # Fast simulation
        
        # Update sensor data
        blackboard.set("sensor_data", sensor_data)
        blackboard.set("last_sensor_update", event['timestamp'])
        
        return Status.SUCCESS


class UserInputEventHandler:
    """User input event handler"""
    
    async def handle(self, event, blackboard):
        user_input = event['data']
        print(f"Processing user input: {user_input}")
        await asyncio.sleep(0.01)  # Fast simulation
        
        # Process user input
        blackboard.set("user_input", user_input)
        blackboard.set("last_user_input", event['timestamp'])
        
        return Status.SUCCESS


class SystemStatusEventHandler:
    """System status event handler"""
    
    async def handle(self, event, blackboard):
        status_data = event['data']
        print(f"Processing system status event: {status_data}")
        await asyncio.sleep(0.01)  # Fast simulation
        
        # Update system status
        blackboard.set("system_status", status_data)
        blackboard.set("last_status_update", event['timestamp'])
        
        return Status.SUCCESS


class EventDrivenAction(Action):
    """Event-driven action node"""
    
    def __init__(self, name, required_event_type, event_system=None, **kwargs):
        super().__init__(name, **kwargs)
        self.event_system = event_system
        self.required_event_type = required_event_type
        self.last_event_time = 0
    
    async def execute(self, blackboard):
        print(f"Event-driven action {self.name}: Waiting for event {self.required_event_type}")
        
        # Check for new events
        for event in self.event_system.event_history:
            if (event['type'] == self.required_event_type and 
                event['timestamp'] > self.last_event_time):
                
                self.last_event_time = event['timestamp']
                print(f"Event-driven action {self.name}: Event received, starting execution")
                
                await asyncio.sleep(0.01)  # Fast simulation
                return Status.SUCCESS
        
        print(f"Event-driven action {self.name}: No required event received")
        return Status.RUNNING


class EventCondition(Condition):
    """Event condition node"""
    
    def __init__(self, name, event_type, timeout=2.0, event_system=None, **kwargs):  # Reduced timeout from 5.0
        super().__init__(name, **kwargs)
        self.event_system = event_system
        self.event_type = event_type
        self.timeout = timeout
        self.start_time = None
    
    async def evaluate(self, blackboard):
        if self.start_time is None:
            self.start_time = time.time()
        
        # Check for timeout
        if time.time() - self.start_time > self.timeout:
            print(f"Event condition {self.name}: Wait timeout")
            return False
        
        # If no event system, return False
        if self.event_system is None:
            print(f"Event condition {self.name}: No event system")
            return False
        
        # Check for specified event type
        for event in self.event_system.event_history:
            if (event['type'] == self.event_type and 
                event['timestamp'] > self.start_time):
                print(f"Event condition {self.name}: Detected event {self.event_type}")
                return True
        
        print(f"Event condition {self.name}: Waiting for event {self.event_type}")
        return False


class EmergencyResponseAction(Action):
    """Emergency response action"""
    
    async def execute(self, blackboard):
        print("Executing emergency response...")
        await asyncio.sleep(0.01)  # Fast simulation
        
        # Execute emergency response logic
        blackboard.set("emergency_response_executed", True)
        blackboard.set("response_time", time.time())
        
        print("Emergency response completed")
        return Status.SUCCESS


class SensorDataProcessingAction(Action):
    """Sensor data processing action"""
    
    async def execute(self, blackboard):
        print("Processing sensor data...")
        await asyncio.sleep(0.01)  # Fast simulation
        
        sensor_data = blackboard.get("sensor_data", {})
        if sensor_data:
            # Process sensor data
            processed_data = {
                'temperature': sensor_data.get('temperature', 0) + random.uniform(-1, 1),
                'humidity': sensor_data.get('humidity', 0) + random.uniform(-2, 2),
                'pressure': sensor_data.get('pressure', 0) + random.uniform(-0.5, 0.5)
            }
            
            blackboard.set("processed_sensor_data", processed_data)
            print(f"Sensor data processing completed: {processed_data}")
        
        return Status.SUCCESS


class UserCommandAction(Action):
    """User command processing action"""
    
    async def execute(self, blackboard):
        print("Processing user command...")
        await asyncio.sleep(0.01)  # Fast simulation
        
        user_input = blackboard.get("user_input", "")
        if user_input:
            # Process user command
            blackboard.set("command_processed", True)
            blackboard.set("last_command", user_input)
            print(f"User command processing completed: {user_input}")
        
        return Status.SUCCESS


async def main():
    """Main function - Demonstrate event system"""
    
    # Register custom node types
    register_custom_nodes()
    
    print("=== ABTree Event System Example ===\n")
    
    # 1. Create event system
    event_system = EventSystem("Main Event System")
    
    # 2. Register event handlers
    emergency_handler = EmergencyEventHandler()
    sensor_handler = SensorEventHandler()
    user_input_handler = UserInputEventHandler()
    system_status_handler = SystemStatusEventHandler()
    
    event_system.subscribe("emergency", emergency_handler.handle, priority=3)
    event_system.subscribe("sensor", sensor_handler.handle, priority=1)
    event_system.subscribe("user_input", user_input_handler.handle, priority=2)
    event_system.subscribe("system_status", system_status_handler.handle, priority=1)
    
    # 3. Create behavior tree
    root = Selector("Event-Driven System")
    
    # Emergency response branch
    emergency_branch = Sequence("Emergency Response")
    emergency_condition = EventCondition("Wait for Emergency Event", "emergency")
    emergency_condition.event_system = event_system
    emergency_branch.add_child(emergency_condition)
    emergency_branch.add_child(EmergencyResponseAction("Emergency Response"))
    
    # Sensor processing branch
    sensor_branch = Sequence("Sensor Processing")
    sensor_condition = EventCondition("Wait for Sensor Event", "sensor")
    sensor_condition.event_system = event_system
    sensor_branch.add_child(sensor_condition)
    sensor_branch.add_child(SensorDataProcessingAction("Sensor Data Processing"))
    
    # User command processing branch
    user_branch = Sequence("User Command Processing")
    user_condition = EventCondition("Wait for User Input", "user_input")
    user_condition.event_system = event_system
    user_branch.add_child(user_condition)
    user_branch.add_child(UserCommandAction("User Command Processing"))
    
    # Event processing branch
    event_processing_branch = Sequence("Event Processing")
    event_processing_branch.add_child(event_system)
    
    # 4. Assemble behavior tree
    root.add_child(emergency_branch)
    root.add_child(sensor_branch)
    root.add_child(user_branch)
    root.add_child(event_processing_branch)
    
    # 5. Create behavior tree instance
    tree = BehaviorTree()
    tree.load_from_root(root)
    blackboard = tree.blackboard
    
    # 6. Initialize data
    blackboard.set("emergency_mode", False)
    blackboard.set("emergency_count", 0)
    blackboard.set("command_processed", False)
    
    print("Starting event-driven system execution...")
    print("=" * 50)
    
    # 7. Simulate event publishing and processing
    for i in range(6):  # Reduced from 10 to 6 cycles
        print(f"\n--- Round {i+1} Execution ---")
        
        # Randomly publish events
        event_types = ["sensor", "user_input", "system_status", "emergency"]
        weights = [0.4, 0.3, 0.2, 0.1]  # Event probability weights
        
        event_type = random.choices(event_types, weights=weights)[0]
        
        if event_type == "sensor":
            event_system.publish("sensor", {
                "temperature": random.uniform(20, 30),
                "humidity": random.uniform(40, 60),
                "pressure": random.uniform(1000, 1020)
            })
        elif event_type == "user_input":
            commands = ["start", "stop", "status", "config"]
            event_system.publish("user_input", random.choice(commands))
        elif event_type == "system_status":
            event_system.publish("system_status", {
                "cpu_usage": random.uniform(0, 100),
                "memory_usage": random.uniform(0, 100),
                "disk_usage": random.uniform(0, 100)
            })
        elif event_type == "emergency":
            event_system.publish("emergency", f"Emergency situation {i+1}")
        
        # Execute behavior tree
        result = await tree.tick()
        print(f"Execution result: {result}")
        
        # Display status
        print(f"Emergency mode: {blackboard.get('emergency_mode')}")
        print(f"Emergency event count: {blackboard.get('emergency_count')}")
        print(f"Command processed: {blackboard.get('command_processed')}")
        
        await asyncio.sleep(0.01)  # Fast simulation
    
    print("\n=== Final Status ===")
    print(f"Total events: {len(event_system.event_history)}")
    print(f"Emergency events: {blackboard.get('emergency_count')}")
    print(f"Last command: {blackboard.get('last_command', 'None')}")
    print(f"Processed sensor data: {blackboard.get('processed_sensor_data', {})}")  
 

if __name__ == "__main__":
    asyncio.run(main()) 