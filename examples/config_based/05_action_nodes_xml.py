#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 05: Action Nodes - XML Configuration Version

This is the XML configuration version of the Action Nodes example.
It demonstrates how to configure various action nodes using XML.

Key Learning Points:
    - How to define different types of action nodes using XML
    - How to register custom action node types
    - How to parse XML configuration with complex action logic
    - Understanding action node execution patterns in XML
"""

import asyncio
import random
from abtree import BehaviorTree, Action, register_node
from abtree.core import Status


class SimpleAction(Action):
    """Simple action node - always succeeds"""
    
    async def execute(self, blackboard):
        print(f"Executing simple action: {self.name}")
        await asyncio.sleep(0.02)
        return Status.SUCCESS


class ConditionalAction(Action):
    """Conditional action node - decides success or failure based on conditions"""
    
    def __init__(self, name, success_rate=0.7):
        self.name = name
        self.success_rate = success_rate
    
    async def execute(self, blackboard):
        print(f"Executing conditional action: {self.name}")
        await asyncio.sleep(0.03)
        
        # Decide result based on success rate
        if random.random() < self.success_rate:
            print(f"  {self.name} succeeded")
            return Status.SUCCESS
        else:
            print(f"  {self.name} failed")
            return Status.FAILURE


class LongRunningAction(Action):
    """Long-running action node"""
    
    def __init__(self, name, duration=2.0):
        self.name = name
        self.duration = duration
    
    async def execute(self, blackboard):
        print(f"Starting long-running task: {self.name} (estimated {self.duration} seconds)")
        
        # Simulate long processing
        for i in range(int(self.duration * 10)):
            await asyncio.sleep(0.01)
            if i % 10 == 0:
                print(f"  {self.name} progress: {i//10}/{int(self.duration)} seconds")
        
        print(f"Long-running task completed: {self.name}")
        return Status.SUCCESS


class DataProcessingAction(Action):
    """Data processing action node"""
    
    async def execute(self, blackboard):
        print(f"Starting data processing: {self.name}")
        
        # Get input data
        input_data = blackboard.get("input_data", [])
        if not input_data:
            print("  No input data, skipping processing")
            return Status.SUCCESS
        
        # Process data
        processed_data = []
        for item in input_data:
            processed_item = item * 2
            processed_data.append(processed_item)
            await asyncio.sleep(0.01)
        
        # Store results
        blackboard.set("processed_data", processed_data)
        blackboard.set("processing_count", blackboard.get("processing_count", 0) + 1)
        
        print(f"  Processed {len(processed_data)} items")
        return Status.SUCCESS


class ErrorHandlingAction(Action):
    """Error handling action node"""
    
    def __init__(self, name, should_fail=False):
        self.name = name
        self.should_fail = should_fail
    
    async def execute(self, blackboard):
        print(f"Executing error handling action: {self.name}")
        
        try:
            if self.should_fail:
                raise Exception("Simulated error for testing")
            
            await asyncio.sleep(0.05)
            print(f"  {self.name} completed successfully")
            return Status.SUCCESS
            
        except Exception as e:
            print(f"  {self.name} encountered error: {e}")
            blackboard.set("last_error", str(e))
            return Status.FAILURE


def register_custom_nodes():
    """Register custom node types for XML parsing"""
    register_node("SimpleAction", SimpleAction)
    register_node("ConditionalAction", ConditionalAction)
    register_node("LongRunningAction", LongRunningAction)
    register_node("DataProcessingAction", DataProcessingAction)
    register_node("ErrorHandlingAction", ErrorHandlingAction)


async def main():
    """Main function - demonstrate XML-based action node configuration"""
    
    print("=== ABTree Action Nodes XML Configuration Example ===\n")
    
    # Register custom node types for XML parsing
    register_custom_nodes()
    
    # XML string configuration
    xml_config = '''
    <BehaviorTree name="ActionNodes" description="Action nodes example with XML configuration">
        <Sequence name="Root Sequence">
            <Sequence name="Simple Actions">
                <SimpleAction name="Task 1" />
                <SimpleAction name="Task 2" />
                <SimpleAction name="Task 3" />
            </Sequence>
            <Sequence name="Conditional Actions">
                <ConditionalAction name="Risky Task 1" />
                <ConditionalAction name="Risky Task 2" />
                <ConditionalAction name="Risky Task 3" />
            </Sequence>
            <Sequence name="Data Processing">
                <DataProcessingAction name="Process Data" />
            </Sequence>
            <Sequence name="Error Handling">
                <ErrorHandlingAction name="Safe Task" />
                <ErrorHandlingAction name="Failing Task" />
            </Sequence>
        </Sequence>
    </BehaviorTree>
    '''
    
    # Parse XML configuration
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    xml_blackboard = xml_tree.blackboard
    
    # Initialize test data
    xml_blackboard.set("input_data", [1, 2, 3, 4, 5])
    xml_blackboard.set("processing_count", 0)
    
    print("Behavior tree configured by XML string:")
    print(xml_config.strip())
    print("\nStarting execution of XML-configured behavior tree...")
    
    # Execute behavior tree
    xml_result = await xml_tree.tick()
    
    print(f"\nXML configuration execution completed! Result: {xml_result}")
    print(f"Processing count: {xml_blackboard.get('processing_count')}")
    print(f"Processed data: {xml_blackboard.get('processed_data')}")
    print(f"Last error: {xml_blackboard.get('last_error', 'None')}")


if __name__ == "__main__":
    asyncio.run(main()) 