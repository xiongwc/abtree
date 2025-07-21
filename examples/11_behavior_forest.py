"""
Behavior Forest Example - Multi-Behavior Tree Collaboration

This example demonstrates the Behavior Forest architecture with 6 different
communication patterns for multi-agent collaboration.
"""

import asyncio
import random
from typing import Any, Dict, Set

from abtree import (
    # Core components
    BehaviorTree, Blackboard, EventSystem, Status,
    # Node types
    Sequence, Selector, Action, Condition, Log, Wait, SetBlackboard, CheckBlackboard,
    # Forest components
    BehaviorForest, ForestNode, ForestNodeType, ForestManager, ForestConfig,
    PubSubMiddleware, ReqRespMiddleware, SharedBlackboardMiddleware,
    StateWatchingMiddleware, BehaviorCallMiddleware, TaskBoardMiddleware,
    # Registration
    register_node,
)


# ==================== Custom Node Definitions ====================

class RobotAction(Action):
    """Base robot action node"""
    
    def __init__(self, name: str, robot_id: str):
        super().__init__(name)
        self.robot_id = robot_id
    
    async def execute(self, blackboard):
        print(f"🤖 {self.robot_id}: {self.name}")
        return Status.SUCCESS


class PatrolAction(RobotAction):
    """Patrol action for robots"""
    
    async def execute(self, blackboard):
        await super().execute(blackboard)
        print(f"   📍 {self.robot_id} is patrolling area")
        await asyncio.sleep(0.5)
        return Status.SUCCESS


class ChargeAction(RobotAction):
    """Charging action for robots"""
    
    async def execute(self, blackboard):
        await super().execute(blackboard)
        battery_level = blackboard.get("battery_level", 50)
        if battery_level < 30:
            print(f"   🔋 {self.robot_id} is charging (battery: {battery_level}%)")
            blackboard.set("battery_level", min(100, battery_level + 20))
            await asyncio.sleep(1.0)
            return Status.SUCCESS
        else:
            print(f"   ✅ {self.robot_id} battery is sufficient ({battery_level}%)")
            return Status.SUCCESS


class EmergencyResponseAction(RobotAction):
    """Emergency response action"""
    
    async def execute(self, blackboard):
        await super().execute(blackboard)
        print(f"   🚨 {self.robot_id} responding to emergency!")
        await asyncio.sleep(0.3)
        return Status.SUCCESS


class TaskExecutionAction(RobotAction):
    """Task execution action"""
    
    def __init__(self, name: str, robot_id: str, task_type: str):
        super().__init__(name, robot_id)
        self.task_type = task_type
    
    async def execute(self, blackboard):
        await super().execute(blackboard)
        print(f"   📋 {self.robot_id} executing {self.task_type} task")
        await asyncio.sleep(0.8)
        return Status.SUCCESS


class BatteryCheckCondition(Condition):
    """Check battery level condition"""
    
    def __init__(self, name: str, robot_id: str, threshold: int = 30):
        super().__init__(name)
        self.robot_id = robot_id
        self.threshold = threshold
    
    async def evaluate(self, blackboard):
        battery_level = blackboard.get("battery_level", 50)
        is_low = battery_level < self.threshold
        print(f"   🔋 {self.robot_id} battery check: {battery_level}% (low: {is_low})")
        return is_low


class EmergencyCheckCondition(Condition):
    """Check for emergency condition"""
    
    def __init__(self, name: str, robot_id: str):
        super().__init__(name)
        self.robot_id = robot_id
    
    async def evaluate(self, blackboard):
        emergency_active = blackboard.get("emergency_active", False)
        print(f"   🚨 {self.robot_id} emergency check: {emergency_active}")
        return emergency_active


class TaskAvailableCondition(Condition):
    """Check if tasks are available"""
    
    def __init__(self, name: str, robot_id: str):
        super().__init__(name)
        self.robot_id = robot_id
    
    async def evaluate(self, blackboard):
        available_tasks = blackboard.get("available_tasks", 0)
        print(f"   📋 {self.robot_id} task check: {available_tasks} tasks available")
        return available_tasks > 0


# ==================== Forest Node Builders ====================

