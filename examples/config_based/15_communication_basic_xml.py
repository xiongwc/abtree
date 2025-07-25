#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 15: Communication Basic - XML Configuration Version

Simple example demonstrating event communication within a single behavior tree using XML configuration.
"""

import asyncio
from abtree import (
    BehaviorTree, Blackboard, Status,
    Action, Log, Wait, register_node
)
from abtree.engine.event import EventDispatcher


class PublisherAction(Action):
    """Simple publisher action that emits events"""
    
    def __init__(self, name: str, topic: str, message: str):
        super().__init__(name)
        self.topic = topic
        self.message = message
    
    async def execute(self, blackboard):
        # Get event dispatcher from blackboard
        event_dispatcher = blackboard.get("__event_dispatcher") if blackboard else self.get_event_dispatcher()
        if event_dispatcher:
            # Emit event with topic and message
            await event_dispatcher.emit(f"topic_{self.topic}", source=self.name, data=self.message)
            print(f"📤 Publishing to {self.topic}: {self.message}")
            print(f"   Event emitted: topic_{self.topic}")
        else:
            print(f"⚠️  No event dispatcher found in blackboard")
        return Status.SUCCESS


class SubscriberAction(Action):
    """Simple subscriber action that waits for events"""
    
    def __init__(self, name: str, topic: str):
        super().__init__(name)
        self.topic = topic
    
    async def execute(self, blackboard):
        # Get event dispatcher from blackboard
        event_dispatcher = blackboard.get("__event_dispatcher") if blackboard else self.get_event_dispatcher()
        if event_dispatcher:
            print(f"📥 Subscribing to {self.topic}")
            print(f"   Waiting for event: topic_{self.topic}")
            
            # Wait for the event with timeout
            event_triggered = await event_dispatcher.wait_for(f"topic_{self.topic}", timeout=2.0)
            if event_triggered:
                print(f"✅ Event received: topic_{self.topic}")
            else:
                print(f"⏰ Timeout waiting for event: topic_{self.topic}")
        else:
            print(f"⚠️  No event dispatcher found in blackboard")
        return Status.SUCCESS


def register_custom_nodes():
    """Register custom node types"""
    register_node("PublisherAction", PublisherAction)
    register_node("SubscriberAction", SubscriberAction)


async def main():
    """Main function"""
    print("=== Communication Basic Test (XML) ===\n")
    
    register_custom_nodes()
    
    # Create behavior tree with shared event dispatcher
    blackboard = Blackboard()
    event_dispatcher = EventDispatcher()
    blackboard.set("__event_dispatcher", event_dispatcher)
    
    tree = BehaviorTree(
        blackboard=blackboard,
        event_dispatcher=event_dispatcher,
        name="EventTestTree"
    )
    
    # XML configuration for event dispatcher test
    xml_config = '''
    <BehaviorTree name="EventTestTree">
        <Sequence name="Event Test Sequence">
            <SubscriberAction name="Subscribe Event" topic="news" />
            <PublisherAction name="Publish Event" topic="news" message="Hello World" />
        </Sequence>
    </BehaviorTree>
    '''
    
    # Load tree from XML
    tree.load_from_string(xml_config)
    
    print("🚀 Starting event dispatcher test (XML)...")
    await tree.start()
    
    # Wait for the sequence to complete
    await asyncio.sleep(3.0)
    
    print("\n🛑 Stopping event dispatcher test...")
    await tree.stop()

    print("✅ event dispatcher test completed!")


if __name__ == "__main__":
    asyncio.run(main()) 