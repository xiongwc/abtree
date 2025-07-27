#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 14: State Management – Complex State Handling

Demonstrates how to use ABTree for advanced state management, including transitions, persistence, and synchronization.
State management is a critical part of complex systems.

Key Learning Points:

    State transition logic

    State persistence

    State synchronization

    State recovery

    State monitoring

    How to configure state management using XML strings
"""

import asyncio
import json
import time
import random
from pathlib import Path
from abtree import BehaviorTree, Sequence, Selector, Action, Condition, register_node
from abtree.core import Status
from abtree.nodes.base import BaseNode
from abtree.parser.xml_parser import XMLParser


# Register custom node types
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
    
    def save_state(self, filepath):
        """Save state to file"""
        state_data = {
            'current_state': self.current_state,
            'previous_state': self.previous_state,
            'last_state_change': self.last_state_change,
            'state_data': self.state_data,
            'state_history': self.state_history[-10:]  # Only save recent 10 records
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            print(f"State Manager {self.name}: State saved to {filepath}")
            return True
        except Exception as e:
            print(f"State Manager {self.name}: Failed to save state: {e}")
            return False
    
    def load_state(self, filepath):
        """Load state from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            self.current_state = state_data.get('current_state', 'idle')
            self.previous_state = state_data.get('previous_state', None)
            self.last_state_change = state_data.get('last_state_change', time.time())
            self.state_data = state_data.get('state_data', {})
            self.state_history = state_data.get('state_history', [])
            
            print(f"State Manager {self.name}: State loaded from {filepath}")
            return True
        except Exception as e:
            print(f"State Manager {self.name}: Failed to load state: {e}")
            return False


class StateTransitionAction(Action):
    """State transition action"""
    
    def __init__(self, name, target_state, state_manager=None, condition_func=None, **kwargs):
        super().__init__(name, **kwargs)
        self.state_manager = state_manager
        self.target_state = target_state
        self.condition_func = condition_func
    
    async def execute(self):
        if self.state_manager is None:
            print(f"State transition action {self.name}: No state manager")
            return Status.FAILURE
        
        print(f"State transition action {self.name}: Attempting to transition to {self.target_state}")
        
        # Check transition conditions
        if self.condition_func and not self.condition_func(self.blackboard):
            print(f"State transition action {self.name}: Transition conditions not met")
            return Status.FAILURE
        
        # Execute state transition
        if self.state_manager.transition_to(self.target_state):
            print(f"State transition action {self.name}: Transition successful")
            return Status.SUCCESS
        else:
            print(f"State transition action {self.name}: Transition failed")
            return Status.FAILURE


class StateCondition(Condition):
    """State condition node"""
    
    def __init__(self, name, expected_state, state_manager=None, duration_check=None, **kwargs):
        super().__init__(name, **kwargs)
        self.state_manager = state_manager
        self.expected_state = expected_state
        self.duration_check = duration_check  # Minimum duration
    
    async def evaluate(self):
        if self.state_manager is None:
            print(f"State condition {self.name}: No state manager")
            return False
        
        current_state = self.state_manager.current_state
        state_match = current_state == self.expected_state
        
        if state_match and self.duration_check:
            duration = self.state_manager.get_state_duration()
            duration_ok = duration >= self.duration_check
            print(f"State condition {self.name}: State={current_state}, Duration={duration:.1f}s")
            return duration_ok
        else:
            print(f"State condition {self.name}: Current state={current_state}, Expected state={self.expected_state}")
            return state_match


class StateMonitoringAction(Action):
    """State monitoring action"""
    
    def __init__(self, name, state_manager=None, **kwargs):
        super().__init__(name, **kwargs)
        self.state_manager = state_manager
    
    async def execute(self):
        if self.state_manager is None:
            print(f"State monitoring action {self.name}: No state manager")
            return Status.FAILURE
        
        print(f"State monitoring action {self.name}: Monitoring current state")
        
        # Collect state information
        state_info = {
            'current_state': self.state_manager.current_state,
            'previous_state': self.state_manager.previous_state,
            'state_duration': self.state_manager.get_state_duration(),
            'history_count': len(self.state_manager.state_history),
            'timestamp': time.time()
        }
        
        # Update blackboard
        self.blackboard.set("state_info", state_info)
        self.blackboard.set("last_monitoring", time.time())
        
        print(f"State monitoring action {self.name}: State information updated")
        return Status.SUCCESS


class StateRecoveryAction(Action):
    """State recovery action"""
    
    def __init__(self, name, recovery_state="idle", state_manager=None, **kwargs):
        super().__init__(name, **kwargs)
        self.state_manager = state_manager
        self.recovery_state = recovery_state
    
    async def execute(self):
        if self.state_manager is None:
            print(f"State recovery action {self.name}: No state manager")
            return Status.FAILURE
        
        print(f"State recovery action {self.name}: Attempting to recover to {self.recovery_state}")
        
        # Check if current state is error state
        if self.state_manager.current_state == "error":
            # Attempt recovery
            if self.state_manager.transition_to(self.recovery_state):
                print(f"State recovery action {self.name}: Recovery successful")
                self.blackboard.set("recovery_successful", True)
                return Status.SUCCESS
            else:
                print(f"State recovery action {self.name}: Recovery failed")
                self.blackboard.set("recovery_successful", False)
                return Status.FAILURE
        else:
            print(f"State recovery action {self.name}: Current state is not error, no recovery needed")
            return Status.SUCCESS


