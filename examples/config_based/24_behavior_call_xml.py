#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 24: Behavior Call Communication - XML Configuration

Minimal example demonstrating Behavior Call communication pattern using XML.
"""

import asyncio
import tempfile
import os
from abtree import (
    BehaviorTree, Blackboard, Status,
    Action, Log, Wait,
    BehaviorForest, register_node
)
from abtree.parser.xml_parser import XMLParser


class CallerAction(Action):
    """Simple caller action"""
    
    def __init__(self, name: str, behavior: str):
        self.name = name
        self.behavior = behavior
    
    async def execute(self, blackboard):
        print(f"📞 Calling behavior: {self.behavior}")
        return Status.SUCCESS


class ProviderAction(Action):
    """Simple provider action"""
    
    def __init__(self, name: str, behavior: str):
        self.name = name
        self.behavior = behavior
    
    async def execute(self, blackboard):
        print(f"📞 Providing behavior: {self.behavior}")
        return Status.SUCCESS


def create_behavior_call_xml() -> str:
    """Create XML configuration for Behavior Call communication"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<BehaviorForest name="BehaviorCallForest" description="Behavior Call Communication Example">
    
    <BehaviorTree name="Caller" description="Caller Service">
        <Sequence name="Caller Behavior">
            <Log name="Caller Start" message="Caller starting" />
            <CallerAction name="Call Behavior" behavior="process" />
            <Wait name="Caller Wait" duration="1.0" />
        </Sequence>
    </BehaviorTree>
    
    <BehaviorTree name="Provider" description="Provider Service">
        <Sequence name="Provider Behavior">
            <Log name="Provider Start" message="Provider starting" />
            <ProviderAction name="Provide Behavior" behavior="process" />
            <Wait name="Provider Wait" duration="1.0" />
        </Sequence>
    </BehaviorTree>
    
    <Communication>
        <ComCall name="process">
            <ComProvider service="Provider" />
            <ComCaller service="Caller" />
        </ComCall>
    </Communication>
    
</BehaviorForest>'''


def register_custom_nodes():
    """Register custom node types"""
    register_node("CallerAction", CallerAction)
    register_node("ProviderAction", ProviderAction)


async def main():
    """Main function"""
    print("=== Behavior Call Communication Example ===\n")
    
    register_custom_nodes()
    
    xml_config = create_behavior_call_xml()
    
    forest = BehaviorForest()
    forest.load_from_string(xml_config)
    
    await forest.start()
    await asyncio.sleep(0.05)
    await forest.stop()


if __name__ == "__main__":
    asyncio.run(main()) 