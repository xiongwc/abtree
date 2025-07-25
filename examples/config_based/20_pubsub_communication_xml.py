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
from abtree.engine.event import EventDispatcher


class CommPublisher(Action):
    """publisher action that emits events"""
    
    def __init__(self, name: str):
        super().__init__(name)
    
    async def execute(self,topic:str,message: any):
        event_dispatcher = self.get_event_dispatcher()
        if event_dispatcher:
            await event_dispatcher.emit(f"topic_{topic}", source=self.name, data=message)
        else:
            print(f"⚠️  No event dispatcher found in blackboard")
        return Status.SUCCESS


class SubscriberAction(Action):
    """subscriber action that waits for events"""
    
    def __init__(self, name: str):
        super().__init__(name)    
    async def execute(self,topic:str,message: any):
        event_dispatcher = self.get_event_dispatcher()
        if event_dispatcher:            
            event_triggered = await event_dispatcher.wait_for(f"topic_{topic}", timeout=2.0)
            if event_triggered:
                event_info = event_dispatcher.get_event_info(f"topic_{topic}")
                received_message = event_info.data if event_info and event_info.data else "No message data"
                message = received_message  # Automatically sync to blackboard
                self.setPort("message", message)
                print(f"✅ Received message: {message}")
            else:
                print(f"⏰ Timeout waiting for event: topic_{topic}")
        else:
            print(f"⚠️  No event dispatcher found in blackboard")
        return Status.SUCCESS


def create_pubsub_xml() -> str:
    """Create XML configuration for PubSub communication"""
    return '''
<BehaviorForest name="PubSubForest" description="PubSub Communication Example">
    
    <BehaviorTree name="Subscriber" description="Subscriber Service">
        <Sequence name="Subscriber Behavior">            
            <SubscriberAction name="Subscribe Event" topic="news" message="{message}"/>
            <Log message="{message}" />
        </Sequence>
    </BehaviorTree>
    
    <BehaviorTree name="Publisher" description="Publisher Service">
        <Sequence name="Publisher Behavior">
            <CommPublisher name="Publish Event" topic="news" message="hello world" />            
        </Sequence>
    </BehaviorTree>
    
    <Communication>
        <CommTopic name="news">
            <CommPublisher service="Publisher" />
            <CommSubscriber service="Subscriber" />
        </CommTopic>
    </Communication>
    
</BehaviorForest>'''


def register_custom_nodes():
    """Register custom node types"""
    register_node("CommPublisher", CommPublisher)
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