#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 17: Robot Control - XML Configuration Version

This is the XML configuration version of the Robot Control example.
It demonstrates how to configure robotic control systems using XML.

Key Learning Points:
    - How to define robot control using XML
    - How to configure sensor data processing
    - How to implement motion control with XML
    - Understanding battery management in XML
"""

import asyncio
import math
import random
import time
from dataclasses import dataclass
from typing import List
from abtree import (
    BehaviorTree, Sequence, Selector, Action, Condition, Status,
    register_node, Blackboard
)


@dataclass
class Position:
    """Position class"""
    x: float
    y: float
    
    def distance_to(self, other: 'Position') -> float:
        """Calculate distance to another position"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


class RobotController:
    """Simple robot controller"""
    
    def __init__(self, name):
        self.name = name
        self.position = Position(0, 0)
        self.target_position = Position(0, 0)
        self.speed = 1.0
        self.battery_level = 100.0
        self.obstacles = []
        self.tasks = []
    
    def set_target(self, x: float, y: float):
        """Set target position"""
        self.target_position = Position(x, y)
        print(f"Robot {self.name}: Set target ({x}, {y})")
    
    def move_towards_target(self, delta_time: float):
        """Move towards target"""
        if self.position.distance_to(self.target_position) < 0.1:
            return True
        
        dx = self.target_position.x - self.position.x
        dy = self.target_position.y - self.position.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            dx /= distance
            dy /= distance
            move_distance = self.speed * delta_time
            
            self.position.x += dx * move_distance
            self.position.y += dy * move_distance
            
            self.battery_level -= 0.1 * delta_time
            self.battery_level = max(0, self.battery_level)
            
            print(f"Robot {self.name}: Moving to ({self.position.x:.2f}, {self.position.y:.2f})")
        
        return False
    
    def get_sensor_data(self):
        """Get sensor data"""
        return {
            'battery_level': self.battery_level,
            'obstacle_distance': self.get_nearest_obstacle_distance(),
            'temperature': random.uniform(20, 30),
            'position': {'x': self.position.x, 'y': self.position.y}
        }
    
    def get_nearest_obstacle_distance(self) -> float:
        """Get nearest obstacle distance"""
        if not self.obstacles:
            return float('inf')
        
        min_distance = float('inf')
        for obstacle in self.obstacles:
            distance = self.position.distance_to(obstacle)
            min_distance = min(min_distance, distance)
        
        return min_distance
    
    def add_obstacle(self, x: float, y: float):
        """Add obstacle"""
        self.obstacles.append(Position(x, y))
        print(f"Robot {self.name}: Added obstacle at ({x}, {y})")
    
    def add_task(self, task_name: str, target_x: float, target_y: float):
        """Add task"""
        self.tasks.append({
            'name': task_name,
            'target': Position(target_x, target_y),
            'completed': False
        })
        print(f"Robot {self.name}: Added task '{task_name}' at ({target_x}, {target_y})")


class SensorDataAction(Action):
    """Sensor data processing action"""
    
    def __init__(self, name, robot_controller=None, **kwargs):
        self.name = name
        self.robot_controller = robot_controller
    
    async def execute(self):
        if self.robot_controller is None:
            self.robot_controller = self.blackboard.get("robot_controller")
        
        if self.robot_controller is None:
            print(f"Error: Robot controller not found")
            return Status.FAILURE
        
        # Get sensor data
        sensor_data = self.robot_controller.get_sensor_data()
        
        # Update blackboard data
        self.blackboard.set("sensor_data", sensor_data)
        self.blackboard.set("battery_level", sensor_data['battery_level'])
        self.blackboard.set("obstacle_distance", sensor_data['obstacle_distance'])
        self.blackboard.set("temperature", sensor_data['temperature'])
        self.blackboard.set("position", sensor_data['position'])
        
        print(f"Processing sensor data: {self.name}")
        print(f"  Battery level: {sensor_data['battery_level']:.1f}%")
        print(f"  Obstacle distance: {sensor_data['obstacle_distance']:.2f}m")
        print(f"  Temperature: {sensor_data['temperature']:.1f}°C")
        print(f"  Position: ({sensor_data['position']['x']:.2f}, {sensor_data['position']['y']:.2f})")
        
        await asyncio.sleep(0.01)
        return Status.SUCCESS


