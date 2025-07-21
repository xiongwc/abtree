#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 05: Action Nodes in Depth – Using Various Action Nodes

Demonstrates how to create and use different types of action nodes.
Action nodes are the core components in a behavior tree that perform actual tasks.

Key Learning Points:

    Basic structure of action nodes

    Handling different return statuses

    Dealing with asynchronous operations

    Error handling mechanisms

    How to configure action nodes using XML strings
"""

import asyncio
import random
from abtree import BehaviorTree, Sequence, Selector, Action, register_node
from abtree.core import Status
from abtree.parser.xml_parser import XMLParser


# Register custom node types
def register_custom_nodes():
    """Register custom node types"""
    register_node("SimpleAction", SimpleAction)
    register_node("ConditionalAction", ConditionalAction)
    register_node("LongRunningAction", LongRunningAction)
    register_node("DataProcessingAction", DataProcessingAction)
    register_node("ErrorHandlingAction", ErrorHandlingAction)


class SimpleAction(Action):
    """Simple action node - always succeeds"""
    
    async def execute(self, blackboard):
        print(f"Executing simple action: {self.name}")
        await asyncio.sleep(0.2)
        return Status.SUCCESS


class ConditionalAction(Action):
    """Conditional action node - decides success or failure based on conditions"""
    
    def __init__(self, name, success_rate=0.7):
        super().__init__(name)
        self.success_rate = success_rate
    
    async def execute(self, blackboard):
        print(f"Executing conditional action: {self.name}")
        await asyncio.sleep(0.3)
        
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
        super().__init__(name)
        self.duration = duration
    
    async def execute(self, blackboard):
        print(f"Starting long-running task: {self.name} (estimated {self.duration} seconds)")
        
        # Simulate long processing
        for i in range(int(self.duration * 10)):
            await asyncio.sleep(0.1)
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
            await asyncio.sleep(0.1)  # Simulate processing time
            processed_item = item * 2
            processed_data.append(processed_item)
            print(f"  Processing data: {item} -> {processed_item}")
        
        # Save results to blackboard
        blackboard.set("processed_data", processed_data)
        blackboard.set("processing_count", len(processed_data))
        
        print(f"Data processing completed, processed {len(processed_data)} items")
        return Status.SUCCESS


class ErrorHandlingAction(Action):
    """Error handling action node"""
    
    def __init__(self, name, should_fail=False):
        super().__init__(name)
        self.should_fail = should_fail
    
    async def execute(self, blackboard):
        print(f"Executing error handling action: {self.name}")
        
        if self.should_fail:
            print(f"  {self.name} simulating error")
            # Record error to blackboard
            error_count = blackboard.get("error_count", 0) + 1
            blackboard.set("error_count", error_count)
            blackboard.set("last_error", f"{self.name} failed")
            return Status.FAILURE
        
        await asyncio.sleep(0.2)
        print(f"  {self.name} executed successfully")
        return Status.SUCCESS


async def main():
    """Main function - demonstrate various action node usage"""
    
    # 注册自定义节点类型
    register_custom_nodes()
    
    print("=== ABTree Action Nodes Detailed Example ===\n")
    
    # 1. Create behavior tree
    root = Selector("Action Node Test")
    
    # 2. Add different types of action nodes
    # Simple action sequence
    simple_sequence = Sequence("Simple Action Sequence")
    simple_sequence.add_child(SimpleAction("Action 1"))
    simple_sequence.add_child(SimpleAction("Action 2"))
    simple_sequence.add_child(SimpleAction("Action 3"))
    
    # Conditional action sequence
    conditional_sequence = Sequence("Conditional Action Sequence")
    conditional_sequence.add_child(ConditionalAction("Conditional Action 1", 0.8))
    conditional_sequence.add_child(ConditionalAction("Conditional Action 2", 0.6))
    conditional_sequence.add_child(ConditionalAction("Conditional Action 3", 0.9))
    
    # Long-running task
    long_task = LongRunningAction("Long-Running Task", 1.5)
    
    # Data processing task
    data_sequence = Sequence("Data Processing Sequence")
    data_sequence.add_child(DataProcessingAction("Data Processing"))
    data_sequence.add_child(SimpleAction("Data Validation"))
    
    # Error handling task
    error_sequence = Sequence("Error Handling Sequence")
    error_sequence.add_child(ErrorHandlingAction("Normal Task"))
    error_sequence.add_child(ErrorHandlingAction("Error Task", should_fail=True))
    error_sequence.add_child(SimpleAction("Recovery Task"))
    
    # 3. Add to root node
    root.add_child(simple_sequence)
    root.add_child(conditional_sequence)
    root.add_child(long_task)
    root.add_child(data_sequence)
    root.add_child(error_sequence)
    
    # 3. Create behavior tree
    tree = BehaviorTree()
    tree.load_from_root(root)
    blackboard = tree.blackboard
    
    # 5. Set test data
    blackboard.set("input_data", [1, 2, 3, 4, 5])
    blackboard.set("error_count", 0)
    
    print("Starting action node test...")
    print("=" * 50)
    
    # 6. Execute behavior tree
    result = await tree.tick()
    
    # 7. Display results
    print("=" * 50)
    print(f"Execution result: {result}")
    print(f"Processed data: {blackboard.get('processed_data', [])}")
    print(f"Error count: {blackboard.get('error_count', 0)}")
    print(f"Last error: {blackboard.get('last_error', 'None')}")
    
    # 8. Demonstrate XML configuration method
    print("\n=== XML Configuration Method Demo ===")
    
    # XML string configuration
    xml_config = '''
    <BehaviorTree name="ActionNodesXML" description="Action nodes example with XML configuration">
        <Sequence name="Root Sequence">
            <Selector name="Action Node Test">
                <Sequence name="Simple Action Sequence">
                    <SimpleAction name="Action 1" />
                    <SimpleAction name="Action 2" />
                    <SimpleAction name="Action 3" />
                </Sequence>
                <Sequence name="Conditional Action Sequence">
                    <ConditionalAction name="Conditional Action 1" success_rate="0.8" />
                    <ConditionalAction name="Conditional Action 2" success_rate="0.6" />
                    <ConditionalAction name="Conditional Action 3" success_rate="0.9" />
                </Sequence>
                <LongRunningAction name="Long-Running Task" duration="1.0" />
                <Sequence name="Data Processing Sequence">
                    <DataProcessingAction name="Data Processing" />
                    <SimpleAction name="Data Validation" />
                </Sequence>
            </Selector>
        </Sequence>
    </BehaviorTree>
    '''
    
    # Parse XML configuration
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    xml_blackboard = xml_tree.blackboard
    
    # Set XML configuration test data
    xml_blackboard.set("input_data", [10, 20, 30])
    xml_blackboard.set("error_count", 0)
    
    print("Behavior tree configured by XML string:")
    print(xml_config.strip())
    print("\nStarting execution of XML-configured behavior tree...")
    xml_result = await xml_tree.tick()
    print(f"XML configuration execution completed! Result: {xml_result}")
    print(f"XML configuration processed data: {xml_blackboard.get('processed_data', [])}")


if __name__ == "__main__":
    asyncio.run(main()) 