def create_robot_forest_node(robot_id: str, capabilities: Set[str]) -> ForestNode:
    """Create a robot behavior tree node"""
    
    # Create behavior tree
    root = Selector(f"Robot {robot_id} Decision")
    
    # Emergency response branch (highest priority)
    emergency_branch = Sequence("Emergency Response")
    emergency_branch.add_child(EmergencyCheckCondition("Check Emergency", robot_id))
    emergency_branch.add_child(EmergencyResponseAction("Emergency Response", robot_id))
    
    # Battery management branch
    battery_branch = Sequence("Battery Management")
    battery_branch.add_child(BatteryCheckCondition("Check Battery", robot_id))
    battery_branch.add_child(ChargeAction("Charge Battery", robot_id))
    
    # Task execution branch
    task_branch = Sequence("Task Execution")
    task_branch.add_child(TaskAvailableCondition("Check Tasks", robot_id))
    task_branch.add_child(TaskExecutionAction("Execute Task", robot_id, "general"))
    
    # Patrol branch (lowest priority)
    patrol_branch = Sequence("Patrol")
    patrol_branch.add_child(PatrolAction("Patrol Area", robot_id))
    
    # Assemble tree
    root.add_child(emergency_branch)
    root.add_child(battery_branch)
    root.add_child(task_branch)
    root.add_child(patrol_branch)
    
    # Create behavior tree
    tree = BehaviorTree()
    tree.load_from_root(root)
    
    # Initialize blackboard
    blackboard = tree.blackboard
    blackboard.set("battery_level", random.randint(20, 80))
    blackboard.set("emergency_active", False)
    blackboard.set("available_tasks", 0)
    
    # Create forest node
    node = ForestNode(
        name=f"Robot_{robot_id}",
        tree=tree,
        node_type=ForestNodeType.WORKER,
        capabilities=capabilities
    )
    
    return node


def create_coordinator_forest_node() -> ForestNode:
    """Create a coordinator behavior tree node"""
    
    # Create behavior tree
    root = Sequence("Coordinator Main")
    
    # Task distribution
    task_distribution = Sequence("Task Distribution")
    task_distribution.add_child(Log(name="Distribute Tasks", message="Distributing tasks to robots"))
    task_distribution.add_child(Wait(name="Task Wait", duration=1.0))
    
    # Emergency monitoring
    emergency_monitoring = Sequence("Emergency Monitoring")
    emergency_monitoring.add_child(Log(name="Monitor Emergencies", message="Monitoring for emergencies"))
    emergency_monitoring.add_child(Wait(name="Emergency Wait", duration=0.5))
    
    # System status
    system_status = Sequence("System Status")
    system_status.add_child(Log(name="Update Status", message="Updating system status"))
    system_status.add_child(Wait(name="Status Wait", duration=2.0))
    
    # Assemble tree
    root.add_child(task_distribution)
    root.add_child(emergency_monitoring)
    root.add_child(system_status)
    
    # Create behavior tree
    tree = BehaviorTree()
    tree.load_from_root(root)
    
    # Create forest node
    node = ForestNode(
        name="Coordinator",
        tree=tree,
        node_type=ForestNodeType.COORDINATOR,
        capabilities={"coordination", "task_distribution", "monitoring"}
    )
    
    return node


def create_monitor_forest_node() -> ForestNode:
    """Create a monitor behavior tree node"""
    
    # Create behavior tree
    root = Sequence("Monitor Main")
    
    # System monitoring
    system_monitoring = Sequence("System Monitoring")
    system_monitoring.add_child(Log(name="Monitor System", message="Monitoring system health"))
    system_monitoring.add_child(Wait(name="Monitor Wait", duration=1.5))
    
    # Performance tracking
    performance_tracking = Sequence("Performance Tracking")
    performance_tracking.add_child(Log(name="Track Performance", message="Tracking performance metrics"))
    performance_tracking.add_child(Wait(name="Performance Wait", duration=1.0))
    
    # Assemble tree
    root.add_child(system_monitoring)
    root.add_child(performance_tracking)
    
    # Create behavior tree
    tree = BehaviorTree()
    tree.load_from_root(root)
    
    # Create forest node
    node = ForestNode(
        name="Monitor",
        tree=tree,
        node_type=ForestNodeType.MONITOR,
        capabilities={"monitoring", "performance_tracking", "health_check"}
    )
    
    return node


