#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 27: Task Board Communication - XML Configuration

Minimal example demonstrating Task Board communication pattern using XML.
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


class TaskPublisherAction(Action):
    """Simple task publisher action"""
    
    def __init__(self, name: str, task: str):
        self.name = name
        self.task = task
    
    async def execute(self, blackboard):
        print(f"📋 Publishing task: {self.task}")
        return Status.SUCCESS


class TaskClaimantAction(Action):
    """Simple task claimant action"""
    
    def __init__(self, name: str, task: str):
        self.name = name
        self.task = task
    
    async def execute(self, blackboard):
        print(f"📋 Claiming task: {self.task}")
        return Status.SUCCESS


def create_task_board_xml() -> str:
    """Create XML configuration for Task Board communication"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<BehaviorForest name="TaskBoardForest" description="Task Board Communication Example">
    
    <BehaviorTree name="Publisher" description="Task Publisher Service">
        <Sequence name="Publisher Behavior">
            <Log name="Publisher Start" message="Publisher starting" />
            <TaskPublisherAction name="Publish Task" task="work" />
            <Wait name="Publisher Wait" duration="1.0" />
        </Sequence>
    </BehaviorTree>
    
    <BehaviorTree name="Claimant" description="Task Claimant Service">
        <Sequence name="Claimant Behavior">
            <Log name="Claimant Start" message="Claimant starting" />
            <TaskClaimantAction name="Claim Task" task="work" />
            <Wait name="Claimant Wait" duration="1.0" />
        </Sequence>
    </BehaviorTree>
    
    <Communication>
        <CommTask name="work">
            <CommPublisher service="Publisher" />
            <ComClaimant service="Claimant" />
        </CommTask>
    </Communication>
    
</BehaviorForest>'''


def register_custom_nodes():
    """Register custom node types"""
    register_node("TaskPublisherAction", TaskPublisherAction)
    register_node("TaskClaimantAction", TaskClaimantAction)


async def main():
    """Main function"""
    print("=== Task Board Communication Example ===\n")
    
    register_custom_nodes()
    
    xml_config = create_task_board_xml()
    
    forest = BehaviorForest()
    forest.load_from_string(xml_config)
    
    await forest.start()
    await asyncio.sleep(0.05)
    await forest.stop()


if __name__ == "__main__":
    asyncio.run(main()) 