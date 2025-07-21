#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 15: Event System - XML Configuration Version

This is the XML configuration version of the Event System example.
It demonstrates how to configure event-driven behavior trees using XML.

Key Learning Points:
    - How to define event systems using XML
    - How to configure event handling workflows
    - How to implement event prioritization with XML
    - Understanding event filtering in XML
"""

import asyncio
import random
import time
from abtree import (
    BehaviorTree, Sequence, Selector, Action, Condition, Status,
    register_node, Blackboard
)


class EventSystem:
    """Event System - Manage event publishing and subscription"""
    
    def __init__(self, name):
        self.name = name
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
                        print(f"Event {event_type} processed successfully")
                        return Status.SUCCESS
                except Exception as e:
                    print(f"Event processing error: {e}")
        
        return Status.FAILURE
    
    async def tick(self, blackboard):
        """Execute event system"""
        return await self.process_events(blackboard)


class EmergencyEventHandler:
    """Emergency event handler"""
    
    async def handle(self, event, blackboard):
        print(f"🚨 Processing emergency event: {event['data']}")
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
        print(f"📡 Processing sensor data: {sensor_data}")
        blackboard.set("sensor_data", sensor_data)
        blackboard.set("last_sensor_update", time.time())
        await asyncio.sleep(0.01)  # Fast simulation
        return Status.SUCCESS


class UserInputEventHandler:
    """User input event handler"""
    
    async def handle(self, event, blackboard):
        user_input = event['data']
        print(f"👤 Processing user input: {user_input}")
        blackboard.set("user_command", user_input)
        blackboard.set("user_input_time", time.time())
        await asyncio.sleep(0.01)  # Fast simulation
        return Status.SUCCESS


class SystemStatusEventHandler:
    """System status event handler"""
    
    async def handle(self, event, blackboard):
        status_data = event['data']
        print(f"⚙️ Processing system status: {status_data}")
        blackboard.set("system_status", status_data)
        blackboard.set("status_update_time", time.time())
        await asyncio.sleep(0.01)  # Fast simulation
        return Status.SUCCESS


class EventDrivenAction(Action):
    """Event-driven action node"""
    
    def __init__(self, name, required_event_type, event_system=None, **kwargs):
        self.name = name
        self.required_event_type = required_event_type
        self.event_system = event_system
    
    async def execute(self, blackboard):
        if self.event_system is None:
            self.event_system = blackboard.get("event_system")
        
        if self.event_system is None:
            print(f"Error: Event system not found")
            return Status.FAILURE
        
        # Check if there are events of the specified type
        for event in self.event_system.event_queue:
            if event['type'] == self.required_event_type:
                print(f"Executing event-driven action: {self.name} (event type: {self.required_event_type})")
                return Status.SUCCESS
        
        print(f"Waiting for event: {self.required_event_type}")
        return Status.RUNNING


class EventCondition(Condition):
    """Event condition node"""
    
    def __init__(self, name, event_type, timeout=5.0, event_system=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.event_type = event_type
        self.timeout = timeout
        self.event_system = event_system
        self.start_time = None
    
    async def evaluate(self, blackboard):
        if self.event_system is None:
            self.event_system = blackboard.get("event_system")
        
        if self.event_system is None:
            return False
        
        if self.start_time is None:
            self.start_time = time.time()
        
        # Check timeout
        if time.time() - self.start_time > self.timeout:
            print(f"Event condition timed out: {self.name}")
            return False
        
        # Check if there are events of the specified type
        for event in self.event_system.event_history:
            if event['type'] == self.event_type:
                time_since_event = time.time() - event['timestamp']
                if time_since_event < self.timeout:
                    print(f"Event condition met: {self.name} (event type: {self.event_type})")
                    return True
        
        return False


class EmergencyResponseAction(Action):
    """Emergency response action node"""
    
    async def execute(self, blackboard):
        print("🚨 Executing emergency response...")
        
        # Simulate emergency response process
        response_steps = [
            "Stop all non-critical operations",
            "Activate safety protocols",
            "Send emergency notification",
            "Start backup system"
        ]
        
        for step in response_steps:
            print(f"  - {step}")
            await asyncio.sleep(0.01)  # Fast simulation
        
        blackboard.set("emergency_response_complete", True)
        blackboard.set("emergency_response_time", time.time())
        
        print("Emergency response complete")
        return Status.SUCCESS


class SensorDataProcessingAction(Action):
    """Sensor data processing action node"""
    
    async def execute(self, blackboard):
        print("📡 Processing sensor data...")
        
        sensor_data = blackboard.get("sensor_data", {})
        if sensor_data:
            print(f"   Sensor data: {sensor_data}")
            
            # Simulate data processing
            processed_data = {
                'temperature': sensor_data.get('temperature', 0) + random.uniform(-1, 1),
                'humidity': sensor_data.get('humidity', 0) + random.uniform(-2, 2),
                'pressure': sensor_data.get('pressure', 0) + random.uniform(-0.5, 0.5)
            }
            
            blackboard.set("processed_sensor_data", processed_data)
            print(f"   Processed data: {processed_data}")
        else:
            print("   No sensor data")
        
        await asyncio.sleep(0.01)  # Fast simulation
        return Status.SUCCESS


class UserCommandAction(Action):
    """User command processing action node"""
    
    async def execute(self, blackboard):
        print("👤 Processing user command...")
        
        user_command = blackboard.get("user_command", "")
        if user_command:
            print(f"   User command: {user_command}")
            
            # Simulate command processing
            if "start" in user_command.lower():
                blackboard.set("system_started", True)
                print("   System started")
            elif "stop" in user_command.lower():
                blackboard.set("system_stopped", True)
                print("   System stopped")
            elif "status" in user_command.lower():
                blackboard.set("status_requested", True)
                print("   Status information requested")
            else:
                print("   Unknown command")
        else:
            print("   No user command")
        
        await asyncio.sleep(0.01)  # Fast simulation
        return Status.SUCCESS


def register_custom_nodes():
    """Register custom node types"""
    # Note: EventSystem is not a node, it's a system component
    # register_node("EventSystem", EventSystem)  # Removed - not a node
    register_node("EventDrivenAction", EventDrivenAction)
    register_node("EventCondition", EventCondition)
    register_node("EmergencyResponseAction", EmergencyResponseAction)
    register_node("SensorDataProcessingAction", SensorDataProcessingAction)
    register_node("UserCommandAction", UserCommandAction)


async def main():
    """Main function - Demonstrate XML-based event system configuration"""
    
    print("=== ABTree Event System XML Configuration Example ===\n")
    
    # Register custom node types
    register_custom_nodes()
    
    # Create event system
    event_system = EventSystem("MainEventSystem")
    
    # Register event handlers
    event_system.subscribe("emergency", EmergencyEventHandler().handle, priority=10)
    event_system.subscribe("sensor_data", SensorEventHandler().handle, priority=5)
    event_system.subscribe("user_input", UserInputEventHandler().handle, priority=3)
    event_system.subscribe("system_status", SystemStatusEventHandler().handle, priority=2)
    
    # Create blackboard
    blackboard = Blackboard()
    blackboard.set("event_system", event_system)
    blackboard.set("emergency_active", False)
    blackboard.set("system_started", False)
    blackboard.set("system_stopped", False)
    
    # Create behavior tree
    tree = BehaviorTree()
    
    # Define XML configuration string
    xml_config = '''
    <BehaviorTree name="EventSystemXML" description="Event-driven behavior tree with XML configuration">
        <Selector name="Event System Root">
            <!-- Emergency event handling (highest priority) -->
            <Sequence name="Emergency Handling">
                <EventCondition name="Check Emergency Event" event_type="emergency" timeout="10.0" />
                <EventDrivenAction name="Process Emergency" required_event_type="emergency" />
                <EmergencyResponseAction name="Emergency Response" />
            </Sequence>
            
            <!-- Sensor data processing -->
            <Sequence name="Sensor Data Processing">
                <EventCondition name="Check Sensor Data" event_type="sensor_data" timeout="5.0" />
                <EventDrivenAction name="Process Sensor Data" required_event_type="sensor_data" />
                <SensorDataProcessingAction name="Process Sensor Data" />
            </Sequence>
            
            <!-- User command processing -->
            <Sequence name="User Command Processing">
                <EventCondition name="Check User Input" event_type="user_input" timeout="3.0" />
                <EventDrivenAction name="Process User Command" required_event_type="user_input" />
                <UserCommandAction name="Execute User Command" />
            </Sequence>
            
            <!-- System status monitoring -->
            <Sequence name="System Status Monitoring">
                <EventCondition name="Check System Status" event_type="system_status" timeout="2.0" />
                <EventDrivenAction name="Process System Status" required_event_type="system_status" />
            </Sequence>
        </Selector>
    </BehaviorTree>
    '''
    
    # Load XML configuration
    tree.load_from_string(xml_config)
    
    print("Event system behavior tree configured:")
    print("  - Emergency handling: Highest priority")
    print("  - Sensor data processing: Medium priority")
    print("  - User command processing: Low priority")
    print("  - System status monitoring: Lowest priority")
    
    # Execute behavior tree
    print("\n=== Starting event system execution ===")
    
    for i in range(15):
        print(f"\n--- Execution round {i+1} ---")
        
        # Simulate publishing events
        if i == 2:  # Round 3: Publish emergency event
            event_system.publish("emergency", "System failure", priority=10)
        elif i == 5:  # Round 6: Publish sensor data
            event_system.publish("sensor_data", {"temperature": 25.5, "humidity": 60}, priority=5)
        elif i == 8:  # Round 9: Publish user input
            event_system.publish("user_input", "start system", priority=3)
        elif i == 11:  # Round 12: Publish system status
            event_system.publish("system_status", {"cpu": 45, "memory": 70}, priority=2)
        
        # Execute behavior tree
        result = await tree.tick()
        print(f"Execution result: {result}")
        
        # Display current status
        emergency_active = blackboard.get("emergency_active", False)
        system_started = blackboard.get("system_started", False)
        print(f"Emergency status: {emergency_active}, System started: {system_started}")
        
        await asyncio.sleep(0.01)  # Fast simulation
    
    print("\nEvent system execution complete!")


if __name__ == "__main__":
    asyncio.run(main()) 