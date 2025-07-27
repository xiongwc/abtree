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
    CommPublisher, CommSubscriber,
    BehaviorForest, register_node,
    logger
)

def create_pubsub_xml() -> str:
    """Create XML configuration for PubSub communication"""
    return '''
<BehaviorForest name="PubSubForest" description="PubSub Communication Example">
    
    <BehaviorTree name="Subscriber" description="Subscriber Service">
        <Sequence name="Subscriber Behavior">            
            <CommSubscriber name="Subscribe Event" topic="news" message="{message}"/>
            <Log message="{message}" />
        </Sequence>
    </BehaviorTree>
    
    <BehaviorTree name="Publisher" description="Publisher Service">
        <Sequence name="Publisher Behavior">
            <CommPublisher name="Publish Event" topic="news" message="Hello world!" />            
        </Sequence>
    </BehaviorTree>   

    
</BehaviorForest>'''


def register_custom_nodes():
    """Register custom node types"""
    register_node("CommPublisher", CommPublisher)
    register_node("CommSubscriber", CommSubscriber)

async def main():
    """Main function"""
    print("=== PubSub Communication Example ===\n")    

    # Use new logger approach
    logger.info("Starting PubSub communication example")
    
    register_custom_nodes()
    
    xml_config = create_pubsub_xml()
    forest = BehaviorForest()
    forest.load_from_string(xml_config)
    
    logger.info("🚀 Starting PubSub communication...")
    await forest.start()
    
    # Wait longer to see the event communication
    await asyncio.sleep(2.0)
    
    logger.info("🛑 Stopping PubSub communication...")
    await forest.stop()

    logger.info("PubSub communication example completed")

if __name__ == "__main__":
    asyncio.run(main()) 