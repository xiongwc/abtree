#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ABTree Examples Test Script

Run all learning examples (both code-based and XML-based) to verify they all work properly.
Examples are organized in a logical learning progression from basic to advanced concepts.
"""

import asyncio
import importlib
import sys
import time
from pathlib import Path


async def run_example(example_name, example_number, is_xml=False):
    """Run a single example"""
    try:
        print(f"\n{'='*60}")
        prefix = "XML" if is_xml else "Code"
        print(f"Running {prefix} example {example_number:02d}: {example_name}")
        print(f"{'='*60}")
        
        # Import and run example
        if is_xml:
            module = importlib.import_module(f"examples.config_based.{example_name}")
        else:
            module = importlib.import_module(f"examples.{example_name}")
        
        if hasattr(module, 'main'):
            start_time = time.time()
            await module.main()
            end_time = time.time()
            
            print(f"\n✅ {prefix} example {example_number:02d} ran successfully (Time: {end_time - start_time:.2f} seconds)")
            return True
        else:
            print(f"❌ {prefix} example {example_number:02d} missing main function")
            return False
            
    except Exception as e:
        print(f"❌ {prefix} example {example_number:02d} failed: {e}")
        return False


async def main():
    """Main function - run all examples"""
    
    print("🚀 ABTree Examples Test Started")
    print("=" * 60)
    print("📚 Learning Progression:")
    print("  1-5:  Basic concepts (Hello World, Sequences, Selectors, Blackboard)")
    print("  6-10: Core node types (Conditions, Decorators, Composites, Control Flow)")
    print("  11-15: Advanced features (Forests, State Management, Communication)")
    print("  16-20: Real-world applications (Testing, Robotics, Smart Home, Game AI)")
    print("=" * 60)
    
    # Define all code-based examples in logical order
    code_examples = [
        ("01_hello_world", "Basic Workflow"),
        ("02_simple_sequence", "Node Types Detailed"),
        ("03_selector_basic", "Control Flow Patterns"),
        ("04_blackboard_basic", "event dispatcher"),
        ("05_action_nodes", "Blackboard Usage"),
        ("06_condition_nodes", "Async Operations"),
        ("07_decorator_nodes", "Error Handling"),
        ("08_composite_nodes", "Priority System"),
        ("09_control_flow_basic", "Dynamic Behavior"),
        ("10_control_flow_advanced", "Multi-Agent System"),
        ("11_behavior_forest", "Behavior Forest"),
        ("12_forest_manager", "Forest Manager"),
        ("13_advanced_forest_features", "Advanced Forest Features"),
        ("14_state_management", "State Management"),
        ("15_communication_basic", "Communication Basic"),
        ("16_automation_testing", "Automation Testing"),
        ("17_robot_control", "Robot Control"),
        ("18_smart_home", "Smart Home System"),
        ("19_game_ai", "Game AI"),
        ("20_list_registered_nodes", "List Registered Nodes")
    ]
    
    # Define all XML-based examples in logical order
    xml_examples = [
        ("01_hello_world_xml", "Basic Workflow (XML)"),
        ("02_simple_sequence_xml", "Node Types Detailed (XML)"),
        ("03_selector_basic_xml", "Control Flow Patterns (XML)"),
        ("04_blackboard_basic_xml", "event dispatcher (XML)"),
        ("05_blackboard_exchange_xml", "Blackboard Exchange (XML)"),
        ("06_action_nodes_xml", "Blackboard Usage (XML)"),
        ("07_condition_nodes_xml", "Async Operations (XML)"),
        ("08_composite_nodes_xml", "Priority System (XML)"),
        ("09_control_flow_basic_xml", "Dynamic Behavior (XML)"),
        ("10_control_flow_advanced_xml", "Multi-Agent System (XML)"),
        ("11_behavior_forest_xml", "Behavior Forest (XML)"),
        ("12_decorator_nodes_xml", "Decorator Nodes (XML)"),
        ("13_advanced_forest_features_xml", "Advanced Forest Features (XML)"),
        ("14_forest_manager_xml", "Forest Manager (XML)"),
        ("15_communication_basic_xml", "Communication Basic (XML)"),
        ("16_automation_testing_xml", "Automation Testing (XML)"),
        ("17_robot_control_xml", "Robot Control (XML)"),
        ("18_smart_home_xml", "Smart Home System (XML)"),
        ("19_game_ai_xml", "Game AI (XML)"),
        ("20_pubsub_communication_xml", "PubSub Communication (XML)"),
        ("21_reqresp_communication_xml", "Request-Response Communication (XML)"),
        ("22_shared_blackboard_xml", "Shared Blackboard Communication (XML)"),
        ("23_state_management_xml", "State Management (XML)"),
        ("24_behavior_call_xml", "Behavior Call Communication (XML)"),
        ("25_state_watching_xml", "State Watching Communication (XML)"),
        ("26_list_registered_nodes_xml", "List Registered Nodes (XML)"),
        ("27_task_board_xml", "Task Board Communication (XML)")
    ]
    
    # Run code-based examples
    print("\n📝 Running Code-based Examples...")
    code_results = []
    total_code_examples = len(code_examples)
    successful_code_examples = 0
    
    for i, (module_name, description) in enumerate(code_examples, 1):
        success = await run_example(module_name, i, is_xml=False)
        code_results.append((i, module_name, description, success))
        
        if success:
            successful_code_examples += 1
        
        # Add delay to avoid output confusion
        await asyncio.sleep(0.5)
    
    # Run XML-based examples
    print("\n📄 Running XML-based Examples...")
    xml_results = []
    total_xml_examples = len(xml_examples)
    successful_xml_examples = 0
    
    for i, (module_name, description) in enumerate(xml_examples, 1):
        success = await run_example(module_name, i, is_xml=True)
        xml_results.append((i, module_name, description, success))
        
        if success:
            successful_xml_examples += 1
        
        # Add delay to avoid output confusion
        await asyncio.sleep(0.5)
    
    # Calculate overall statistics
    total_examples = total_code_examples + total_xml_examples
    successful_examples = successful_code_examples + successful_xml_examples
    
    # Display result summary
    print(f"\n{'='*60}")
    print("📊 Test Result Summary")
    print(f"{'='*60}")
    
    print(f"Total examples: {total_examples}")
    print(f"  - Code-based examples: {total_code_examples}")
    print(f"  - XML-based examples: {total_xml_examples}")
    print(f"Successfully run: {successful_examples}")
    print(f"  - Code-based successful: {successful_code_examples}")
    print(f"  - XML-based successful: {successful_xml_examples}")
    print(f"Failed count: {total_examples - successful_examples}")
    print(f"Success rate: {successful_examples/total_examples*100:.1f}%")
    
    print(f"\n📝 Code-based examples results:")
    for i, module_name, description, success in code_results:
        status = "✅ Success" if success else "❌ Failed"
        print(f"  {i:02d}. {description} ({module_name}) - {status}")
    
    print(f"\n📄 XML-based examples results:")
    for i, module_name, description, success in xml_results:
        status = "✅ Success" if success else "❌ Failed"
        print(f"  {i:02d}. {description} ({module_name}) - {status}")
    
    if successful_examples == total_examples:
        print(f"\n🎉 All examples ran successfully!")
    else:
        print(f"\n⚠️  {total_examples - successful_examples} examples failed")
    
    print(f"\n💡 Tips:")
    print(f"  - Check failed examples for error messages")
    print(f"  - Ensure all dependencies are properly installed")
    print(f"  - Check Python version compatibility (requires 3.8+)")
    print(f"  - See examples/README.md for learning path")
    print(f"  - XML examples demonstrate configuration-based approach")
    print(f"  - Examples are organized in logical learning progression")


if __name__ == "__main__":
    # Add examples directory to Python path
    examples_dir = Path(__file__).parent
    sys.path.insert(0, str(examples_dir.parent))
    
    # Run tests
    asyncio.run(main()) 