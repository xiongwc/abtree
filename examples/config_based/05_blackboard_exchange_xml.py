#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 05: Blackboard Data Exchange - XML Configuration Version

Demonstrates {} parameter passing mechanism in XML configuration.
Shows how to exchange data between nodes through blackboard variables.
"""

import asyncio
from abtree import BehaviorTree, Action, Condition, register_node
from abtree.core import Status


class DataProducerAction(Action):
    """Data producer node - generates data and stores it in blackboard"""
    
    def __init__(self, name: str = ""):
        super().__init__(name)
    
    async def execute(self, output_port):
        print(f"🔧 {self.name} - Starting data generation...")
        print(f"   Received output port parameter: {output_port}")
        
        # Generate data and store in blackboard
        generated_data = 100
        self.setPort("output_port", generated_data)
        print(f"   ✅ Successfully generated data: {generated_data} and stored in blackboard")
        
        return Status.SUCCESS


class DataConsumerAction(Action):
    """Data consumer node - reads data from blackboard and processes it"""
    
    def __init__(self, name: str = ""):
        super().__init__(name)
    
    async def execute(self, input_port):
        print(f"📥 {self.name} - Starting data consumption...")
        print(f"   Received input port parameter: {input_port}")
        
        # Get data from blackboard
        received_data = self.getPort("input_port")
        print(f"   📊 Data retrieved from blackboard: {received_data}")
        
        # Simulate data processing
        processed_result = received_data * 2
        print(f"   🔄 Data processing result: {received_data} × 2 = {processed_result}")
        
        return Status.SUCCESS


def register_custom_nodes():
    """Register custom node types"""
    register_node("DataProducerAction", DataProducerAction)
    register_node("DataConsumerAction", DataConsumerAction)


async def main():
    """Demonstrate blackboard data exchange functionality"""
    
    print("🌳 Blackboard Data Exchange Demo")
    print("=" * 50)
    print("This example demonstrates how to pass data between different nodes")
    print("using blackboard variables with {} syntax in XML")
    print()
    
    # Register custom nodes
    register_custom_nodes()
    
    # XML configuration - using {} parameter substitution
    xml_config = '''
    <BehaviorTree name="DataExchangeDemo">
        <Sequence name="DataExchangeSequence">
            <DataProducerAction output_port="{shared_data}" />
            <DataConsumerAction input_port="{shared_data}" />
        </Sequence>
    </BehaviorTree>
    '''
    
    # Create and load behavior tree
    tree = BehaviorTree()
    tree.load_from_string(xml_config)
    
    print("🚀 Starting behavior tree execution...")
    print("-" * 30)
    
    # Execute behavior tree
    result = await tree.tick()
    
    print("-" * 30)
    print(f"🎯 Behavior tree execution completed, status: {result}")
    print("\n💡 Key Points:")
    print("   • DataProducerAction stores data in blackboard using setPort()")
    print("   • DataConsumerAction retrieves data from blackboard using getPort()")
    print("   • {shared_data} in XML automatically binds to corresponding ports")


if __name__ == "__main__":
    asyncio.run(main()) 