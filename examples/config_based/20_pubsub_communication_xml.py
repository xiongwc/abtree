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
from abtree.engine.event_system import EventSystem


class PublisherAction(Action):
    """Simple publisher action that emits events"""
    
    def __init__(self, name: str, topic: str, message: str):
        super().__init__(name)
        self.topic = topic
        self.message = message
    
    async def execute(self, blackboard):
        # Get event system from blackboard
        event_system = blackboard.get("__event_system")
        if event_system:
            # Emit event with topic and message data
            await event_system.emit(f"topic_{self.topic}", source=self.name, data=self.message)
            print(f"📤 Publishing to {self.topic}: {self.message}")
            print(f"   Event emitted: topic_{self.topic}")
        else:
            print(f"⚠️  No event system found in blackboard")
        return Status.SUCCESS


class SubscriberAction(Action):
    """Simple subscriber action that waits for events"""
    
    def __init__(self, name: str, topic: str):
        super().__init__(name)
        self.topic = topic
    
    async def execute(self, blackboard):
        # Get event system from blackboard
        event_system = blackboard.get("__event_system")
        if event_system:
            print(f"📥 Subscribing to {self.topic}")
            print(f"   Waiting for event: topic_{self.topic}")
            
            # Wait for the event with timeout
            event_triggered = await event_system.wait_for(f"topic_{self.topic}", timeout=2.0)
            if event_triggered:
                # Get event info from the event system
                event_info = event_system.get_event_info(f"topic_{self.topic}")
                source = event_info.source if event_info else "unknown"
                message = event_info.data if event_info and event_info.data else "No message data"
                
                print(f"✅ Event received: topic_{self.topic} from {source}")
                print(f"   📨 Message: {message}")
            else:
                print(f"⏰ Timeout waiting for event: topic_{self.topic}")
        else:
            print(f"⚠️  No event system found in blackboard")
        return Status.SUCCESS


def create_pubsub_xml() -> str:
    """Create XML configuration for PubSub communication"""
    return '''
<BehaviorForest name="PubSubForest" description="PubSub Communication Example">
    
    <BehaviorTree name="Subscriber" description="Subscriber Service">
        <Sequence name="Subscriber Behavior">
            <Log message="Subscriber starting" />
            <SubscriberAction name="Subscribe Event" topic="news" />
            <Wait name="Subscriber Wait" duration="0.1" />
        </Sequence>
    </BehaviorTree>
    
    <BehaviorTree name="Publisher" description="Publisher Service">
        <Sequence name="Publisher Behavior">
            <Log message="Publisher starting" />
            <Wait name="Publisher Delay" duration="0.1" />
            <PublisherAction name="Publish Event" topic="news" message="Hello World" />
            <Wait name="Publisher Wait" duration="0.1" />
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
    
    print("🚀 Starting PubSub communication...")
    await forest.start()
    
    # Wait longer to see the event communication
    await asyncio.sleep(2.0)
    
    print("\n🛑 Stopping PubSub communication...")
    await forest.stop()

    from loguru import logger
    logger.info("PubSub Communication Example")

if __name__ == "__main__":
    asyncio.run(main()) 