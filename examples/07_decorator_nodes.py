#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 07: Decorator Nodes in Depth – Using Various Decorator Nodes

Demonstrates how to create and use different types of decorator nodes.
Decorator nodes modify the behavior of their child nodes, such as repeating execution or inverting results.

Key Learning Points:

    Basic structure of decorator nodes

    Mechanisms for repeated execution

    Result inversion

    Conditional decorators

    Time-limiting decorators

    How to configure decorator nodes using XML strings
"""

import asyncio
import time
from abtree import BehaviorTree, Sequence, Selector, Action, Condition, Decorator, register_node
from abtree.core import Status
from abtree.parser.xml_parser import XMLParser


# Register custom node types
def register_custom_nodes():
    """Register custom node types"""
    register_node("RepeatDecorator", RepeatDecorator)
    register_node("InverterDecorator", InverterDecorator)
    register_node("UntilSuccessDecorator", UntilSuccessDecorator)
    register_node("TimeoutDecorator", TimeoutDecorator)
    register_node("ConditionalDecorator", ConditionalDecorator)
    register_node("RetryDecorator", RetryDecorator)
    register_node("SuccessAction", SuccessAction)
    register_node("FailureAction", FailureAction)
    register_node("RandomAction", RandomAction)
    register_node("LongRunningAction", LongRunningAction)


class RepeatDecorator(Decorator):
    """Repeat decorator - repeats child node execution for specified number of times"""
    
    def __init__(self, name, repeat_count=3, **kwargs):
        super().__init__(name, **kwargs)
        self.repeat_count = repeat_count
        self.current_count = 0
    
    async def tick(self, blackboard):
        if self.current_count >= self.repeat_count:
            self.current_count = 0
            return Status.SUCCESS
        
        self.current_count += 1
        print(f"Repeat execution {self.name}: {self.current_count}/{self.repeat_count} times")
        
        result = await self.child.tick(blackboard)
        print(f"Repeat execution {self.name}: child node returns {result}")
        
        return result


class InverterDecorator(Decorator):
    """Inverter decorator - inverts the result of child node"""
    
    async def tick(self, blackboard):
        print(f"Inverter decorator {self.name}: executing child node")
        result = await self.child.tick(blackboard)
        
        # Invert result
        if result == Status.SUCCESS:
            inverted_result = Status.FAILURE
        elif result == Status.FAILURE:
            inverted_result = Status.SUCCESS
        else:
            inverted_result = result
        
        print(f"Inverter decorator {self.name}: {result} -> {inverted_result}")
        return inverted_result


class UntilSuccessDecorator(Decorator):
    """Until success decorator - repeats execution until success"""
    
    def __init__(self, name, max_attempts=5, **kwargs):
        super().__init__(name, **kwargs)
        self.max_attempts = max_attempts
        self.attempt_count = 0
    
    async def tick(self, blackboard):
        while self.attempt_count < self.max_attempts:
            self.attempt_count += 1
            print(f"Until success {self.name}: attempt {self.attempt_count}/{self.max_attempts}")
            
            result = await self.child.tick(blackboard)
            if result == Status.SUCCESS:
                print(f"Until success {self.name}: succeeded on attempt {self.attempt_count}")
                self.attempt_count = 0
                return Status.SUCCESS
        
        print(f"Until success {self.name}: reached maximum attempts, returning failure")
        self.attempt_count = 0
        return Status.FAILURE


class TimeoutDecorator(Decorator):
    """Timeout decorator - limits child node execution time"""
    
    def __init__(self, name, timeout_seconds=2.0, **kwargs):
        super().__init__(name, **kwargs)
        self.timeout_seconds = timeout_seconds
    
    async def tick(self, blackboard):
        print(f"Timeout decorator {self.name}: starting execution, timeout {self.timeout_seconds} seconds")
        start_time = time.time()
        
        try:
            # Use asyncio.wait_for to set timeout
            result = await asyncio.wait_for(
                self.child.tick(blackboard),
                timeout=self.timeout_seconds
            )
            print(f"Timeout decorator {self.name}: completed normally, took {time.time() - start_time:.2f} seconds")
            return result
            
        except asyncio.TimeoutError:
            print(f"Timeout decorator {self.name}: execution timeout, took {time.time() - start_time:.2f} seconds")
            return Status.FAILURE


class ConditionalDecorator(Decorator):
    """Conditional decorator - decides whether to execute child node based on condition"""
    
    def __init__(self, name, condition_key, condition_value=True, **kwargs):
        super().__init__(name, **kwargs)
        self.condition_key = condition_key
        self.condition_value = condition_value
    
    async def tick(self, blackboard):
        condition_met = blackboard.get(self.condition_key, False) == self.condition_value
        
        if condition_met:
            print(f"Conditional decorator {self.name}: condition met, executing child node")
            return await self.child.tick(blackboard)
        else:
            print(f"Conditional decorator {self.name}: condition not met, skipping child node")
            return Status.FAILURE


class RetryDecorator(Decorator):
    """Retry decorator - automatically retries on failure"""
    
    def __init__(self, name, max_retries=3, delay=0.5, **kwargs):
        super().__init__(name, **kwargs)
        self.max_retries = max_retries
        self.delay = delay
        self.retry_count = 0
    
    async def tick(self, blackboard):
        while self.retry_count <= self.max_retries:
            result = await self.child.tick(blackboard)
            
            if result == Status.SUCCESS:
                print(f"Retry decorator {self.name}: success, no retry needed")
                self.retry_count = 0
                return Status.SUCCESS
            
            self.retry_count += 1
            if self.retry_count <= self.max_retries:
                print(f"Retry decorator {self.name}: failed, retrying in {self.delay} seconds ({self.retry_count}/{self.max_retries})")
                await asyncio.sleep(self.delay)
        
        print(f"Retry decorator {self.name}: reached maximum retries, final failure")
        self.retry_count = 0
        return Status.FAILURE


# Test action and condition nodes
class SuccessAction(Action):
    """Action that always succeeds"""
    
    async def execute(self, blackboard):
        print(f"Executing success action: {self.name}")
        await asyncio.sleep(0.01)
        return Status.SUCCESS


class FailureAction(Action):
    """Action that always fails"""
    
    async def execute(self, blackboard):
        print(f"Executing failure action: {self.name}")
        await asyncio.sleep(0.01)
        return Status.FAILURE


class RandomAction(Action):
    """Action that randomly succeeds or fails"""
    
    def __init__(self, name, success_rate=0.5, **kwargs):
        super().__init__(name, **kwargs)
        self.success_rate = success_rate
    
    async def execute(self, blackboard):
        import random
        success = random.random() < self.success_rate
        print(f"Executing random action: {self.name} - {'Success' if success else 'Failure'}")
        await asyncio.sleep(0.01)
        return Status.SUCCESS if success else Status.FAILURE


class LongRunningAction(Action):
    """Long-running action"""
    
    def __init__(self, name, duration=3.0, **kwargs):
        super().__init__(name, **kwargs)
        self.duration = duration
    
    async def execute(self, blackboard):
        print(f"Starting long-running action: {self.name} ({self.duration} seconds)")
        await asyncio.sleep(self.duration)
        print(f"Long-running action completed: {self.name}")
        return Status.SUCCESS


async def main():
    """Main function - demonstrates various decorator node usage"""
    
    # Register custom node types
    register_custom_nodes()
    
    print("=== ABTree Decorator Nodes Detailed Example ===\n")
    
    # 1. Create behavior tree
    root = Selector("Decorator Node Test")
    
    # 2. Create various decorator tests
    # Repeat execution test
    repeat_test = RepeatDecorator("Repeat 3 times", 3)
    repeat_test.add_child(SuccessAction("Success Action"))
    
    # Inverter test
    invert_test = InverterDecorator("Invert Failure")
    invert_test.add_child(FailureAction("Failure Action"))
    
    # Until success test
    until_success_test = UntilSuccessDecorator("Until Success", 5)
    until_success_test.add_child(RandomAction("Random Action", 0.3))
    
    # Timeout test
    timeout_test = TimeoutDecorator("2 second timeout", 2.0)
    timeout_test.add_child(LongRunningAction("Long Running Action", 3.0))
    
    # Conditional decorator test
    conditional_test = ConditionalDecorator("Conditional Execution", "should_execute", True)
    conditional_test.add_child(SuccessAction("Conditional Action"))
    
    # Retry test
    retry_test = RetryDecorator("Retry 3 times", 3, 0.3)
    retry_test.add_child(RandomAction("Retry Action", 0.4))
    
    # 3. Add to root node
    root.add_child(repeat_test)
    root.add_child(invert_test)
    root.add_child(until_success_test)
    root.add_child(timeout_test)
    root.add_child(conditional_test)
    root.add_child(retry_test)
    
    # 3. Create behavior tree
    tree = BehaviorTree()
    tree.load_from_node(root)
    blackboard = tree.blackboard
    
    # 5. Set test data
    blackboard.set("should_execute", True)
    
    print("Starting decorator node test...")
    print("=" * 50)
    
    # 6. Execute behavior tree
    result = await tree.tick()
    
    # 7. Show results
    print("=" * 50)
    print(f"Execution result: {result}")
    
    # 8. Demonstrate conditional decorator condition change
    print("\n=== Demonstrate Conditional Decorator Condition Change ===")
    blackboard.set("should_execute", False)
    result2 = await tree.tick()
    print(f"Result after condition change: {result2}")
    
    # 9. Demonstrate XML configuration method
    print("\n=== XML Configuration Method Demo ===")   


if __name__ == "__main__":
    asyncio.run(main()) 