class StatePersistenceAction(Action):
    """State persistence action"""
    
    def __init__(self, name, filepath, state_manager=None, **kwargs):
        super().__init__(name, **kwargs)
        self.state_manager = state_manager
        self.filepath = filepath
    
    async def execute(self):
        if self.state_manager is None:
            print(f"State persistence action {self.name}: No state manager")
            return Status.FAILURE
        
        print(f"State persistence action {self.name}: Saving state to {self.filepath}")
        
        success = self.state_manager.save_state(self.filepath)
        self.blackboard.set("state_saved", success)
        
        if success:
            print(f"State persistence action {self.name}: Save successful")
            return Status.SUCCESS
        else:
            print(f"State persistence action {self.name}: Save failed")
            return Status.FAILURE


class StateLoadAction(Action):
    """State load action"""
    
    def __init__(self, name, filepath, state_manager=None, **kwargs):
        super().__init__(name, **kwargs)
        self.state_manager = state_manager
        self.filepath = filepath
    
    async def execute(self):
        if self.state_manager is None:
            print(f"State load action {self.name}: No state manager")
            return Status.FAILURE
        
        print(f"State load action {self.name}: Loading state from {self.filepath}")
        
        success = self.state_manager.load_state(self.filepath)
        self.blackboard.set("state_loaded", success)
        
        if success:
            print(f"State load action {self.name}: Load successful")
            return Status.SUCCESS
        else:
            print(f"State load action {self.name}: Load failed")
            return Status.FAILURE


class ErrorDetectionCondition(Condition):
    """Error detection condition"""
    
    def __init__(self, name, error_threshold=3):
        super().__init__(name)
        self.error_threshold = error_threshold
    
    async def evaluate(self):
        error_count = self.blackboard.get("error_count", 0)
        print(f"Error detection condition {self.name}: Error count={error_count}, Threshold={self.error_threshold}")
        return error_count >= self.error_threshold


class MaintenanceRequiredCondition(Condition):
    """Maintenance required condition"""
    
    def __init__(self, name, maintenance_interval=60):  # Reduced from 300 to 60 seconds
        super().__init__(name)
        self.maintenance_interval = maintenance_interval
    
    async def evaluate(self):
        last_maintenance = self.blackboard.get("last_maintenance", 0)
        current_time = time.time()
        time_since_maintenance = current_time - last_maintenance
        
        print(f"Maintenance required condition {self.name}: Time since last maintenance {time_since_maintenance:.1f}s")
        return time_since_maintenance >= self.maintenance_interval


class WorkingStateAction(Action):
    """Working state action"""
    
    async def execute(self):
        print("Executing working state action...")
        await asyncio.sleep(0.01)  # Fast simulation
        
        # Simulate work process
        work_progress = self.blackboard.get("work_progress", 0)
        work_progress += random.randint(5, 15)
        self.blackboard.set("work_progress", work_progress)
        
        # Simulate possible errors
        if random.random() < 0.1:  # 10% error probability
            error_count = self.blackboard.get("error_count", 0) + 1
            self.blackboard.set("error_count", error_count)
            print(f"Error occurred during work process, error count: {error_count}")
        
        print(f"Work progress: {work_progress}%")
        return Status.SUCCESS


class MaintenanceAction(Action):
    """Maintenance action"""
    
    async def execute(self):
        print("Executing maintenance action...")
        await asyncio.sleep(0.01)  # Fast simulation
        
        # Execute maintenance
        self.blackboard.set("last_maintenance", time.time())
        self.blackboard.set("maintenance_count", self.blackboard.get("maintenance_count", 0) + 1)
        self.blackboard.set("error_count", 0)  # Reset error count
        
        print("Maintenance completed")
        return Status.SUCCESS


