#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 25: State Watching Communication - XML Configuration

Minimal example demonstrating State Watching communication pattern using XML.
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


class StateChangerAction(Action):
    """Simple state changer action"""
    
    def __init__(self, name: str, state: str):
        self.name = name
        self.state = state
    
    async def execute(self, blackboard):
        print(f"🔄 Changing state to: {self.state}")
        return Status.SUCCESS


class StateWatcherAction(Action):
    """Simple state watcher action"""
    
    def __init__(self, name: str, state: str):
        self.name = name
        self.state = state
    
    async def execute(self, blackboard):
        print(f"👀 Watching state: {self.state}")
        return Status.SUCCESS


def create_state_watching_xml() -> str:
    """Create XML configuration for State Watching communication"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<BehaviorForest name="StateWatchingForest" description="State Watching Communication Example">
    
    <BehaviorTree name="Changer" description="State Changer Service">
        <Sequence name="Changer Behavior">
            <Log name="Changer Start" message="Changer starting" />
            <StateChangerAction name="Change State" state="active" />
            <Wait name="Changer Wait" duration="1.0" />
        </Sequence>
    </BehaviorTree>
    
    <BehaviorTree name="Watcher" description="State Watcher Service">
        <Sequence name="Watcher Behavior">
            <Log name="Watcher Start" message="Watcher starting" />
            <StateWatcherAction name="Watch State" state="status" />
            <Wait name="Watcher Wait" duration="1.0" />
        </Sequence>
    </BehaviorTree>
    
    <Communication>
        <CommState name="status">
            <CommWatcher service="Watcher" />
        </CommState>
    </Communication>
    
</BehaviorForest>'''


def register_custom_nodes():
    """Register custom node types"""
    register_node("StateChangerAction", StateChangerAction)
    register_node("StateWatcherAction", StateWatcherAction)


async def main():
    """Main function"""
    print("=== State Watching Communication Example ===\n")
    
    register_custom_nodes()
    
    xml_config = create_state_watching_xml()
    
    forest = BehaviorForest()
    forest.load_from_string(xml_config)
    
    await forest.start()
    await asyncio.sleep(0.05)
    await forest.stop()


if __name__ == "__main__":
    asyncio.run(main()) 