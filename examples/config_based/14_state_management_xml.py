#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 14: State Management - XML Configuration Version

This is the XML configuration version of the State Management example.
It demonstrates how to configure state management using XML.

Key Learning Points:
    - How to define state management using XML
    - How to configure state transitions
    - How to implement state persistence with XML
    - Understanding state synchronization in XML
"""

import asyncio
import json
import time
import random
from pathlib import Path
from abtree import (
    BehaviorTree, Sequence, Selector, Action, Condition, Status,
    Blackboard, register_node,
)


class StateManager:
    """State Manager - Manage complex state transitions and persistence"""
    
    def __init__(self, name, initial_state="idle"):
        self.name = name
        self.current_state = initial_state
        self.previous_state = None
        self.state_history = []
        self.state_transitions = {
            "idle": ["working", "maintenance", "error"],
            "working": ["idle", "maintenance", "error", "paused"],
            "maintenance": ["idle", "working"],
            "error": ["idle", "maintenance"],
            "paused": ["working", "idle"]
        }
        self.state_data = {}
        self.last_state_change = time.time()
    
    def can_transition_to(self, target_state):
        """Check if can transition to target state"""
        if self.current_state in self.state_transitions:
            return target_state in self.state_transitions[self.current_state]
        return False
    
    def transition_to(self, new_state, data=None):
        """Transition to new state"""
        if self.can_transition_to(new_state):
            self.previous_state = self.current_state
            self.current_state = new_state
            self.last_state_change = time.time()
            
            # Record state history
            self.state_history.append({
                'from_state': self.previous_state,
                'to_state': new_state,
                'timestamp': time.time(),
                'data': data
            })
            
            # Limit history length
            if len(self.state_history) > 50:
                self.state_history.pop(0)
            
            print(f"State Manager {self.name}: {self.previous_state} -> {new_state}")
            return True
        else:
            print(f"State Manager {self.name}: Cannot transition from {self.current_state} to {new_state}")
            return False
    
    def get_state_duration(self):
        """Get current state duration"""
        return time.time() - self.last_state_change
    
    def get_state_info(self):
        """Get state information"""
        return {
            'current_state': self.current_state,
            'previous_state': self.previous_state,
            'state_duration': self.get_state_duration(),
            'state_history': self.state_history[-5:] if self.state_history else []
        }
    
    def save_state(self, filepath):
        """Save state to file"""
        state_data = {
            'name': self.name,
            'current_state': self.current_state,
            'state_data': self.state_data,
            'state_history': self.state_history,
            'timestamp': time.time()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)
        
        print(f"State saved to: {filepath}")
    
    def load_state(self, filepath):
        """Load state from file"""
        if Path(filepath).exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            self.current_state = state_data.get('current_state', 'idle')
            self.state_data = state_data.get('state_data', {})
            self.state_history = state_data.get('state_history', [])
            
            print(f"State loaded from file: {filepath}")
            return True
        return False


class StateTransitionAction(Action):
    """State transition action node"""
    
    def __init__(self, name, target_state, state_manager=None, condition_func=None, **kwargs):
        self.name = name
        self.target_state = target_state
        self.state_manager = state_manager
        self.condition_func = condition_func
    
    async def execute(self, blackboard):
        if self.state_manager is None:
            state_manager_name = blackboard.get("state_manager_name", "default")
            self.state_manager = blackboard.get("state_managers", {}).get(state_manager_name)
        
        if self.state_manager is None:
            print(f"Error: State manager not found")
            return Status.FAILURE
        
        # Check transition conditions
        if self.condition_func and not self.condition_func(blackboard):
            print(f"State transition conditions not met: {self.name}")
            return Status.FAILURE
        
        # Execute state transition
        success = self.state_manager.transition_to(self.target_state)
        
        if success:
            # Update blackboard data
            blackboard.set("current_state", self.state_manager.current_state)
            blackboard.set("state_transition_time", time.time())
            print(f"State transition successful: {self.name} -> {self.target_state}")
            return Status.SUCCESS
        else:
            print(f"State transition failed: {self.name}")
            return Status.FAILURE


class StateCondition(Condition):
    """State condition node"""
    
    def __init__(self, name, expected_state, state_manager=None, duration_check=None, **kwargs):
        self.name = name
        self.expected_state = expected_state
        self.state_manager = state_manager
        self.duration_check = duration_check
    
    async def evaluate(self, blackboard):
        if self.state_manager is None:
            state_manager_name = blackboard.get("state_manager_name", "default")
            self.state_manager = blackboard.get("state_managers", {}).get(state_manager_name)
        
        if self.state_manager is None:
            return False
        
        current_state = self.state_manager.current_state
        state_match = current_state == self.expected_state
        
        # Check duration
        if self.duration_check and state_match:
            duration = self.state_manager.get_state_duration()
            if duration < self.duration_check:
                return False
        
        print(f"State check {self.name}: current={current_state}, expected={self.expected_state}, match={state_match}")
        return state_match


class StateMonitoringAction(Action):
    """State monitoring action node"""
    
    def __init__(self, name, state_manager=None, **kwargs):
        self.name = name
        self.state_manager = state_manager
    
    async def execute(self, blackboard):
        if self.state_manager is None:
            state_manager_name = blackboard.get("state_manager_name", "default")
            self.state_manager = blackboard.get("state_managers", {}).get(state_manager_name)
        
        if self.state_manager is None:
            return Status.FAILURE
        
        # Get state information
        state_info = self.state_manager.get_state_info()
        
        # Update blackboard data
        blackboard.set("state_info", state_info)
        blackboard.set("state_duration", state_info['state_duration'])
        blackboard.set("state_history", state_info['state_history'])
        
        print(f"State monitoring {self.name}:")
        print(f"  Current state: {state_info['current_state']}")
        print(f"  Duration: {state_info['state_duration']:.2f} seconds")
        print(f"  History records: {len(state_info['state_history'])} entries")
        
        return Status.SUCCESS


class StateRecoveryAction(Action):
    """State recovery action node"""
    
    def __init__(self, name, recovery_state="idle", state_manager=None, **kwargs):
        self.name = name
        self.recovery_state = recovery_state
        self.state_manager = state_manager
    
    async def execute(self, blackboard):
        if self.state_manager is None:
            state_manager_name = blackboard.get("state_manager_name", "default")
            self.state_manager = blackboard.get("state_managers", {}).get(state_manager_name)
        
        if self.state_manager is None:
            return Status.FAILURE
        
        current_state = self.state_manager.current_state
        
        # Check if recovery is needed
        if current_state in ["error", "paused"]:
            print(f"Executing state recovery: {current_state} -> {self.recovery_state}")
            success = self.state_manager.transition_to(self.recovery_state)
            
            if success:
                blackboard.set("recovery_performed", True)
                blackboard.set("recovery_time", time.time())
                return Status.SUCCESS
            else:
                return Status.FAILURE
        else:
            print(f"No state recovery needed: current state {current_state}")
            return Status.SUCCESS


class StatePersistenceAction(Action):
    """State persistence action node"""
    
    def __init__(self, name, filepath, state_manager=None, **kwargs):
        self.name = name
        self.filepath = filepath
        self.state_manager = state_manager
    
    async def execute(self, blackboard):
        if self.state_manager is None:
            state_manager_name = blackboard.get("state_manager_name", "default")
            self.state_manager = blackboard.get("state_managers", {}).get(state_manager_name)
        
        if self.state_manager is None:
            return Status.FAILURE
        
        try:
            self.state_manager.save_state(self.filepath)
            blackboard.set("state_saved", True)
            blackboard.set("state_file", self.filepath)
            return Status.SUCCESS
        except Exception as e:
            print(f"State save failed: {e}")
            return Status.FAILURE


class StateLoadAction(Action):
    """State load action node"""
    
    def __init__(self, name, filepath, state_manager=None, **kwargs):
        self.name = name
        self.filepath = filepath
        self.state_manager = state_manager
    
    async def execute(self, blackboard):
        if self.state_manager is None:
            state_manager_name = blackboard.get("state_manager_name", "default")
            self.state_manager = blackboard.get("state_managers", {}).get(state_manager_name)
        
        if self.state_manager is None:
            return Status.FAILURE
        
        try:
            success = self.state_manager.load_state(self.filepath)
            if success:
                blackboard.set("state_loaded", True)
                blackboard.set("state_file", self.filepath)
                return Status.SUCCESS
            else:
                return Status.FAILURE
        except Exception as e:
            print(f"State load failed: {e}")
            return Status.FAILURE


class ErrorDetectionCondition(Condition):
    """Error detection condition node"""
    
    def __init__(self, name, error_threshold=3, **kwargs):
        self.name = name
        self.error_threshold = error_threshold
    
    async def evaluate(self, blackboard):
        error_count = blackboard.get("error_count", 0)
        has_error = error_count >= self.error_threshold
        
        print(f"Error detection {self.name}: error_count={error_count}, threshold={self.error_threshold}, has_error={has_error}")
        return has_error


class MaintenanceRequiredCondition(Condition):
    """Maintenance required condition node"""
    
    def __init__(self, name, maintenance_interval=300, **kwargs):  # 5 minutes
        self.name = name
        self.maintenance_interval = maintenance_interval
    
    async def evaluate(self, blackboard):
        last_maintenance = blackboard.get("last_maintenance_time", 0)
        current_time = time.time()
        time_since_maintenance = current_time - last_maintenance
        
        needs_maintenance = time_since_maintenance >= self.maintenance_interval
        
        print(f"Maintenance check {self.name}: time_since_maintenance={time_since_maintenance:.1f} seconds, needs_maintenance={needs_maintenance}")
        return needs_maintenance


class WorkingStateAction(Action):
    """Working state action node"""
    
    async def execute(self, blackboard):
        print("Executing working state operation...")
        
        # Simulate work process
        work_duration = random.uniform(0.5, 2.0)
        await asyncio.sleep(0.01)  # Fast simulation
        
        # Update work statistics
        work_count = blackboard.get("work_count", 0) + 1
        blackboard.set("work_count", work_count)
        blackboard.set("last_work_time", time.time())
        
        print(f"Work completed: {work_count}th work, duration {work_duration:.2f} seconds")
        return Status.SUCCESS


class MaintenanceAction(Action):
    """Maintenance action node"""
    
    async def execute(self, blackboard):
        print("Executing system maintenance...")
        
        # Simulate maintenance process
        maintenance_duration = random.uniform(1.0, 3.0)
        await asyncio.sleep(0.01)  # Fast simulation
        
        # Update maintenance statistics
        blackboard.set("last_maintenance_time", time.time())
        blackboard.set("maintenance_count", blackboard.get("maintenance_count", 0) + 1)
        
        print(f"Maintenance completed: duration {maintenance_duration:.2f} seconds")
        return Status.SUCCESS


def register_custom_nodes():
    """Register custom node types"""
    register_node("StateTransitionAction", StateTransitionAction)
    register_node("StateCondition", StateCondition)
    register_node("StateMonitoringAction", StateMonitoringAction)
    register_node("StateRecoveryAction", StateRecoveryAction)
    register_node("StatePersistenceAction", StatePersistenceAction)
    register_node("StateLoadAction", StateLoadAction)
    register_node("ErrorDetectionCondition", ErrorDetectionCondition)
    register_node("MaintenanceRequiredCondition", MaintenanceRequiredCondition)
    register_node("WorkingStateAction", WorkingStateAction)
    register_node("MaintenanceAction", MaintenanceAction)


async def main():
    """Main function - Demonstrate XML-based state management configuration"""
    
    print("=== ABTree State Management XML Configuration Example ===\n")
    
    # Register custom node types
    register_custom_nodes()
    
    # Create state manager
    state_manager = StateManager("SystemStateManager", "idle")
    
    # Create blackboard
    blackboard = Blackboard()
    blackboard.set("state_managers", {"default": state_manager})
    blackboard.set("state_manager_name", "default")
    blackboard.set("error_count", 0)
    blackboard.set("work_count", 0)
    blackboard.set("maintenance_count", 0)
    
    # Create behavior tree
    tree = BehaviorTree()
    
    # Define XML configuration string
    xml_config = '''
    <BehaviorTree name="StateManagementXML" description="State management with XML configuration">
        <Selector name="State Management Root">
            <!-- Error handling (highest priority) -->
            <Sequence name="Error Handling">
                <ErrorDetectionCondition name="Check Errors" error_threshold="3" />
                <StateTransitionAction name="Transition to Error" target_state="error" />
                <StateRecoveryAction name="Recover from Error" recovery_state="idle" />
            </Sequence>
            
            <!-- Maintenance handling -->
            <Sequence name="Maintenance Handling">
                <MaintenanceRequiredCondition name="Check Maintenance" maintenance_interval="300" />
                <StateTransitionAction name="Transition to Maintenance" target_state="maintenance" />
                <MaintenanceAction name="Perform Maintenance" />
                <StateTransitionAction name="Return to Idle" target_state="idle" />
            </Sequence>
            
            <!-- Normal operation -->
            <Sequence name="Normal Operation">
                <StateCondition name="Check Idle State" expected_state="idle" />
                <StateTransitionAction name="Start Working" target_state="working" />
                <WorkingStateAction name="Perform Work" />
                <StateTransitionAction name="Return to Idle" target_state="idle" />
            </Sequence>
            
            <!-- State monitoring -->
            <Sequence name="State Monitoring">
                <StateMonitoringAction name="Monitor State" />
                <StatePersistenceAction name="Save State" filepath="state_backup.json" />
            </Sequence>
        </Selector>
    </BehaviorTree>
    '''
    
    # Load XML configuration
    tree.load_from_string(xml_config)
    
    print("State management behavior tree configured:")
    print("  - Error handling: Detect errors and recover")
    print("  - Maintenance handling: Regular maintenance")
    print("  - Normal operation: Work cycle")
    print("  - State monitoring: Monitor and persist")
    
    # Execute behavior tree
    print("\n=== Starting state management execution ===")
    
    for i in range(10):
        print(f"\n--- Execution round {i+1} ---")
        
        # Simulate some random events
        if random.random() < 0.1:  # 10% probability to trigger error
            blackboard.set("error_count", blackboard.get("error_count", 0) + 1)
            print("⚠️ Error detected!")
        
        # Execute behavior tree
        result = await tree.tick()
        print(f"Execution result: {result}")
        
        # Display current state
        state_info = state_manager.get_state_info()
        print(f"Current state: {state_info['current_state']}")
        
        await asyncio.sleep(0.01)
    
    print("\nState management execution complete!")


if __name__ == "__main__":
    asyncio.run(main()) 