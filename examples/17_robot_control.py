#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 17: Simplified Robotic Control System

Demonstrates a simplified robotic control system using ABTree, including:
- Sensor data processing
- Motion control
- Basic obstacle avoidance
- Battery management
- Task scheduling
- XML configuration loading
"""

import asyncio
import math
import random
import time
from dataclasses import dataclass
from typing import List
from abtree import BehaviorTree, Sequence, Selector, Action, Condition, register_node
from abtree.core import Status


def register_custom_nodes():
    """Register custom node types"""
    register_node("SensorDataAction", SensorDataAction)
    register_node("BatteryCheckCondition", BatteryCheckCondition)
    register_node("ObstacleCheckCondition", ObstacleCheckCondition)
    register_node("MovementAction", MovementAction)
    register_node("BatteryChargingAction", BatteryChargingAction)
    register_node("TaskSchedulingAction", TaskSchedulingAction)


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
        print(f"Robot {self.name}: Added obstacle ({x}, {y})")


class SensorDataAction(Action):
    """Sensor data processing action"""
    
    def __init__(self, name, robot_controller=None):
        super().__init__(name)
        self.robot_controller = robot_controller
    
    async def execute(self, blackboard):
        print(f"SensorDataAction {self.name}: Processing sensor data")
        
        # Get robot_controller from blackboard if not provided in constructor
        if self.robot_controller is None:
            self.robot_controller = blackboard.get("robot_controller")
            if self.robot_controller is None:
                print(f"SensorDataAction {self.name}: No robot_controller found in blackboard")
                return Status.FAILURE
        
        sensor_data = self.robot_controller.get_sensor_data()
        blackboard.set("sensor_data", sensor_data)
        
        await asyncio.sleep(0.01)
        return Status.SUCCESS


class BatteryCheckCondition(Condition):
    """Battery level check condition"""
    
    def __init__(self, name, threshold=20.0, robot_controller=None):
        super().__init__(name)
        self.threshold = threshold
        self.robot_controller = robot_controller
    
    async def evaluate(self, blackboard):
        # Get robot_controller from blackboard if not provided in constructor
        if self.robot_controller is None:
            self.robot_controller = blackboard.get("robot_controller")
            if self.robot_controller is None:
                print(f"BatteryCheckCondition {self.name}: No robot_controller found in blackboard")
                return False
        
        battery_level = self.robot_controller.battery_level
        print(f"BatteryCheckCondition {self.name}: Battery {battery_level:.1f}%, threshold {self.threshold}%")
        
        return battery_level <= self.threshold


class ObstacleCheckCondition(Condition):
    """Obstacle distance check condition"""
    
    def __init__(self, name, safe_distance=2.0, robot_controller=None):
        super().__init__(name)
        self.safe_distance = safe_distance
        self.robot_controller = robot_controller
    
    async def evaluate(self, blackboard):
        # Get robot_controller from blackboard if not provided in constructor
        if self.robot_controller is None:
            self.robot_controller = blackboard.get("robot_controller")
            if self.robot_controller is None:
                print(f"ObstacleCheckCondition {self.name}: No robot_controller found in blackboard")
                return False
        
        distance = self.robot_controller.get_nearest_obstacle_distance()
        print(f"ObstacleCheckCondition {self.name}: Distance {distance:.2f}m, safe {self.safe_distance}m")
        
        return distance <= self.safe_distance


class MovementAction(Action):
    """Movement action"""
    
    def __init__(self, name, robot_controller=None):
        super().__init__(name)
        self.robot_controller = robot_controller
    
    async def execute(self, blackboard):
        print(f"MovementAction {self.name}: Starting movement")
        
        # Get robot_controller from blackboard if not provided in constructor
        if self.robot_controller is None:
            self.robot_controller = blackboard.get("robot_controller")
            if self.robot_controller is None:
                print(f"MovementAction {self.name}: No robot_controller found in blackboard")
                return Status.FAILURE
        
        # Simulate movement
        for i in range(3):
            if self.robot_controller.move_towards_target(0.1):
                print(f"MovementAction {self.name}: Target reached")
                return Status.SUCCESS
            await asyncio.sleep(0.01)
        
        print(f"MovementAction {self.name}: Moving...")
        return Status.RUNNING


class BatteryChargingAction(Action):
    """Battery charging action"""
    
    def __init__(self, name, robot_controller=None):
        super().__init__(name)
        self.robot_controller = robot_controller
    
    async def execute(self, blackboard):
        print(f"BatteryChargingAction {self.name}: Starting charge")
        
        # Get robot_controller from blackboard if not provided in constructor
        if self.robot_controller is None:
            self.robot_controller = blackboard.get("robot_controller")
            if self.robot_controller is None:
                print(f"BatteryChargingAction {self.name}: No robot_controller found in blackboard")
                return Status.FAILURE
        
        for i in range(2):
            self.robot_controller.battery_level += 30
            self.robot_controller.battery_level = min(100, self.robot_controller.battery_level)
            print(f"BatteryChargingAction {self.name}: Charge progress {i+1}/2, level {self.robot_controller.battery_level:.1f}%")
            await asyncio.sleep(0.01)
        
        print(f"BatteryChargingAction {self.name}: Charge completed")
        return Status.SUCCESS


class TaskSchedulingAction(Action):
    """Task scheduling action"""
    
    def __init__(self, name, robot_controller=None):
        super().__init__(name)
        self.robot_controller = robot_controller
    
    async def execute(self, blackboard):
        print(f"TaskSchedulingAction {self.name}: Scheduling tasks")
        
        # Get robot_controller from blackboard if not provided in constructor
        if self.robot_controller is None:
            self.robot_controller = blackboard.get("robot_controller")
            if self.robot_controller is None:
                print(f"TaskSchedulingAction {self.name}: No robot_controller found in blackboard")
                return Status.FAILURE
        
        tasks = blackboard.get("task_queue", [])
        
        if not tasks:
            new_tasks = [
                {'type': 'move', 'target': {'x': random.uniform(-5, 5), 'y': random.uniform(-5, 5)}},
                {'type': 'patrol', 'route': [{'x': 0, 'y': 0}, {'x': 3, 'y': 3}, {'x': -3, 'y': -3}]}
            ]
            blackboard.set("task_queue", new_tasks)
            print(f"TaskSchedulingAction {self.name}: Generated {len(new_tasks)} new tasks")
        else:
            current_task = tasks[0]
            print(f"TaskSchedulingAction {self.name}: Processing task {current_task['type']}")
            
            if current_task['type'] == 'move':
                target = current_task['target']
                self.robot_controller.set_target(target['x'], target['y'])
                tasks.pop(0)
            
            blackboard.set("task_queue", tasks)
        
        await asyncio.sleep(0.01)
        return Status.SUCCESS


async def main():
    """Main function - demonstrate simplified robot control system"""
    
    register_custom_nodes()
    
    print("=== ABTree Simplified Robot Control System ===\n")
    
    # Create robot controller
    robot = RobotController("SmartRobot")
    
    # Add some obstacles
    robot.add_obstacle(2, 2)
    robot.add_obstacle(-1, 3)
    
    # Create behavior tree
    root = Selector("RobotControlSystem")
    
    # Emergency branch
    emergency_branch = Sequence("Emergency")
    emergency_branch.add_child(BatteryCheckCondition("BatteryCheck", 15))
    emergency_branch.add_child(BatteryChargingAction("BatteryCharge"))
    
    # Obstacle branch
    obstacle_branch = Sequence("ObstacleAvoidance")
    obstacle_branch.add_child(ObstacleCheckCondition("ObstacleCheck", 1.5))
    obstacle_branch.add_child(MovementAction("AvoidObstacle"))
    
    # Task execution branch
    task_branch = Sequence("TaskExecution")
    task_branch.add_child(TaskSchedulingAction("TaskSchedule"))
    task_branch.add_child(MovementAction("MoveToTarget"))
    
    # Sensor processing branch
    sensor_branch = Sequence("SensorProcessing")
    sensor_branch.add_child(SensorDataAction("ProcessSensors"))
    
    # Assemble behavior tree
    root.add_child(emergency_branch)
    root.add_child(obstacle_branch)
    root.add_child(task_branch)
    root.add_child(sensor_branch)
    
    # Create behavior tree instance
    tree = BehaviorTree()
    tree.load_from_root(root)
    blackboard = tree.blackboard
    
    # Initialize data
    blackboard.set("task_queue", [])
    blackboard.set("robot_controller", robot)
    
    print("Starting robot control system...")
    print("=" * 40)
    
    # Execute multiple rounds
    for i in range(5):
        print(f"\n--- Round {i+1} ---")
        
        result = await tree.tick()
        print(f"Result: {result}")
        
        sensor_data = blackboard.get("sensor_data", {})
        print(f"Robot position: ({robot.position.x:.2f}, {robot.position.y:.2f})")
        print(f"Battery level: {robot.battery_level:.1f}%")
        print(f"Obstacle distance: {sensor_data.get('obstacle_distance', float('inf')):.2f}m")
        print(f"Task queue length: {len(blackboard.get('task_queue', []))}")
        
        # Simulate external events
        if i % 2 == 0:
            robot.battery_level = max(0, robot.battery_level - 15)
            print(f"Battery level reduced to {robot.battery_level:.1f}%")
        
        if i % 3 == 0:
            robot.add_obstacle(random.uniform(-4, 4), random.uniform(-4, 4))
        
        await asyncio.sleep(0.05)
    
    print("\n=== Final Status ===")
    print(f"Final robot position: ({robot.position.x:.2f}, {robot.position.y:.2f})")
    print(f"Final battery level: {robot.battery_level:.1f}%")
    print(f"Total tasks: {len(blackboard.get('task_queue', []))}")
    
    # Demonstrate XML configuration
    print("\n=== XML Configuration Demo ===")
    
    # XML string configuration
    xml_config = '''
    <BehaviorTree name="RobotControlXML" description="XML configured robot control system">
        <Selector name="RobotControlSystem">
            <Sequence name="Emergency">
                <BatteryCheckCondition name="BatteryCheck" threshold="15" />
                <BatteryChargingAction name="BatteryCharge" />
            </Sequence>
            <Sequence name="ObstacleAvoidance">
                <ObstacleCheckCondition name="ObstacleCheck" safe_distance="1.5" />
                <MovementAction name="AvoidObstacle" />
            </Sequence>
            <Sequence name="TaskExecution">
                <TaskSchedulingAction name="TaskSchedule"/>
                <MovementAction name="MoveToTarget" />
            </Sequence>
            <Sequence name="SensorProcessing">
                <SensorDataAction name="ProcessSensors"/>
            </Sequence>
        </Selector>
    </BehaviorTree>
    '''
    
    # Parse XML configuration
    xml_tree = BehaviorTree()
    
    xml_tree.load_from_string(xml_config)
    xml_blackboard = xml_tree.blackboard
    
    # Set robot_controller in blackboard for XML nodes
    xml_blackboard.set("robot_controller", robot)
    
    # Initialize XML configuration data
    xml_blackboard.set("task_queue", [])
    
    print("Behavior tree configured via XML string:")
    print(xml_config.strip())
    print("\nStarting XML configured behavior tree...")
    xml_result = await xml_tree.tick()
    print(f"XML configuration execution completed! Result: {xml_result}")
    print(f"XML configuration task queue length: {len(xml_blackboard.get('task_queue', []))}")


if __name__ == "__main__":
    asyncio.run(main()) 