async def main():
    """Main function - Demonstrate state management"""
    
    # Register custom node types
    register_custom_nodes()
    
    print("=== ABTree State Management Example ===\n")
    
    # 1. Create state manager
    state_manager = StateManager("System State Manager", "idle")
    
    # 2. Create behavior tree
    root = Selector("State Management System")
    
    # 3. Create various state branches
    # Error recovery branch
    error_recovery = Sequence("Error Recovery")
    error_recovery.add_child(ErrorDetectionCondition("Detect Errors", 2))
    error_transition = StateTransitionAction("Transition to Error State", "error")
    error_transition.state_manager = state_manager
    error_recovery.add_child(error_transition)
    error_recovery_action = StateRecoveryAction("Recover State", "idle")
    error_recovery_action.state_manager = state_manager
    error_recovery.add_child(error_recovery_action)
    
    # Maintenance branch
    maintenance_branch = Sequence("Maintenance Branch")
    maintenance_branch.add_child(MaintenanceRequiredCondition("Check Maintenance Required", 30))  # Reduced from 60 to 30 seconds
    maintenance_transition = StateTransitionAction("Transition to Maintenance State", "maintenance")
    maintenance_transition.state_manager = state_manager
    maintenance_branch.add_child(maintenance_transition)
    maintenance_branch.add_child(MaintenanceAction("Execute Maintenance"))
    work_transition = StateTransitionAction("Transition to Working State", "working")
    work_transition.state_manager = state_manager
    maintenance_branch.add_child(work_transition)
    
    # Work branch
    work_branch = Sequence("Work Branch")
    state_condition = StateCondition("Check if Idle", "idle")
    state_condition.state_manager = state_manager
    work_branch.add_child(state_condition)
    start_work_transition = StateTransitionAction("Start Work", "working")
    start_work_transition.state_manager = state_manager
    work_branch.add_child(start_work_transition)
    work_branch.add_child(WorkingStateAction("Execute Work"))
    
    # State monitoring branch
    monitoring_branch = Sequence("State Monitoring")
    monitoring_action = StateMonitoringAction("Monitor State")
    monitoring_action.state_manager = state_manager
    monitoring_branch.add_child(monitoring_action)
    
    # State persistence branch
    persistence_branch = Sequence("State Persistence")
    persistence_action = StatePersistenceAction("Save State", "state_backup.json")
    persistence_action.state_manager = state_manager
    persistence_branch.add_child(persistence_action)
    
    # 4. Assemble behavior tree
    root.add_child(error_recovery)
    root.add_child(maintenance_branch)
    root.add_child(work_branch)
    root.add_child(monitoring_branch)
    root.add_child(persistence_branch)
    
    # 5. Create behavior tree instance
    tree = BehaviorTree()
    tree.load_from_node(root)
    blackboard = tree.blackboard
    
    # 6. Initialize data
    blackboard.set("work_progress", 0)
    blackboard.set("error_count", 0)
    blackboard.set("maintenance_count", 0)
    blackboard.set("last_maintenance", time.time())
    
    print("Starting state management system execution...")
    print("=" * 50)
    
    # 7. Execute multiple rounds of testing
    for i in range(8):  # Reduced from 15 to 8 cycles
        print(f"\n--- Round {i+1} Execution ---")
        
        # Execute behavior tree
        result = await tree.tick()
        print(f"Execution result: {result}")
        
        # Display current state
        state_info = blackboard.get("state_info", {})
        print(f"Current state: {state_info.get('current_state', 'unknown')}")
        print(f"Work progress: {blackboard.get('work_progress')}%")
        print(f"Error count: {blackboard.get('error_count')}")
        print(f"Maintenance count: {blackboard.get('maintenance_count')}")
        
        # Simulate some external events
        if i % 3 == 0:
            # Simulate errors
            error_count = blackboard.get("error_count", 0) + 1
            blackboard.set("error_count", error_count)
            print(f"Simulated error occurred, error count: {error_count}")
        
        await asyncio.sleep(0.01)  # Fast simulation
    
    # 8. Demonstrate state loading
    print("\n=== Demonstrate State Loading ===")
    if Path("state_backup.json").exists():
        load_action = StateLoadAction("Load State", "state_backup.json")
        load_action.state_manager = state_manager
        await load_action.execute(blackboard)
        print(f"State after loading: {state_manager.current_state}")
    
    print("\n=== Final Status ===")
    print(f"Final state: {state_manager.current_state}")
    print(f"State history count: {len(state_manager.state_history)}")
    print(f"Total work progress: {blackboard.get('work_progress')}%")
    print(f"Total error count: {blackboard.get('error_count')}")
    print(f"Total maintenance count: {blackboard.get('maintenance_count')}")
    
    # 9. Demonstrate XML configuration method
    print("\n=== XML Configuration Method Demo ===")
    
    # XML string configuration
    xml_config = '''
    <BehaviorTree name="StateManagementXML" description="XML configured state management example">
        <Sequence name="Root Sequence">
            <Selector name="State Management System">
                <Sequence name="Work Branch">
                    <StateCondition name="Check if Idle" expected_state="idle" />
                    <StateTransitionAction name="Start Work" target_state="working" />
                    <WorkingStateAction name="Execute Work" />
                </Sequence>
                <Sequence name="State Monitoring">
                    <StateMonitoringAction name="Monitor State" />
                </Sequence>
            </Selector>
        </Sequence>
    </BehaviorTree>
    '''
    
    # Parse XML configuration
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    xml_blackboard = xml_tree.blackboard
    
    # Initialize XML configuration data
    xml_blackboard.set("work_progress", 0)
    xml_blackboard.set("error_count", 0)
    xml_blackboard.set("maintenance_count", 0)
    xml_blackboard.set("last_maintenance", time.time())
    
    print("Behavior tree configured through XML string:")
    print(xml_config.strip())
    print("\nStarting execution of XML configured behavior tree...")
    xml_result = await xml_tree.tick()
    print(f"XML configuration execution completed! Result: {xml_result}")
    print(f"XML configuration work progress: {xml_blackboard.get('work_progress')}%")


if __name__ == "__main__":
    asyncio.run(main()) 