#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 20: PubSub Communication - XML Configuration

Minimal example demonstrating PubSub communication pattern using XML.
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


class PublisherAction(Action):
    """Simple publisher action"""
    
    def __init__(self, name: str, topic: str, message: str):
        self.name = name
        self.topic = topic
        self.message = message
    
    async def execute(self, blackboard):
        print(f"📤 Publishing to {self.topic}: {self.message}")
        return Status.SUCCESS


class SubscriberAction(Action):
    """Simple subscriber action"""
    
    def __init__(self, name: str, topic: str):
        self.name = name
        self.topic = topic
    
    async def execute(self, blackboard):
        print(f"📥 Subscribing to {self.topic}")
        return Status.SUCCESS


def create_pubsub_xml() -> str:
    """Create XML configuration for PubSub communication"""
    return '''
<BehaviorForest name="PubSubForest" description="PubSub Communication Example">
    
    <BehaviorTree name="Publisher" description="Publisher Service">
        <Sequence name="Publisher Behavior">
            <Log message="Publisher starting" />
            <PublisherAction name="Publish Event" topic="news" message="Hello World" />
            <Wait name="Publisher Wait" duration="1.0" />
        </Sequence>
    </BehaviorTree>
    
    <BehaviorTree name="Subscriber" description="Subscriber Service">
        <Sequence name="Subscriber Behavior">
            <Log message="Subscriber starting" />
            <SubscriberAction name="Subscribe Event" topic="news" />
            <Wait name="Subscriber Wait" duration="1.0" />
        </Sequence>
    </BehaviorTree>
    
    <Communication>
        <ComTopic name="news">
            <ComPublisher service="Publisher" />
            <ComSubscriber service="Subscriber" />
        </ComTopic>
    </Communication>
    
</BehaviorForest>'''


def register_custom_nodes():
    """Register custom node types"""
    register_node("PublisherAction", PublisherAction)
    register_node("SubscriberAction", SubscriberAction)


async def main():
    """Main function"""
    print("=== PubSub Communication Example ===\n")
    
    register_custom_nodes()
    
    xml_config = create_pubsub_xml()
    forest = BehaviorForest()
    forest.load_from_string(xml_config)
    
    await forest.start()
    await asyncio.sleep(0.05)
    await forest.stop()

    from loguru import logger
    logger.info("PubSub Communication Example")

if __name__ == "__main__":
    asyncio.run(main()) 