#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 07: Decorator Nodes - XML Configuration Version

This is the XML configuration version of the Decorator Nodes example.
It demonstrates how to configure various decorator nodes using XML.

Key Learning Points:
    - How to define different types of decorator nodes using XML
    - How to register custom decorator node types
    - How to parse XML configuration with decorator logic
    - Understanding decorator execution patterns in XML
"""

import asyncio
import time
import random
from abtree import BehaviorTree, Action, Decorator, register_node
from abtree.core import Status


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
    
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
    
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
                return Status.SUCCESS
        
        print(f"Until success {self.name}: failed after {self.max_attempts} attempts")
        return Status.FAILURE


class TimeoutDecorator(Decorator):
    """Timeout decorator - limits execution time"""
    
    def __init__(self, name, timeout_seconds=2.0, **kwargs):
        super().__init__(name, **kwargs)
        self.timeout_seconds = timeout_seconds
    
    async def tick(self, blackboard):
        print(f"Timeout decorator {self.name}: starting with {self.timeout_seconds}s timeout")
        start_time = time.time()
        
        try:
            # Execute child with timeout
            result = await asyncio.wait_for(
                self.child.tick(blackboard),
                timeout=self.timeout_seconds
            )
            print(f"Timeout decorator {self.name}: completed successfully")
            return result
        except asyncio.TimeoutError:
            print(f"Timeout decorator {self.name}: timed out after {self.timeout_seconds}s")
            return Status.FAILURE


class ConditionalDecorator(Decorator):
    """Conditional decorator - executes child only if condition is met"""
    
    def __init__(self, name, condition_key, condition_value=True, **kwargs):
        super().__init__(name, **kwargs)
        self.condition_key = condition_key
        self.condition_value = condition_value
    
    async def tick(self, blackboard):
        condition_met = blackboard.get(self.condition_key, False) == self.condition_value
        print(f"Conditional decorator {self.name}: condition {self.condition_key}={condition_met}")
        
        if condition_met:
            return await self.child.tick(blackboard)
        else:
            print(f"Conditional decorator {self.name}: skipping execution")
            return Status.SUCCESS


class RetryDecorator(Decorator):
    """Retry decorator - retries on failure with delay"""
    
    def __init__(self, name, max_retries=3, delay=0.5, **kwargs):
        super().__init__(name, **kwargs)
        self.max_retries = max_retries
        self.delay = delay
    
    async def tick(self, blackboard):
        for attempt in range(self.max_retries + 1):
            print(f"Retry decorator {self.name}: attempt {attempt + 1}/{self.max_retries + 1}")
            
            result = await self.child.tick(blackboard)
            if result == Status.SUCCESS:
                print(f"Retry decorator {self.name}: succeeded on attempt {attempt + 1}")
                return Status.SUCCESS
            
            if attempt < self.max_retries:
                print(f"Retry decorator {self.name}: waiting {self.delay}s before retry")
                await asyncio.sleep(self.delay)
        
        print(f"Retry decorator {self.name}: failed after {self.max_retries + 1} attempts")
        return Status.FAILURE


class SuccessAction(Action):
    """Action that always succeeds"""
    
    async def execute(self, blackboard):
        print(f"Executing success action: {self.name}")
        await asyncio.sleep(0.02)
        return Status.SUCCESS


class FailureAction(Action):
    """Action that always fails"""
    
    async def execute(self, blackboard):
        print(f"Executing failure action: {self.name}")
        await asyncio.sleep(0.02)
        return Status.FAILURE


class RandomAction(Action):
    """Action that randomly succeeds or fails"""
    
    def __init__(self, name, success_rate=0.5):
        self.name = name
        self.success_rate = success_rate
    
    async def execute(self, blackboard):
        print(f"Executing random action: {self.name}")
        await asyncio.sleep(0.02)
        
        if random.random() < self.success_rate:
            print(f"  {self.name} succeeded")
            return Status.SUCCESS
        else:
            print(f"  {self.name} failed")
            return Status.FAILURE


class LongRunningAction(Action):
    """Long-running action for timeout testing"""
    
    def __init__(self, name, duration=3.0):
        self.name = name
        self.duration = duration
    
    async def execute(self, blackboard):
        print(f"Starting long-running action: {self.name} ({self.duration}s)")
        
        for i in range(int(self.duration * 10)):
            await asyncio.sleep(0.01)
            if i % 10 == 0:
                print(f"  {self.name} progress: {i//10}/{int(self.duration)} seconds")
        
        print(f"Long-running action completed: {self.name}")
        return Status.SUCCESS


def register_custom_nodes():
    """Register custom node types for XML parsing"""
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


async def main():
    """Main function - demonstrate XML-based decorator node configuration"""
    
    print("=== ABTree Decorator Nodes XML Configuration Example ===\n")
    
    # Register custom node types for XML parsing
    register_custom_nodes()
    
    # XML string configuration
    xml_config = '''
    <BehaviorTree name="DecoratorNodesXML" description="Decorator nodes example with XML configuration">
        <Sequence name="Root Sequence">
            <Sequence name="Repeat Decorator Test">
                <RepeatDecorator name="Repeat 3 Times" repeat_count="3">
                    <SuccessAction name="Repeated Action" />
                </RepeatDecorator>
            </Sequence>
            <Sequence name="Inverter Decorator Test">
                <InverterDecorator name="Invert Success">
                    <SuccessAction name="Action to Invert" />
                </InverterDecorator>
            </Sequence>
            <Sequence name="Until Success Decorator Test">
                <UntilSuccessDecorator name="Until Success" max_attempts="3">
                    <RandomAction name="Random Action" success_rate="0.3" />
                </UntilSuccessDecorator>
            </Sequence>
            <Sequence name="Timeout Decorator Test">
                <TimeoutDecorator name="Timeout Test" timeout_seconds="1.0">
                    <LongRunningAction name="Long Action" duration="2.0" />
                </TimeoutDecorator>
            </Sequence>
            <Sequence name="Conditional Decorator Test">
                <ConditionalDecorator name="Conditional Test" condition_key="should_execute" condition_value="True">
                    <SuccessAction name="Conditional Action" />
                </ConditionalDecorator>
            </Sequence>
            <Sequence name="Retry Decorator Test">
                <RetryDecorator name="Retry Test" max_retries="2" delay="0.3">
                    <RandomAction name="Retry Action" success_rate="0.4" />
                </RetryDecorator>
            </Sequence>
        </Sequence>
    </BehaviorTree>
    '''
    
    # Parse XML configuration
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    xml_blackboard = xml_tree.blackboard
    
    # Initialize test data
    xml_blackboard.set("should_execute", True)
    
    print("Behavior tree configured by XML string:")
    print(xml_config.strip())
    print("\nStarting execution of XML-configured behavior tree...")
    
    # Execute behavior tree
    xml_result = await xml_tree.tick()
    
    print(f"\nXML configuration execution completed! Result: {xml_result}")
    print(f"Should execute: {xml_blackboard.get('should_execute')}")


if __name__ == "__main__":
    asyncio.run(main()) 