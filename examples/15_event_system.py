#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 11: Event System – Event-Driven Behavior Trees

Demonstrates how to use the event system to drive the execution of behavior trees.
The event system allows behavior trees to respond to external events, enabling more flexible decision logic.

Key Learning Points:

    Event listening mechanisms

    Event handling workflows

    Asynchronous event system

    Event prioritization

    Event filtering

    How to configure the event system using XML strings
"""

import asyncio
import random
import time
from abtree import BehaviorTree, Sequence, Selector, Action, Condition, register_node
from abtree.core import Status
from abtree.nodes.base import BaseNode
from abtree.parser.xml_parser import XMLParser


# 注册自定义节点类型
def register_custom_nodes():
    """注册自定义节点类型"""
    register_node("EventSystem", EventSystem)
    register_node("EventDrivenAction", EventDrivenAction)
    register_node("EventCondition", EventCondition)
    register_node("EmergencyResponseAction", EmergencyResponseAction)
    register_node("SensorDataProcessingAction", SensorDataProcessingAction)
    register_node("UserCommandAction", UserCommandAction)


class EventSystem(BaseNode):
    """事件系统 - 管理事件的发布和订阅"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.subscribers = {}
        self.event_queue = []
        self.event_history = []
    
    def subscribe(self, event_type, handler, priority=1):
        """订阅事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append({
            'handler': handler,
            'priority': priority,
            'timestamp': time.time()
        })
        
        # 按优先级排序
        self.subscribers[event_type].sort(key=lambda x: (-x['priority'], x['timestamp']))
    
    def publish(self, event_type, data=None, priority=1):
        """发布事件"""
        event = {
            'type': event_type,
            'data': data,
            'priority': priority,
            'timestamp': time.time()
        }
        
        self.event_queue.append(event)
        self.event_history.append(event)
        
        # 限制历史记录长度
        if len(self.event_history) > 100:
            self.event_history.pop(0)
        
        print(f"事件系统 {self.name}: 发布事件 {event_type} (优先级: {priority})")
    
    async def process_events(self, blackboard):
        """处理事件队列"""
        if not self.event_queue:
            return Status.SUCCESS
        
        # 按优先级排序事件
        self.event_queue.sort(key=lambda x: (-x['priority'], x['timestamp']))
        
        # 处理最高优先级事件
        event = self.event_queue.pop(0)
        event_type = event['type']
        
        if event_type in self.subscribers:
            for subscriber in self.subscribers[event_type]:
                try:
                    result = await subscriber['handler'](event, blackboard)
                    if result == Status.SUCCESS:
                        print(f"事件系统 {self.name}: 事件 {event_type} 处理成功")
                        return Status.SUCCESS
                except Exception as e:
                    print(f"事件系统 {self.name}: 事件处理错误: {e}")
        
        return Status.FAILURE
    
    async def tick(self, blackboard):
        """执行事件系统"""
        return await self.process_events(blackboard)


class EmergencyEventHandler:
    """紧急事件处理器"""
    
    async def handle(self, event, blackboard):
        print(f"处理紧急事件: {event['data']}")
        await asyncio.sleep(0.2)
        
        # 设置紧急状态
        blackboard.set("emergency_mode", True)
        blackboard.set("last_emergency", event['timestamp'])
        blackboard.set("emergency_count", blackboard.get("emergency_count", 0) + 1)
        
        return Status.SUCCESS


class SensorEventHandler:
    """传感器事件处理器"""
    
    async def handle(self, event, blackboard):
        sensor_data = event['data']
        print(f"处理传感器事件: {sensor_data}")
        await asyncio.sleep(0.1)
        
        # 更新传感器数据
        blackboard.set("sensor_data", sensor_data)
        blackboard.set("last_sensor_update", event['timestamp'])
        
        return Status.SUCCESS


class UserInputEventHandler:
    """用户输入事件处理器"""
    
    async def handle(self, event, blackboard):
        user_input = event['data']
        print(f"处理用户输入: {user_input}")
        await asyncio.sleep(0.1)
        
        # 处理用户输入
        blackboard.set("user_input", user_input)
        blackboard.set("last_user_input", event['timestamp'])
        
        return Status.SUCCESS


class SystemStatusEventHandler:
    """系统状态事件处理器"""
    
    async def handle(self, event, blackboard):
        status_data = event['data']
        print(f"处理系统状态事件: {status_data}")
        await asyncio.sleep(0.1)
        
        # 更新系统状态
        blackboard.set("system_status", status_data)
        blackboard.set("last_status_update", event['timestamp'])
        
        return Status.SUCCESS


class EventDrivenAction(Action):
    """事件驱动的动作节点"""
    
    def __init__(self, name, required_event_type, event_system=None, **kwargs):
        super().__init__(name, **kwargs)
        self.event_system = event_system
        self.required_event_type = required_event_type
        self.last_event_time = 0
    
    async def execute(self, blackboard):
        print(f"事件驱动动作 {self.name}: 等待事件 {self.required_event_type}")
        
        # 检查是否有新事件
        for event in self.event_system.event_history:
            if (event['type'] == self.required_event_type and 
                event['timestamp'] > self.last_event_time):
                
                self.last_event_time = event['timestamp']
                print(f"事件驱动动作 {self.name}: 收到事件，开始执行")
                
                await asyncio.sleep(0.3)
                return Status.SUCCESS
        
        print(f"事件驱动动作 {self.name}: 未收到所需事件")
        return Status.RUNNING


class EventCondition(Condition):
    """事件条件节点"""
    
    def __init__(self, name, event_type, timeout=5.0, event_system=None, **kwargs):
        super().__init__(name, **kwargs)
        self.event_system = event_system
        self.event_type = event_type
        self.timeout = timeout
        self.start_time = None
    
    async def evaluate(self, blackboard):
        if self.start_time is None:
            self.start_time = time.time()
        
        # 检查是否超时
        if time.time() - self.start_time > self.timeout:
            print(f"事件条件 {self.name}: 等待超时")
            return False
        
        # 如果没有事件系统，返回False
        if self.event_system is None:
            print(f"事件条件 {self.name}: 无事件系统")
            return False
        
        # 检查是否有指定类型的事件
        for event in self.event_system.event_history:
            if (event['type'] == self.event_type and 
                event['timestamp'] > self.start_time):
                print(f"事件条件 {self.name}: 检测到事件 {self.event_type}")
                return True
        
        print(f"事件条件 {self.name}: 等待事件 {self.event_type}")
        return False


class EmergencyResponseAction(Action):
    """紧急响应动作"""
    
    async def execute(self, blackboard):
        print("执行紧急响应...")
        await asyncio.sleep(0.5)
        
        # 执行紧急响应逻辑
        blackboard.set("emergency_response_executed", True)
        blackboard.set("response_time", time.time())
        
        print("紧急响应完成")
        return Status.SUCCESS


class SensorDataProcessingAction(Action):
    """传感器数据处理动作"""
    
    async def execute(self, blackboard):
        print("处理传感器数据...")
        await asyncio.sleep(0.3)
        
        sensor_data = blackboard.get("sensor_data", {})
        if sensor_data:
            # 处理传感器数据
            processed_data = {
                'temperature': sensor_data.get('temperature', 0) + random.uniform(-1, 1),
                'humidity': sensor_data.get('humidity', 0) + random.uniform(-2, 2),
                'pressure': sensor_data.get('pressure', 0) + random.uniform(-0.5, 0.5)
            }
            
            blackboard.set("processed_sensor_data", processed_data)
            print(f"传感器数据处理完成: {processed_data}")
        
        return Status.SUCCESS


class UserCommandAction(Action):
    """用户命令处理动作"""
    
    async def execute(self, blackboard):
        print("处理用户命令...")
        await asyncio.sleep(0.2)
        
        user_input = blackboard.get("user_input", "")
        if user_input:
            # 处理用户命令
            blackboard.set("command_processed", True)
            blackboard.set("last_command", user_input)
            print(f"用户命令处理完成: {user_input}")
        
        return Status.SUCCESS


async def main():
    """主函数 - 演示事件系统"""
    
    # 注册自定义节点类型
    register_custom_nodes()
    
    print("=== ABTree 事件系统示例 ===\n")
    
    # 1. 创建事件系统
    event_system = EventSystem("主事件系统")
    
    # 2. 注册事件处理器
    emergency_handler = EmergencyEventHandler()
    sensor_handler = SensorEventHandler()
    user_input_handler = UserInputEventHandler()
    system_status_handler = SystemStatusEventHandler()
    
    event_system.subscribe("emergency", emergency_handler.handle, priority=3)
    event_system.subscribe("sensor", sensor_handler.handle, priority=1)
    event_system.subscribe("user_input", user_input_handler.handle, priority=2)
    event_system.subscribe("system_status", system_status_handler.handle, priority=1)
    
    # 3. 创建行为树
    root = Selector("事件驱动系统")
    
    # 紧急响应分支
    emergency_branch = Sequence("紧急响应")
    emergency_condition = EventCondition("等待紧急事件", "emergency")
    emergency_condition.event_system = event_system
    emergency_branch.add_child(emergency_condition)
    emergency_branch.add_child(EmergencyResponseAction("紧急响应"))
    
    # 传感器处理分支
    sensor_branch = Sequence("传感器处理")
    sensor_condition = EventCondition("等待传感器事件", "sensor")
    sensor_condition.event_system = event_system
    sensor_branch.add_child(sensor_condition)
    sensor_branch.add_child(SensorDataProcessingAction("传感器数据处理"))
    
    # 用户命令处理分支
    user_branch = Sequence("用户命令处理")
    user_condition = EventCondition("等待用户输入", "user_input")
    user_condition.event_system = event_system
    user_branch.add_child(user_condition)
    user_branch.add_child(UserCommandAction("用户命令处理"))
    
    # 事件处理分支
    event_processing_branch = Sequence("事件处理")
    event_processing_branch.add_child(event_system)
    
    # 4. 组装行为树
    root.add_child(emergency_branch)
    root.add_child(sensor_branch)
    root.add_child(user_branch)
    root.add_child(event_processing_branch)
    
    # 5. 创建行为树实例
    tree = BehaviorTree()
    tree.load_from_root(root)
    blackboard = tree.blackboard
    
    # 6. 初始化数据
    blackboard.set("emergency_mode", False)
    blackboard.set("emergency_count", 0)
    blackboard.set("command_processed", False)
    
    print("开始执行事件驱动系统...")
    print("=" * 50)
    
    # 7. 模拟事件发布和处理
    for i in range(10):
        print(f"\n--- 第 {i+1} 轮执行 ---")
        
        # 随机发布事件
        event_types = ["sensor", "user_input", "system_status", "emergency"]
        weights = [0.4, 0.3, 0.2, 0.1]  # 事件概率权重
        
        event_type = random.choices(event_types, weights=weights)[0]
        
        if event_type == "sensor":
            event_system.publish("sensor", {
                "temperature": random.uniform(20, 30),
                "humidity": random.uniform(40, 60),
                "pressure": random.uniform(1000, 1020)
            })
        elif event_type == "user_input":
            commands = ["start", "stop", "status", "config"]
            event_system.publish("user_input", random.choice(commands))
        elif event_type == "system_status":
            event_system.publish("system_status", {
                "cpu_usage": random.uniform(0, 100),
                "memory_usage": random.uniform(0, 100),
                "disk_usage": random.uniform(0, 100)
            })
        elif event_type == "emergency":
            event_system.publish("emergency", f"紧急情况 {i+1}")
        
        # 执行行为树
        result = await tree.tick()
        print(f"执行结果: {result}")
        
        # 显示状态
        print(f"紧急模式: {blackboard.get('emergency_mode')}")
        print(f"紧急事件数: {blackboard.get('emergency_count')}")
        print(f"命令处理: {blackboard.get('command_processed')}")
        
        await asyncio.sleep(0.5)
    
    print("\n=== 最终状态 ===")
    print(f"总事件数: {len(event_system.event_history)}")
    print(f"紧急事件数: {blackboard.get('emergency_count')}")
    print(f"最后命令: {blackboard.get('last_command', '无')}")
    print(f"处理后的传感器数据: {blackboard.get('processed_sensor_data', {})}")
    
    # 8. 演示XML配置方式
    print("\n=== XML配置方式演示 ===")
    
    # XML字符串配置
    xml_config = '''
    <BehaviorTree name="EventSystemXML" description="XML配置的事件系统示例">
        <Sequence name="根序列">
            <Selector name="事件驱动系统">
                <Sequence name="紧急响应">
                    <EventCondition name="等待紧急事件" event_type="emergency" timeout="5.0" />
                    <EmergencyResponseAction name="紧急响应" />
                </Sequence>
                <Sequence name="传感器处理">
                    <EventCondition name="等待传感器事件" event_type="sensor" timeout="3.0" />
                    <SensorDataProcessingAction name="传感器数据处理" />
                </Sequence>
                <Sequence name="用户命令处理">
                    <EventCondition name="等待用户输入" event_type="user_input" timeout="2.0" />
                    <UserCommandAction name="用户命令处理" />
                </Sequence>
            </Selector>
        </Sequence>
    </BehaviorTree>
    '''
    
    # 解析XML配置
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    xml_blackboard = xml_tree.blackboard
    
    # 初始化XML配置的数据
    xml_blackboard.set("emergency_mode", False)
    xml_blackboard.set("emergency_count", 0)
    xml_blackboard.set("command_processed", False)
    
    print("通过XML字符串配置的行为树:")
    print(xml_config.strip())
    print("\n开始执行XML配置的行为树...")
    xml_result = await xml_tree.tick()
    print(f"XML配置执行完成! 结果: {xml_result}")
    print(f"XML配置紧急模式: {xml_blackboard.get('emergency_mode')}")


if __name__ == "__main__":
    asyncio.run(main()) 