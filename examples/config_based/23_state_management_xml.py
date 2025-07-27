#!/usr/bin/env python3
"""
Example 23: State Management - XML Configuration

Simple state management example demonstrating:
- State transitions and conditions
- Error handling and recovery
"""

import asyncio
import time
import random
from abtree import (
    BehaviorTree, Sequence, Selector, Action, Condition, Status,
    Blackboard, register_node,
)


class StateManager:
    """Simple state manager for system states"""
    
    def __init__(self, name, initial_state="idle"):
        self.name = name
        self.current_state = initial_state
    
    def transition_to(self, new_state):
        """Transition to new state"""
        old_state = self.current_state
        self.current_state = new_state
        print(f"State transition: {old_state} -> {new_state}")
        return True


class StateTransitionAction(Action):
    """Action to transition to a new state"""
    
    def __init__(self, name, target_state, **kwargs):
        super().__init__(name)
        self.target_state = target_state
    
    async def execute(self):
        state_manager = self.blackboard.get("state_manager")
        if state_manager:
            state_manager.transition_to(self.target_state)
            return Status.SUCCESS
        return Status.FAILURE


class StateCondition(Condition):
    """Condition to check current state"""
    
    def __init__(self, name, expected_state, **kwargs):
        super().__init__(name)
        self.expected_state = expected_state
    
    async def evaluate(self):
        state_manager = self.blackboard.get("state_manager")
        if state_manager:
            return state_manager.current_state == self.expected_state
        return False


class ErrorDetectionCondition(Condition):
    """Condition to detect errors"""
    
    def __init__(self, name, error_threshold=3, **kwargs):
        super().__init__(name)
        self.error_threshold = error_threshold
    
    async def evaluate(self):
        error_count = self.blackboard.get("error_count", 0)
        return error_count >= self.error_threshold


class WorkingAction(Action):
    """Action to perform work"""
    
    async def execute(self):
        print("Performing work...")
        work_count = self.blackboard.get("work_count", 0) + 1
        self.blackboard.set("work_count", work_count)
        return Status.SUCCESS


class RecoveryAction(Action):
    """Action to recover from error state"""
    
    async def execute(self):
        print("Recovering from error...")
        self.blackboard.set("error_count", 0)
        return Status.SUCCESS


class IdleAction(Action):
    """Action to perform idle operations"""
    
    async def execute(self):
        print("System idle...")
        return Status.SUCCESS


def register_custom_nodes():
    """Register custom node types"""
    register_node("StateTransitionAction", StateTransitionAction)
    register_node("StateCondition", StateCondition)
    register_node("ErrorDetectionCondition", ErrorDetectionCondition)
    register_node("WorkingAction", WorkingAction)
    register_node("RecoveryAction", RecoveryAction)
    register_node("IdleAction", IdleAction)


async def main():
    """Main function - Demonstrate simplified state management"""
    
    print("=== ABTree State Management Example ===\n")
    
    # Register custom nodes
    register_custom_nodes()
    
    # Create state manager and blackboard
    state_manager = StateManager("SystemState")
    blackboard = Blackboard()
    blackboard.set("state_manager", state_manager)
    blackboard.set("error_count", 0)
    blackboard.set("work_count", 0)
    
    # Create behavior tree
    tree = BehaviorTree(blackboard=blackboard)
    
    # XML configuration
    xml_config = '''
    <BehaviorTree name="StateManagement">
        <Selector name="Root">
            <Sequence name="Error Handling">
                <ErrorDetectionCondition name="Check Errors" error_threshold="3" />
                <StateTransitionAction name="Go to Error" target_state="error" />
                <RecoveryAction name="Recover" />
                <StateTransitionAction name="Return to Idle" target_state="idle" />
            </Sequence>
            <Sequence name="Work Cycle">
                <StateCondition name="Check Idle" expected_state="idle" />
                <StateTransitionAction name="Start Working" target_state="working" />
                <WorkingAction name="Work" />
                <StateTransitionAction name="Return to Idle" target_state="idle" />
            </Sequence>
            <IdleAction name="Stay Idle" />
        </Selector>
    </BehaviorTree>
    '''
    
    # Load configuration
    tree.load_from_string(xml_config)
    
    print("State management system configured:")
    print("- Error handling and recovery")
    print("- Normal work cycle")
    print("- Idle behavior")
    
    # Execute for several rounds
    print("\n=== Starting execution ===")
    
    for i in range(8):
        print(f"\n--- Round {i+1} ---")
        
        # Simulate random events
        if random.random() < 0.15:  # 15% chance of error
            blackboard.set("error_count", blackboard.get("error_count", 0) + 1)
            print("⚠️ Error detected!")
        
        # Execute behavior tree
        result = await tree.tick()
        print(f"Result: {result}")
        print(f"Current state: {state_manager.current_state}")
        
        await asyncio.sleep(0.01)
    
    print("\nExecution complete!")


if __name__ == "__main__":
    asyncio.run(main()) 