#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 21: Request-Response Communication - XML Configuration

Minimal example demonstrating Request-Response communication pattern using XML.
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


class ClientAction(Action):
    """Simple client action"""
    
    def __init__(self, name: str, service: str):
        self.name = name
        self.service = service
    
    async def execute(self, blackboard):
        print(f"📤 Requesting service: {self.service}")
        return Status.SUCCESS


class ServerAction(Action):
    """Simple server action"""
    
    def __init__(self, name: str, service: str):
        self.name = name
        self.service = service
    
    async def execute(self, blackboard):
        print(f"📥 Serving: {self.service}")
        return Status.SUCCESS


def create_reqresp_xml() -> str:
    """Create XML configuration for Request-Response communication"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<BehaviorForest name="ReqRespForest" description="Request-Response Communication Example">
    
    <BehaviorTree name="Client" description="Client Service">
        <Sequence name="Client Behavior">
            <Log name="Client Start" message="Client starting" />
            <ClientAction name="Request Service" service="data" />
            <Wait name="Client Wait" duration="1.0" />
        </Sequence>
    </BehaviorTree>
    
    <BehaviorTree name="Server" description="Server Service">
        <Sequence name="Server Behavior">
            <Log name="Server Start" message="Server starting" />
            <ServerAction name="Serve Request" service="data" />
            <Wait name="Server Wait" duration="1.0" />
        </Sequence>
    </BehaviorTree>   

    
</BehaviorForest>'''


def register_custom_nodes():
    """Register custom node types"""
    register_node("ClientAction", ClientAction)
    register_node("ServerAction", ServerAction)


async def main():
    """Main function"""
    print("=== Request-Response Communication Example ===\n")
    
    register_custom_nodes()
    
    xml_config = create_reqresp_xml()
    
    forest = BehaviorForest()
    forest.load_from_string(xml_config)
    
    await forest.start()
    await asyncio.sleep(0.05)
    await forest.stop()


if __name__ == "__main__":
    asyncio.run(main()) 