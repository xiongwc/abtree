#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ABTree Examples Test Script

Run all 16 learning examples to verify they all work properly.
"""

import asyncio
import importlib
import sys
import time
from pathlib import Path


async def run_example(example_name, example_number):
    """Run a single example"""
    try:
        print(f"\n{'='*60}")
        print(f"Running example {example_number:02d}: {example_name}")
        print(f"{'='*60}")
        
        # Import and run example
        module = importlib.import_module(f"examples.{example_name}")
        
        if hasattr(module, 'main'):
            start_time = time.time()
            await module.main()
            end_time = time.time()
            
            print(f"\n✅ Example {example_number:02d} ran successfully (Time: {end_time - start_time:.2f} seconds)")
            return True
        else:
            print(f"❌ Example {example_number:02d} missing main function")
            return False
            
    except Exception as e:
        print(f"❌ Example {example_number:02d} failed: {e}")
        return False


async def main():
    """Main function - run all examples"""
    
    print("🚀 ABTree Examples Test Started")
    print("=" * 60)
    
    # Define all examples
    examples = [
        ("01_hello_world", "Basic Workflow"),
        ("02_simple_sequence", "Node Types Detailed"),
        ("03_selector_basic", "Control Flow Patterns"),
        ("04_blackboard_basic", "Event System"),
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
        ("15_event_system", "Event System"),
        ("16_automation_testing", "Automation Testing"),
        ("17_robot_control", "Robot Control"),
        ("18_smart_home", "Smart Home System"),
        ("19_game_ai", "Game AI")
    ]
    
    # Run examples
    results = []
    total_examples = len(examples)
    successful_examples = 0
    
    for i, (module_name, description) in enumerate(examples, 1):
        success = await run_example(module_name, i)
        results.append((i, module_name, description, success))
        
        if success:
            successful_examples += 1
        
        # Add delay to avoid output confusion
        await asyncio.sleep(0.5)
    
    # Display result summary
    print(f"\n{'='*60}")
    print("📊 Test Result Summary")
    print(f"{'='*60}")
    
    print(f"Total examples: {total_examples}")
    print(f"Successfully run: {successful_examples}")
    print(f"Failed count: {total_examples - successful_examples}")
    print(f"Success rate: {successful_examples/total_examples*100:.1f}%")
    
    print(f"\nDetailed results:")
    for i, module_name, description, success in results:
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


if __name__ == "__main__":
    # Add examples directory to Python path
    examples_dir = Path(__file__).parent
    sys.path.insert(0, str(examples_dir.parent))
    
    # Run tests
    asyncio.run(main()) 