# ==================== Communication Pattern Examples ====================

async def demonstrate_pubsub_pattern(forest: BehaviorForest):
    """Demonstrate Pub/Sub communication pattern"""
    print("\n=== 🔔 Pub/Sub Pattern Demonstration ===")
    
    # Get pub/sub middleware
    pubsub = None
    for middleware in forest.middleware:
        if isinstance(middleware, PubSubMiddleware):
            pubsub = middleware
            break
    
    if not pubsub:
        print("❌ Pub/Sub middleware not found")
        return
    
    # Subscribe to events
    def emergency_handler(event):
        print(f"🚨 Emergency event received: {event.data}")
    
    def task_handler(event):
        print(f"📋 Task event received: {event.data}")
    
    pubsub.subscribe("emergency", emergency_handler)
    pubsub.subscribe("task", task_handler)
    
    # Publish events
    await pubsub.publish("emergency", "Fire detected in sector A", "Coordinator")
    await pubsub.publish("task", "New cleaning task available", "Coordinator")
    
    await asyncio.sleep(0.5)


async def demonstrate_reqresp_pattern(forest: BehaviorForest):
    """Demonstrate Req/Resp communication pattern"""
    print("\n=== 📞 Req/Resp Pattern Demonstration ===")
    
    # Get req/resp middleware
    reqresp = None
    for middleware in forest.middleware:
        if isinstance(middleware, ReqRespMiddleware):
            reqresp = middleware
            break
    
    if not reqresp:
        print("❌ Req/Resp middleware not found")
        return
    
    # Register services
    async def get_battery_status(params, source):
        robot_id = params.get("robot_id", "unknown")
        # Simulate getting battery status
        return {"robot_id": robot_id, "battery_level": random.randint(20, 100)}
    
    async def get_task_status(params, source):
        task_id = params.get("task_id", "unknown")
        # Simulate getting task status
        return {"task_id": task_id, "status": "in_progress", "progress": 75}
    
    reqresp.register_service("get_battery_status", get_battery_status)
    reqresp.register_service("get_task_status", get_task_status)
    
    # Make requests
    try:
        battery_result = await reqresp.request("get_battery_status", {"robot_id": "R1"}, "Coordinator")
        print(f"🔋 Battery status: {battery_result}")
        
        task_result = await reqresp.request("get_task_status", {"task_id": "T001"}, "Coordinator")
        print(f"📋 Task status: {task_result}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    await asyncio.sleep(0.5)


async def demonstrate_shared_blackboard_pattern(forest: BehaviorForest):
    """Demonstrate Shared Blackboard communication pattern"""
    print("\n=== 📊 Shared Blackboard Pattern Demonstration ===")
    
    # Get shared blackboard middleware
    shared_bb = None
    for middleware in forest.middleware:
        if isinstance(middleware, SharedBlackboardMiddleware):
            shared_bb = middleware
            break
    
    if not shared_bb:
        print("❌ Shared Blackboard middleware not found")
        return
    
    # Set shared data
    shared_bb.set("system_status", "operational", "Coordinator")
    shared_bb.set("active_robots", 3, "Coordinator")
    shared_bb.set("emergency_level", "normal", "Coordinator")
    
    # Read shared data
    system_status = shared_bb.get("system_status", "unknown", "Robot_R1")
    active_robots = shared_bb.get("active_robots", 0, "Robot_R2")
    emergency_level = shared_bb.get("emergency_level", "unknown", "Monitor")
    
    print(f"📊 Shared data - System: {system_status}, Robots: {active_robots}, Emergency: {emergency_level}")
    
    await asyncio.sleep(0.5)


async def demonstrate_state_watching_pattern(forest: BehaviorForest):
    """Demonstrate State Watching communication pattern"""
    print("\n=== 👀 State Watching Pattern Demonstration ===")
    
    # Get state watching middleware
    state_watch = None
    for middleware in forest.middleware:
        if isinstance(middleware, StateWatchingMiddleware):
            state_watch = middleware
            break
    
    if not state_watch:
        print("❌ State Watching middleware not found")
        return
    
    # Watch for state changes
    def emergency_state_handler(key, old_value, new_value, source):
        print(f"🚨 Emergency state changed: {old_value} -> {new_value} (from {source})")
    
    def battery_state_handler(key, old_value, new_value, source):
        print(f"🔋 Battery state changed: {old_value} -> {new_value} (from {source})")
    
    state_watch.watch_state("emergency_level", emergency_state_handler, "Monitor")
    state_watch.watch_state("battery_level", battery_state_handler, "Monitor")
    
    # Update states
    await state_watch.update_state("emergency_level", "high", "Coordinator")
    await state_watch.update_state("battery_level", 15, "Robot_R1")
    await state_watch.update_state("emergency_level", "critical", "Coordinator")
    
    await asyncio.sleep(0.5)


async def demonstrate_behavior_call_pattern(forest: BehaviorForest):
    """Demonstrate Behavior Call communication pattern"""
    print("\n=== 🔄 Behavior Call Pattern Demonstration ===")
    
    # Get behavior call middleware
    behavior_call = None
    for middleware in forest.middleware:
        if isinstance(middleware, BehaviorCallMiddleware):
            behavior_call = middleware
            break
    
    if not behavior_call:
        print("❌ Behavior Call middleware not found")
        return
    
    # Register behaviors
    async def patrol_behavior(params):
        robot_id = params.get("robot_id", "unknown")
        area = params.get("area", "default")
        print(f"🔄 Executing patrol behavior for {robot_id} in {area}")
        return {"status": "patrolling", "area": area}
    
    async def charge_behavior(params):
        robot_id = params.get("robot_id", "unknown")
        print(f"🔄 Executing charge behavior for {robot_id}")
        return {"status": "charging", "battery_increase": 20}
    
    behavior_call.register_behavior("patrol", patrol_behavior)
    behavior_call.register_behavior("charge", charge_behavior)
    
    # Call behaviors
    try:
        patrol_result = await behavior_call.call_behavior("patrol", {"robot_id": "R1", "area": "sector_A"}, "Coordinator")
        print(f"🔄 Patrol result: {patrol_result}")
        
        charge_result = await behavior_call.call_behavior("charge", {"robot_id": "R2"}, "Coordinator")
        print(f"🔄 Charge result: {charge_result}")
    except Exception as e:
        print(f"❌ Behavior call failed: {e}")
    
    await asyncio.sleep(0.5)


async def demonstrate_task_board_pattern(forest: BehaviorForest):
    """Demonstrate Task Board communication pattern"""
    print("\n=== 📋 Task Board Pattern Demonstration ===")
    
    # Get task board middleware
    task_board = None
    for middleware in forest.middleware:
        if isinstance(middleware, TaskBoardMiddleware):
            task_board = middleware
            break
    
    if not task_board:
        print("❌ Task Board middleware not found")
        return
    
    # Publish tasks
    task1_id = task_board.publish_task(
        "Clean Sector A",
        "Clean and sanitize sector A",
        {"cleaning", "navigation"},
        priority=3
    )
    
    task2_id = task_board.publish_task(
        "Inspect Equipment",
        "Inspect and maintain equipment",
        {"inspection", "maintenance"},
        priority=2
    )
    
    task3_id = task_board.publish_task(
        "Emergency Response",
        "Respond to emergency situation",
        {"emergency", "response"},
        priority=5
    )
    
    print(f"📋 Published tasks: {task1_id}, {task2_id}, {task3_id}")
    
    # Simulate robots claiming tasks
    robot_capabilities = {
        "Robot_R1": {"cleaning", "navigation", "emergency"},
        "Robot_R2": {"inspection", "maintenance", "cleaning"},
        "Robot_R3": {"emergency", "response", "navigation"}
    }
    
    for robot_id, capabilities in robot_capabilities.items():
        available_tasks = task_board.get_available_tasks(capabilities)
        if available_tasks:
            task = available_tasks[0]  # Claim highest priority task
            if task_board.claim_task(task.id, robot_id, capabilities):
                print(f"🤖 {robot_id} claimed task: {task.title}")
    
    # Complete some tasks
    if task_board.complete_task(task1_id, {"completion_time": "2:30", "quality": "excellent"}):
        print(f"✅ Task {task1_id} completed")
    
    await asyncio.sleep(0.5)


# ==================== Main Function ====================

async def main():
    """Main function - demonstrate behavior forest"""
    
    print("=== 🌳 Behavior Forest Example ===")
    print("Demonstrating multi-behavior tree collaboration with 6 communication patterns")
    
    # 1. Create forest configuration
    config = ForestConfig(
        name="RobotCollaborationForest",
        tick_rate=30.0,
        enabled_middleware=[
            PubSubMiddleware,
            ReqRespMiddleware,
            SharedBlackboardMiddleware,
            StateWatchingMiddleware,
            BehaviorCallMiddleware,
            TaskBoardMiddleware,
        ]
    )
    
    # 2. Create behavior forest
    forest = BehaviorForest(
        name=config.name,
        forest_blackboard=Blackboard(),
        forest_event_system=EventSystem()
    )
    
    # 3. Add middleware
    forest.add_middleware(PubSubMiddleware("PubSub"))
    forest.add_middleware(ReqRespMiddleware("ReqResp"))
    forest.add_middleware(SharedBlackboardMiddleware("SharedBlackboard"))
    forest.add_middleware(StateWatchingMiddleware("StateWatching"))
    forest.add_middleware(BehaviorCallMiddleware("BehaviorCall"))
    forest.add_middleware(TaskBoardMiddleware("TaskBoard"))
    
    # 4. Create and add forest nodes
    robots = ["R1", "R2", "R3"]
    robot_capabilities = {
        "R1": {"cleaning", "navigation", "emergency"},
        "R2": {"inspection", "maintenance", "cleaning"},
        "R3": {"emergency", "response", "navigation"}
    }
    
    # Add robot nodes
    for robot_id in robots:
        capabilities = robot_capabilities[robot_id]
        node = create_robot_forest_node(robot_id, capabilities)
        forest.add_node(node)
        print(f"🤖 Added robot node: {node.name} with capabilities: {capabilities}")
    
    # Add coordinator node
    coordinator_node = create_coordinator_forest_node()
    forest.add_node(coordinator_node)
    print(f"👨‍💼 Added coordinator node: {coordinator_node.name}")
    
    # Add monitor node
    monitor_node = create_monitor_forest_node()
    forest.add_node(monitor_node)
    print(f"📊 Added monitor node: {monitor_node.name}")
    
    # 5. Start forest
    print(f"\n🚀 Starting behavior forest: {forest.name}")
    await forest.start()
    
    # 6. Demonstrate communication patterns
    await demonstrate_pubsub_pattern(forest)
    await demonstrate_reqresp_pattern(forest)
    await demonstrate_shared_blackboard_pattern(forest)
    await demonstrate_state_watching_pattern(forest)
    await demonstrate_behavior_call_pattern(forest)
    await demonstrate_task_board_pattern(forest)
    
    # 7. Run forest for a few ticks
    print("\n=== 🌳 Running Forest ===")
    for i in range(5):
        print(f"\n--- Tick {i+1} ---")
        results = await forest.tick()
        
        # Display results
        for node_name, status in results.items():
            print(f"  {node_name}: {status.name}")
        
        # Simulate some events
        if i == 1:
            # Trigger emergency
            forest.forest_blackboard.set("emergency_active", True)
            print("🚨 Emergency triggered!")
        elif i == 3:
            # Add tasks
            forest.forest_blackboard.set("available_tasks", 2)
            print("📋 Tasks added!")
        
        await asyncio.sleep(1.0)
    
    # 8. Stop forest
    print("\n🛑 Stopping behavior forest...")
    await forest.stop()
    
    # 9. Display final statistics
    stats = forest.get_stats()
    print(f"\n📊 Forest Statistics:")
    print(f"  Name: {stats['name']}")
    print(f"  Total nodes: {stats['total_nodes']}")
    print(f"  Middleware count: {stats['middleware_count']}")
    print(f"  Tick rate: {stats['tick_rate']}")
    
    print("\n✅ Behavior Forest example completed!")


if __name__ == "__main__":
    asyncio.run(main()) 