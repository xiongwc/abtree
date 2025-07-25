#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 01: Hello World - XML Configuration Version

This is the XML configuration version of the Hello World example.
It demonstrates how to configure behavior trees using XML instead of code.

Key Learning Points:
    - How to define behavior trees using XML
    - How to register custom node types
    - How to parse XML configuration
    - Understanding the difference between code-based and XML-based configuration
"""

import asyncio
from abtree import BehaviorTree, Action, register_node
from abtree.core import Status


class HelloWorldAction(Action):
    """The simplest action node - print Hello World"""
    
    async def execute(self):
        print("Hello World! This is the XML configuration version of ABTree")
        return Status.SUCCESS


async def main():
    """Main function - demonstrate XML-based behavior tree configuration"""
    
    print("=== ABTree Hello World XML Configuration Example ===\n")
    
    # Register the custom node type for XML parsing
    register_node("HelloWorldAction", HelloWorldAction)
    
    # XML string configuration
    xml_config = '''
    <BehaviorTree name="HelloWorld" description="Hello World example with XML configuration">
        <Sequence name="RootSequence">
            <HelloWorldAction name="Greeting" />
        </Sequence>
    </BehaviorTree>
    '''
    
    # Parse XML configuration
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    
    print("Behavior tree configured by XML string:")
    print(xml_config.strip())
    print("\nStart executing behavior tree configured by XML...")
    
    # Execute behavior tree
    xml_result = await xml_tree.tick()
    print(f"XML configuration execution completed! Result: {xml_result}")
    print(f"Status description: {xml_result.name}")


if __name__ == "__main__":
    asyncio.run(main()) 