#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 22: Shared Blackboard Communication - XML Configuration

Minimal example demonstrating Shared Blackboard communication pattern using XML.
"""

import asyncio
import tempfile
import os
from abtree import (
    BehaviorTree, Blackboard, Status,
    Action, Log, Wait, SetBlackboard, CheckBlackboard,
    BehaviorForest, register_node
)
from abtree.parser.xml_parser import XMLParser


class WriterAction(Action):
    """Simple writer action"""
    
    def __init__(self, name: str, key: str, value: str):
        self.name = name
        self.key = key
        self.value = value
    
    async def execute(self, blackboard):
        print(f"✍️ Writing {self.key}: {self.value}")
        return Status.SUCCESS


class ReaderAction(Action):
    """Simple reader action"""
    
    def __init__(self, name: str, key: str):
        self.name = name
        self.key = key
    
    async def execute(self, blackboard):
        print(f"📖 Reading {self.key}")
        return Status.SUCCESS


def create_shared_blackboard_xml() -> str:
    """Create XML configuration for Shared Blackboard communication"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<BehaviorForest name="SharedBlackboardForest" description="Shared Blackboard Communication Example">
    
    <BehaviorTree name="Writer" description="Writer Service">
        <Sequence name="Writer Behavior">
            <Log name="Writer Start" message="Writer starting" />
            <WriterAction name="Write Data" key="status" value="active" />
            <Wait name="Writer Wait" duration="1.0" />
        </Sequence>
    </BehaviorTree>
    
    <BehaviorTree name="Reader" description="Reader Service">
        <Sequence name="Reader Behavior">
            <Log name="Reader Start" message="Reader starting" />
            <ReaderAction name="Read Data" key="status" />
            <Wait name="Reader Wait" duration="1.0" />
        </Sequence>
    </BehaviorTree>
    
    <Communication>
        <ComShared>
            <ComKey name="status" />
            <ComKey name="data" />
        </ComShared>
    </Communication>
    
</BehaviorForest>'''


def register_custom_nodes():
    """Register custom node types"""
    register_node("WriterAction", WriterAction)
    register_node("ReaderAction", ReaderAction)


async def main():
    """Main function"""
    print("=== Shared Blackboard Communication Example ===\n")
    
    register_custom_nodes()
    
    xml_config = create_shared_blackboard_xml()
    
    forest = BehaviorForest()
    forest.load_from_string(xml_config)
    
    await forest.start()
    await asyncio.sleep(0.05)
    await forest.stop()


if __name__ == "__main__":
    asyncio.run(main()) 