#!/usr/bin/env python3
"""
External Communication XML Example - Simplified version

This example shows how to use CommPubExternal and CommSubExternal nodes in XML configuration
to communicate with external systems through the behavior forest.
"""

import asyncio
from abtree import BehaviorForest, load_tree_from_string

async def external_publisher_callback(publish_info):
    print(f"🔗 External system received: {publish_info}")

async def main():
    # XML configuration for external communication
    xml_config = """
    <BehaviorForest name="ExternalCommForest">
        <BehaviorTree name="PubTree">
            <CommPubExternal name="PublishSensorData" topic="sensor_data" data="Hello, World!"/>
        </BehaviorTree>
        
        <BehaviorTree name="SubTree">
            <CommSubExternal name="SubscribeCommands" topic="commands" timeout="3.0"/>
        </BehaviorTree>
    </BehaviorForest>
    """
    
    # Load forest from XML
    forest = load_tree_from_string(xml_config)
    
    # Register external communication callbacks
    forest.register_external_publisher("sensor_data", external_publisher_callback)
    
    await forest.start()    

    # Simulate external system pushing data through forest.sub_external
    print("📡 External system is pushing data...")
    await forest.sub_external("commands", {"action": "move", "direction": "forward"}, "external_system")
    print("✅ External data has been pushed to forest")

    await asyncio.sleep(1)
    
    await forest.stop()

if __name__ == "__main__":
    asyncio.run(main()) 