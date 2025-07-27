#!/usr/bin/env python3
"""
External Communication XML Example - ExternalIO Mode

This example shows how to use CommExternalInput and CommExternalOutput nodes in XML configuration
to communicate with external systems through the behavior forest using the new ExternalIO pattern.
"""

import asyncio
from abtree import BehaviorForest, load_tree_from_string

async def external_input_handler(input_info):
    print(f"🔗 External input received: {input_info}")

async def external_output_handler(output_info):
    print(f"🔗 External output sent: {output_info}")

async def main():
    # XML configuration for external communication using ExternalIO pattern
    xml_config = """
    <BehaviorForest name="ExternalIOForest">
        <BehaviorTree name="InputTree">
            <CommExternalInput name="ProcessSensorData" channel="sensor_data" timeout="3.0"/>
        </BehaviorTree>
        
        <BehaviorTree name="OutputTree">
            <CommExternalOutput name="SendCommands" channel="command_data" data="Hello, External World!"/>
        </BehaviorTree>
        

    </BehaviorForest>
    """
    
    # Load forest from XML
    forest = load_tree_from_string(xml_config)
    
    # Register external IO handlers
    forest.on_input("sensor_data", external_input_handler)
    forest.on_output("command_data", external_output_handler)
    
    await forest.start()

    # Simulate external system sending input data
    print("📡 External system is sending input data...")
    await forest.input("sensor_data", {"temperature": 25.5, "humidity": 60.0}, "sensor_system")
    print("✅ External input data has been processed")

    # Simulate external system receiving output data
    print("📡 External system is receiving output data...")
    await forest.output("command_data", {"action": "move", "direction": "forward"}, "control_system")
    print("✅ External output data has been sent")

    await asyncio.sleep(1)
    
    # Get external IO statistics
    io_stats = forest.get_external_io_stats()
    print(f"📊 External IO Statistics: {io_stats}")
    
    await forest.stop()

if __name__ == "__main__":
    asyncio.run(main()) 