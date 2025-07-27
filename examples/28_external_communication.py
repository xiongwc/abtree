#!/usr/bin/env python3
"""
External Communication Example - Simplified version

This example shows how to use CommPublisher and CommSubscriber nodes to communicate
with external systems through the behavior forest.
"""

import asyncio
from abtree import (
    BehaviorForest,
    CommPublisher,
    CommSubscriber,
    create_tree,
)

async def external_publisher_callback(publish_info):
    print(f"🔗 External system received: {publish_info}")

async def external_subscriber_callback(subscription_info):
    print(f"🔗 External system pushed: {subscription_info}")

async def main():
    # Create behavior forest
    forest = BehaviorForest(name="ExternalCommForest")
    
    # Register external communication callbacks
    forest.register_publisher("sensor_data", external_publisher_callback)
    forest.register_subscriber("commands", external_subscriber_callback)
    
    # Create publisher behavior tree
    publisher_tree = create_tree(
        name="PubTree",
        root=CommPublisher(
            name="PublishSensorData"
        )
    )
    
    # Create subscriber behavior tree
    subscriber_tree = create_tree(
        name="SubTree",
        root=CommSubscriber(
            name="SubscribeCommands"
        )
    )
    
    # Add trees to forest
    from abtree.forest.core import ForestNode, ForestNodeType
    forest.add_node(ForestNode(name="PubNode", tree=publisher_tree, node_type=ForestNodeType.WORKER))
    forest.add_node(ForestNode(name="SubNode", tree=subscriber_tree, node_type=ForestNodeType.WORKER))
    
    # Start the forest
    await forest.start()
    
    # Simulate external data injection
    await forest.subscribe_external("commands", {"action": "move", "direction": "forward"})
    
    # Run one tick
    results = await forest.tick()
    print("Tick results:", results)
    
    # Stop the forest
    await forest.stop()

if __name__ == "__main__":
    asyncio.run(main()) 