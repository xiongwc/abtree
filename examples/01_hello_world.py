#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 01: Hello World - Basic Usage of ABTree

This is a beginner-friendly example demonstrating the most basic usage of the ABTree framework. It shows how to create and run a simple behavior tree, making it ideal for users with no prior experience.

Key Learning Points:

    How to create a behavior tree

    How to define action nodes

    How to execute the behavior tree

    Understanding the SUCCESS status

    How to configure a behavior tree using an XML string
"""

import asyncio
from abtree import BehaviorTree, Action, register_node
from abtree.core import Status
from abtree.parser.xml_parser import XMLParser


class HelloWorldAction(Action):
    """The simplest action node - print Hello World"""
    
    async def execute(self, blackboard):
        print("Hello World! This is the first example of ABTree")
        return Status.SUCCESS


async def main():
    """Main function - demonstrate basic behavior tree creation and execution"""
    
    print("=== ABTree Hello World Example ===\n")   

    
    # 1. Create root node
    root = HelloWorldAction("Greeting")
    
    # 2. Create behavior tree
    tree = BehaviorTree()
    tree.load_from_root(root)
    
    # 3. Execute behavior tree
    print("Start executing behavior tree...")
    result = await tree.tick()
    
    # 4. Output result
    print(f"\nExecution completed! Result: {result}")
    print(f"Status description: {result.name}")
    
    # 5. Demonstrate XML configuration
    print("\n=== XML configuration demonstration ===")
    
    # XML string configuration
    xml_config = '''
    <BehaviorTree name="HelloWorldXML" description="Hello World example with XML configuration">
        <Sequence name="RootSequence">
            <HelloWorldAction name="Greeting" />
        </Sequence>
    </BehaviorTree>
    '''
    
    # Register the custom node type
    register_node("HelloWorldAction", HelloWorldAction)

    # Parse XML configuration
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    
    print("Behavior tree configured by XML string:")
    print(xml_config.strip())
    print("\nStart executing behavior tree configured by XML...")
    xml_result = await xml_tree.tick()
    print(f"XML configuration execution completed! Result: {xml_result}")


if __name__ == "__main__":
    asyncio.run(main()) 