class BatteryCheckCondition(Condition):
    """Battery level check condition"""
    
    def __init__(self, name, threshold=20.0, robot_controller=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.threshold = threshold
        self.robot_controller = robot_controller
    
    async def evaluate(self):
        if self.robot_controller is None:
            self.robot_controller = self.blackboard.get("robot_controller")
        
        if self.robot_controller is None:
            return False
        
        battery_level = self.robot_controller.battery_level
        needs_charging = battery_level < self.threshold
        
        print(f"Battery check {self.name}: {battery_level:.1f}% (threshold: {self.threshold}%, needs charging: {needs_charging})")
        return needs_charging


class ObstacleCheckCondition(Condition):
    """Obstacle detection condition"""
    
    def __init__(self, name, safe_distance=2.0, robot_controller=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.safe_distance = safe_distance
        self.robot_controller = robot_controller
    
    async def evaluate(self):
        if self.robot_controller is None:
            self.robot_controller = self.blackboard.get("robot_controller")
        
        if self.robot_controller is None:
            return False
        
        obstacle_distance = self.robot_controller.get_nearest_obstacle_distance()
        obstacle_detected = obstacle_distance < self.safe_distance
        
        print(f"Obstacle check {self.name}: distance={obstacle_distance:.2f}m (safe distance: {self.safe_distance}m, detected: {obstacle_detected})")
        return obstacle_detected


class MovementAction(Action):
    """Robot movement action"""
    
    def __init__(self, name, robot_controller=None, **kwargs):
        self.name = name
        self.robot_controller = robot_controller
    
    async def execute(self):
        if self.robot_controller is None:
            self.robot_controller = self.blackboard.get("robot_controller")
        
        if self.robot_controller is None:
            print(f"Error: Robot controller not found")
            return Status.FAILURE
        
        print(f"Executing movement action: {self.name}")
        
        # Simulate movement process
        delta_time = 0.5
        target_reached = self.robot_controller.move_towards_target(delta_time)
        
        if target_reached:
            print(f"✅ Target position reached")
            self.blackboard.set("target_reached", True)
            return Status.SUCCESS
        else:
            print(f"🔄 Moving...")
            return Status.RUNNING


class BatteryChargingAction(Action):
    """Battery charging action"""
    
    def __init__(self, name, robot_controller=None, **kwargs):
        self.name = name
        self.robot_controller = robot_controller
    
    async def execute(self):
        if self.robot_controller is None:
            self.robot_controller = self.blackboard.get("robot_controller")
        
        if self.robot_controller is None:
            print(f"Error: Robot controller not found")
            return Status.FAILURE
        
        print(f"Executing charging action: {self.name}")
        
        # Simulate charging process
        charging_time = 2.0
        print(f"🔋 Starting charging...")
        
        for i in range(4):
            await asyncio.sleep(charging_time / 4)
            self.robot_controller.battery_level = min(100.0, self.robot_controller.battery_level + 20.0)
            print(f"  Charging progress: {self.robot_controller.battery_level:.1f}%")
        
        print(f"✅ Charging complete")
        self.blackboard.set("charging_complete", True)
        return Status.SUCCESS


class TaskSchedulingAction(Action):
    """Task scheduling action"""
    
    def __init__(self, name, robot_controller=None, **kwargs):
        self.name = name
        self.robot_controller = robot_controller
    
    async def execute(self):
        if self.robot_controller is None:
            self.robot_controller = self.blackboard.get("robot_controller")
        
        if self.robot_controller is None:
            print(f"Error: Robot controller not found")
            return Status.FAILURE
        
        print(f"Executing task scheduling: {self.name}")
        
        # Check if there are pending tasks
        if not self.robot_controller.tasks:
            print("  No pending tasks")
            return Status.SUCCESS
        
        # Find the first uncompleted task
        for task in self.robot_controller.tasks:
            if not task['completed']:
                print(f"  Executing task: {task['name']}")
                
                # Set target position
                self.robot_controller.set_target(task['target'].x, task['target'].y)
                
                # Simulate task execution
                await asyncio.sleep(0.01)
                
                # Mark task as completed
                task['completed'] = True
                print(f"  ✅ Task completed: {task['name']}")
                break
        
        self.blackboard.set("task_scheduled", True)
        return Status.SUCCESS


class ObstacleAvoidanceAction(Action):
    """Obstacle avoidance action"""
    
    def __init__(self, name, robot_controller=None, **kwargs):
        self.name = name
        self.robot_controller = robot_controller
    
    async def execute(self, blackboard):
        if self.robot_controller is None:
            self.robot_controller = blackboard.get("robot_controller")
        
        if self.robot_controller is None:
            print(f"Error: Robot controller not found")
            return Status.FAILURE
        
        print(f"Executing obstacle avoidance: {self.name}")
        
        # Simulate obstacle avoidance process
        print("  🚧 Obstacle detected, executing avoidance strategy...")
        await asyncio.sleep(0.01)
        
        # Simple avoidance strategy: turn right 90 degrees
        print("  🔄 Turning right 90 degrees")
        await asyncio.sleep(0.01)
        
        print("  ✅ Obstacle avoidance complete")
        blackboard.set("obstacle_avoided", True)
        return Status.SUCCESS


def register_custom_nodes():
    """Register custom node types"""
    register_node("SensorDataAction", SensorDataAction)
    register_node("BatteryCheckCondition", BatteryCheckCondition)
    register_node("ObstacleCheckCondition", ObstacleCheckCondition)
    register_node("MovementAction", MovementAction)
    register_node("BatteryChargingAction", BatteryChargingAction)
    register_node("TaskSchedulingAction", TaskSchedulingAction)
    register_node("ObstacleAvoidanceAction", ObstacleAvoidanceAction)


async def main():
    """Main function - Demonstrate XML-based robot control configuration"""
    
    print("=== ABTree Robot Control XML Configuration Example ===\n")
    
    # Register custom node types
    register_custom_nodes()
    
    # Create robot controller
    robot = RobotController("Robot_01")
    
    # Add some obstacles
    robot.add_obstacle(3, 2)
    robot.add_obstacle(5, 4)
    robot.add_obstacle(1, 6)
    
    # Add some tasks
    robot.add_task("Patrol Task 1", 10, 5)
    robot.add_task("Patrol Task 2", 15, 10)
    robot.add_task("Return to Base", 0, 0)
    
    # Create blackboard
    blackboard = Blackboard()
    blackboard.set("robot_controller", robot)
    blackboard.set("target_reached", False)
    blackboard.set("charging_complete", False)
    blackboard.set("task_scheduled", False)
    blackboard.set("obstacle_avoided", False)
    
    # Create behavior tree
    tree = BehaviorTree()
    
    # Define XML configuration string
    xml_config = '''
    <BehaviorTree name="RobotControlXML" description="Robot control with XML configuration">
        <Selector name="Robot Control Root">
            <!-- Battery management (highest priority) -->
            <Sequence name="Battery Management">
                <BatteryCheckCondition name="Check Battery Level" threshold="20.0" />
                <BatteryChargingAction name="Charge Battery" />
            </Sequence>
            
            <!-- Obstacle avoidance -->
            <Sequence name="Obstacle Avoidance">
                <ObstacleCheckCondition name="Check Obstacles" safe_distance="2.0" />
                <ObstacleAvoidanceAction name="Avoid Obstacles" />
            </Sequence>
            
            <!-- Task execution -->
            <Sequence name="Task Execution">
                <TaskSchedulingAction name="Schedule Tasks" />
                <MovementAction name="Move to Target" />
            </Sequence>
            
            <!-- Sensor monitoring -->
            <Sequence name="Sensor Monitoring">
                <SensorDataAction name="Process Sensor Data" />
            </Sequence>
        </Selector>
    </BehaviorTree>
    '''
    
    # Load XML configuration
    tree.load_from_string(xml_config)
    
    print("Robot control behavior tree configured:")
    print("  - Battery management: Monitor battery level and charge")
    print("  - Obstacle avoidance: Detect and avoid obstacles")
    print("  - Task execution: Schedule and execute tasks")
    print("  - Sensor monitoring: Process sensor data")
    
    # Execute behavior tree
    print("\n=== Starting robot control execution ===")
    
    for i in range(20):
        print(f"\n--- Execution round {i+1} ---")
        
        # Simulate some random events
        if i == 5:  # Round 6: Lower battery level
            robot.battery_level = 15.0
            print("⚠️ Low battery level!")
        elif i == 10:  # Round 11: Add new obstacle
            robot.add_obstacle(8, 3)
            print("🚧 New obstacle detected!")
        
        # Execute behavior tree
        result = await tree.tick()
        print(f"Execution result: {result}")
        
        # Display current status
        sensor_data = robot.get_sensor_data()
        print(f"Current status: Battery={sensor_data['battery_level']:.1f}%, Position=({sensor_data['position']['x']:.2f}, {sensor_data['position']['y']:.2f})")
        
        await asyncio.sleep(0.01)
    
    print("\nRobot control execution complete!")


if __name__ == "__main__":
    asyncio.run(main()) 