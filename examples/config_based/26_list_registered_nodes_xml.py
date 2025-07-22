#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 26: List Registered Nodes - XML Configuration Version

This is the XML configuration version of the List Registered Nodes example.
It demonstrates how to view and inspect registered node types using XML configuration.

Key Learning Points:
    - How to get all registered node types
    - How to check if a specific node type is registered
    - How to get node metadata and statistics
    - How to inspect node class information
    - Understanding the node registration system with XML
"""

import asyncio
from abtree import (
    BehaviorTree, 
    Action, 
    register_node, 
    get_registered_nodes,
    get_global_registry,
    get_builtin_nodes,
    get_custom_nodes,
    unregister_node,
    get_node_class,
    is_node_registered
)
from abtree.core import Status


class CustomAction(Action):
    """A custom action node for demonstration"""
    
    async def execute(self, blackboard):
        print(f"Custom action '{self.name}' executed")
        return Status.SUCCESS


class AnotherCustomAction(Action):
    """Another custom action node for demonstration"""
    
    async def execute(self, blackboard):
        print(f"Another custom action '{self.name}' executed")
        return Status.SUCCESS


def print_node_info(node_type: str, registry):
    """Print detailed information about a node type"""
    print(f"\n--- {node_type} ---")
    
    # Check if registered
    is_registered = registry.is_registered(node_type)
    print(f"Registered: {is_registered}")
    
    if is_registered:
        # Get metadata
        metadata = registry.get_metadata(node_type)
        if metadata:
            print(f"Class Name: {metadata.get('class_name', 'N/A')}")
            print(f"Module: {metadata.get('module', 'N/A')}")
            print(f"Description: {metadata.get('description', 'No description')}")
        
        # Get node class
        node_class = registry.get_node_class(node_type)
        if node_class:
            print(f"Class: {node_class}")
            print(f"Base Classes: {[base.__name__ for base in node_class.__mro__]}")


def print_registry_stats(registry):
    """Print registry statistics"""
    stats = registry.get_stats()
    print(f"\n=== Registry Statistics ===")
    print(f"Total Registered Nodes: {stats['total_registered']}")
    print(f"Has Metadata: {stats['has_metadata']}")
    print(f"Registered Types: {stats['registered_types']}")


async def main():
    """Main function - demonstrate node registry inspection with XML"""
    
    print("=== ABTree List Registered Nodes XML Configuration Example ===\n")
    
    # Get the global registry
    registry = get_global_registry()
    
    print("1. Initial Registry State")
    print("=" * 50)
    print_registry_stats(registry)
    
    # Show all initially registered nodes
    print("\n2. Initially Registered Node Types")
    print("=" * 50)
    initial_nodes = get_registered_nodes()
    print(f"Found {len(initial_nodes)} registered node types:")
    for i, node_type in enumerate(sorted(initial_nodes), 1):
        print(f"  {i:2d}. {node_type}")
    
    # Register custom nodes for XML usage
    print("\n3. Registering Custom Nodes for XML Configuration")
    print("=" * 50)
    register_node("CustomAction", CustomAction, metadata={
        "description": "A custom action node for demonstration",
        "author": "Example Author",
        "version": "1.0.0"
    })
    register_node("AnotherCustomAction", AnotherCustomAction, metadata={
        "description": "Another custom action node for demonstration",
        "author": "Example Author",
        "version": "1.0.0"
    })
    print("Registered 2 custom nodes: CustomAction, AnotherCustomAction")
    
    # Show updated registry
    print("\n4. Updated Registry State")
    print("=" * 50)
    print_registry_stats(registry)
    
    # Show all registered nodes after custom registration
    print("\n5. All Registered Node Types (After Custom Registration)")
    print("=" * 50)
    all_nodes = get_registered_nodes()
    print(f"Found {len(all_nodes)} registered node types:")
    
    # Use new functions to get built-in and custom nodes
    builtin_nodes = get_builtin_nodes()
    custom_nodes = get_custom_nodes()
    
    print("\nBuilt-in Nodes:")
    for i, node_type in enumerate(sorted(builtin_nodes), 1):
        print(f"  {i:2d}. {node_type}")
    
    print("\nCustom Nodes:")
    for i, node_type in enumerate(sorted(custom_nodes), 1):
        print(f"  {i:2d}. {node_type}")
    
    # Show detailed info for custom nodes
    print("\n6. Custom Node Information")
    print("=" * 50)
    for node_type in custom_nodes:
        print_node_info(node_type, registry)
    
    # Demonstrate XML configuration with registered nodes
    print("\n7. XML Configuration with Registered Nodes")
    print("=" * 50)
    
    # XML string that uses both built-in and custom nodes
    xml_config = '''
    <BehaviorTree name="RegistryDemo" description="Demonstrate registered nodes in XML">
        <Sequence name="RootSequence">
            <Log name="StartLog" message="Starting registry demo" />
            <CustomAction name="CustomAction1" />
            <Wait name="Wait1" duration="0.1" />
            <AnotherCustomAction name="CustomAction2" />
            <Log name="EndLog" message="Registry demo completed" />
        </Sequence>
    </BehaviorTree>
    '''
    
    print("XML Configuration:")
    print(xml_config.strip())
    
    # Parse and execute XML configuration
    print("\n8. Executing XML Configuration")
    print("=" * 50)
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    
    print("Executing behavior tree configured by XML...")
    xml_result = await xml_tree.tick()
    print(f"XML configuration execution completed! Result: {xml_result}")
    
    # Demonstrate node creation from registry
    print("\n9. Node Creation from Registry")
    print("=" * 50)
    test_nodes = ["CustomAction", "AnotherCustomAction", "Sequence", "NonExistentNode"]
    
    for node_type in test_nodes:
        node = registry.create(node_type, name=f"test_{node_type}")
        if node:
            print(f"✓ Successfully created {node_type}: {type(node).__name__}")
        else:
            print(f"✗ Failed to create {node_type}: Not registered")
    
    # Show metadata for all nodes
    print("\n10. All Node Metadata")
    print("=" * 50)
    all_metadata = registry.get_all_metadata()
    for node_type, metadata in sorted(all_metadata.items()):
        print(f"\n{node_type}:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
    
    # Demonstrate checking specific nodes
    print("\n11. Node Registration Checks")
    print("=" * 50)
    test_checks = ["Sequence", "CustomAction", "NonExistentNode", "AnotherCustomAction"]
    
    for node_type in test_checks:
        is_registered = registry.is_registered(node_type)
        status = "✓ Registered" if is_registered else "✗ Not Registered"
        print(f"{node_type}: {status}")
    
    # Demonstrate node finding and unregistering
    print("\n12. Node Finding and Unregistering")
    print("=" * 50)
    
    # Test getting node classes
    test_nodes = ["Sequence", "CustomAction", "NonExistentNode"]
    for node_type in test_nodes:
        node_class = get_node_class(node_type)
        if node_class:
            print(f"✓ Found {node_type}: {node_class}")
        else:
            print(f"✗ Not found {node_type}")
    
    # Test unregistering a custom node
    print("\nUnregistering CustomAction...")
    if unregister_node("CustomAction"):
        print("✓ Successfully unregistered CustomAction")
        
        # Check if it's really unregistered
        if not is_node_registered("CustomAction"):
            print("✓ CustomAction is no longer registered")
        else:
            print("✗ CustomAction is still registered")
    else:
        print("✗ Failed to unregister CustomAction")
    
    # Show updated registry
    print("\nUpdated registry after unregistering:")
    updated_nodes = get_registered_nodes()
    print(f"Total registered nodes: {len(updated_nodes)}")
    print(f"Built-in nodes: {len(get_builtin_nodes())}")
    print(f"Custom nodes: {len(get_custom_nodes())}")
    
    print("\n=== Example Completed Successfully! ===")
    print("\nKey Takeaways:")
    print("- Use get_registered_nodes() to get all registered node types")
    print("- Use get_builtin_nodes() to get built-in node types")
    print("- Use get_custom_nodes() to get custom node types")
    print("- Use is_node_registered() to check if a node type exists")
    print("- Use get_node_class() to get node class by name")
    print("- Use unregister_node() to remove a node type")
    print("- Use registry.get_metadata() to get node information")
    print("- Use registry.create() to create node instances")
    print("- Custom nodes can be registered with metadata")
    print("- Registered nodes can be used in XML configurations")
    print("- XML parser automatically uses registered node types")


if __name__ == "__main__":
    asyncio.run(main()) 