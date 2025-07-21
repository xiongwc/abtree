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
    tree.load_from_node(root)
    
    # 3. Execute behavior tree
    print("Start executing behavior tree...")
    result = await tree.tick()
    
    # 4. Output result
    print(f"\nExecution completed! Result: {result}")
    print(f"Status description: {result.name}")


if __name__ == "__main__":
    asyncio.run(main()) 