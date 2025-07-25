#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Decorator Nodes Example

This example demonstrates the usage of various decorator nodes in the behavior tree.
Decorator nodes modify the behavior of their child nodes.
"""

import asyncio
from abtree.engine.behavior_tree import BehaviorTree
from abtree.engine.blackboard import Blackboard
from abtree.core.status import Status
from abtree.nodes.base import BaseNode
from abtree.nodes.decorator import Inverter, Repeater, UntilSuccess, UntilFailure


# Custom action node for demonstration
class SimpleAction(BaseNode):
    def __init__(self, name: str, should_succeed: bool = True):
        super().__init__(name)
        self.should_succeed = should_succeed
        self.execution_count = 0

    async def tick(self):
        self.execution_count += 1
        print(f"  {self.name} executed (count: {self.execution_count})")
        
        if self.should_succeed:
            return Status.SUCCESS
        else:
            return Status.FAILURE


# Custom decorator that always returns success
class AlwaysSuccessDecorator(BaseNode):
    def __init__(self, name: str, child: BaseNode):
        super().__init__(name, children=[child])
        self.child = child

    async def tick(self):
        if not self.child:
            return Status.FAILURE
        
        # Execute child but always return success
        await self.child.tick()
        return Status.SUCCESS


# Custom decorator that counts executions
class CountDecorator(BaseNode):
    def __init__(self, name: str, child: BaseNode):
        super().__init__(name, children=[child])
        self.child = child
        self.execution_count = 0

    async def tick(self):
        if not self.child:
            return Status.FAILURE
        
        self.execution_count += 1
        print(f"  {self.name} execution count: {self.execution_count}")
        
        result = await self.child.tick()
        return result


# Custom decorator that delays execution
class DelayDecorator(BaseNode):
    def __init__(self, name: str, child: BaseNode, delay: float = 0.1):
        super().__init__(name, children=[child])
        self.child = child
        self.delay = delay

    async def tick(self):
        if not self.child:
            return Status.FAILURE
        
        print(f"  {self.name} delaying for {self.delay} seconds...")
        await asyncio.sleep(self.delay)
        
        result = await self.child.tick()
        return result


async def main():
    print("=== Decorator Nodes Example ===\n")

    # Create blackboard
    blackboard = Blackboard()

    # 1. Inverter Decorator
    print("1. Inverter Decorator")
    print("   Inverts the result of the child node")
    
    success_action = SimpleAction("SuccessAction", should_succeed=True)
    failure_action = SimpleAction("FailureAction", should_succeed=False)
    
    inverter_success = Inverter("InverterSuccess", success_action)
    inverter_failure = Inverter("InverterFailure", failure_action)
    
    # Set blackboard on nodes
    success_action.set_blackboard(blackboard)
    failure_action.set_blackboard(blackboard)
    inverter_success.set_blackboard(blackboard)
    inverter_failure.set_blackboard(blackboard)
    
    result = await inverter_success.tick()
    print(f"   Inverter(Success) result: {result}")
    
    result = await inverter_failure.tick()
    print(f"   Inverter(Failure) result: {result}\n")

    # 2. Repeater Decorator
    print("2. Repeater Decorator")
    print("   Repeats the child node execution")
    
    repeat_action = SimpleAction("RepeatAction", should_succeed=True)
    repeater = Repeater("Repeater", repeat_action, repeat_count=3)
    
    repeat_action.set_blackboard(blackboard)
    repeater.set_blackboard(blackboard)
    
    print("   Executing repeater (3 times):")
    for i in range(4):
        result = await repeater.tick()
        print(f"   Tick {i+1}: {result}")
        if result == Status.SUCCESS:
            break
    print()

    # 3. Until Success Decorator
    print("3. Until Success Decorator")
    print("   Repeats until child succeeds")
    
    until_action = SimpleAction("UntilAction", should_succeed=False)
    until_success = UntilSuccess("UntilSuccess", until_action)
    
    until_action.set_blackboard(blackboard)
    until_success.set_blackboard(blackboard)
    
    print("   Executing until success (will keep running):")
    for i in range(3):
        result = await until_success.tick()
        print(f"   Tick {i+1}: {result}")
        if result == Status.SUCCESS:
            break
    
    # Change the action to succeed
    until_action.should_succeed = True
    result = await until_success.tick()
    print(f"   After change: {result}\n")

    # 4. Until Failure Decorator
    print("4. Until Failure Decorator")
    print("   Repeats until child fails")
    
    until_fail_action = SimpleAction("UntilFailAction", should_succeed=True)
    until_failure = UntilFailure("UntilFailure", until_fail_action)
    
    until_fail_action.set_blackboard(blackboard)
    until_failure.set_blackboard(blackboard)
    
    print("   Executing until failure (will keep running):")
    for i in range(3):
        result = await until_failure.tick()
        print(f"   Tick {i+1}: {result}")
        if result == Status.SUCCESS:
            break
    
    # Change the action to fail
    until_fail_action.should_succeed = False
    result = await until_failure.tick()
    print(f"   After change: {result}\n")

    # 5. Custom Decorators
    print("5. Custom Decorators")
    
    # Always Success Decorator
    normal_action = SimpleAction("NormalAction", should_succeed=False)
    always_success = AlwaysSuccessDecorator("AlwaysSuccess", normal_action)
    
    normal_action.set_blackboard(blackboard)
    always_success.set_blackboard(blackboard)
    
    result = await always_success.tick()
    print(f"   AlwaysSuccess result: {result}")
    
    # Count Decorator
    count_action = SimpleAction("CountAction", should_succeed=True)
    count_decorator = CountDecorator("CountDecorator", count_action)
    
    count_action.set_blackboard(blackboard)
    count_decorator.set_blackboard(blackboard)
    
    for i in range(3):
        result = await count_decorator.tick()
        print(f"   Count execution {i+1}: {result}")
    
    # Delay Decorator
    delay_action = SimpleAction("DelayAction", should_succeed=True)
    delay_decorator = DelayDecorator("DelayDecorator", delay_action, delay=0.1)
    
    delay_action.set_blackboard(blackboard)
    delay_decorator.set_blackboard(blackboard)
    
    print("   Executing with delay:")
    result = await delay_decorator.tick()
    print(f"   Delay result: {result}\n")

    # 6. Nested Decorators
    print("6. Nested Decorators")
    print("   Combining multiple decorators")
    
    base_action = SimpleAction("BaseAction", should_succeed=True)
    nested_decorator = Inverter("NestedInverter", 
                               Repeater("NestedRepeater", base_action, repeat_count=2))
    
    base_action.set_blackboard(blackboard)
    nested_decorator.set_blackboard(blackboard)
    
    result = await nested_decorator.tick()
    print(f"   Nested decorator result: {result}")

    print("\n=== Example completed ===")


if __name__ == "__main__":
    asyncio.run(main()) 