#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 10: Advanced Control Flow – Complex Control Flow Patterns

Demonstrates more advanced control flow patterns, including state machines, event-driven execution, and priority queues.
These patterns are highly useful in real-world applications.

Key Learning Points:

    State machine patterns

    Event-driven control flow

    Priority queues

    Dynamic decision-making

    Complex branching logic

    How to configure advanced control flows using XML strings
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
    register_node("ChargeAction", ChargeAction)
    register_node("OptimizeAction", OptimizeAction)
    register_node("MaintenanceAction", MaintenanceAction)
    register_node("StateMachine", StateMachine)
    register_node("EventDrivenController", EventDrivenController)
    register_node("PriorityQueue", PriorityQueue)
    register_node("DynamicDecisionMaker", DynamicDecisionMaker)


class StateMachine(BaseNode):
    """状态机 - 管理复杂的状态转换"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.current_state = "idle"
        self.states = {
            "idle": self.idle_state,
            "working": self.working_state,
            "error": self.error_state,
            "recovery": self.recovery_state
        }
        self.transitions = {
            "idle": ["working"],
            "working": ["idle", "error"],
            "error": ["recovery", "idle"],
            "recovery": ["working", "idle"]
        }
    
    async def idle_state(self, blackboard):
        """空闲状态"""
        print(f"状态机 {self.name}: 空闲状态")
        await asyncio.sleep(0.2)
        
        # 检查是否有工作要做
        if blackboard.get("has_work", False):
            self.current_state = "working"
            return Status.SUCCESS
        else:
            return Status.RUNNING
    
    async def working_state(self, blackboard):
        """工作状态"""
        print(f"状态机 {self.name}: 工作状态")
        await asyncio.sleep(0.3)
        
        # 模拟工作过程
        work_progress = blackboard.get("work_progress", 0)
        work_progress += random.randint(10, 30)
        blackboard.set("work_progress", work_progress)
        
        # 检查是否出错
        if random.random() < 0.1:  # 10%出错概率
            self.current_state = "error"
            blackboard.set("error_count", blackboard.get("error_count", 0) + 1)
            return Status.FAILURE
        
        # 检查工作是否完成
        if work_progress >= 100:
            self.current_state = "idle"
            blackboard.set("work_completed", True)
            blackboard.set("work_progress", 0)
            return Status.SUCCESS
        
        return Status.RUNNING
    
    async def error_state(self, blackboard):
        """错误状态"""
        print(f"状态机 {self.name}: 错误状态")
        await asyncio.sleep(0.5)
        
        # 尝试恢复
        if random.random() < 0.7:  # 70%恢复概率
            self.current_state = "recovery"
            return Status.SUCCESS
        else:
            self.current_state = "idle"
            return Status.FAILURE
    
    async def recovery_state(self, blackboard):
        """恢复状态"""
        print(f"状态机 {self.name}: 恢复状态")
        await asyncio.sleep(0.4)
        
        self.current_state = "working"
        return Status.SUCCESS
    
    async def tick(self, blackboard):
        """执行当前状态"""
        if self.current_state in self.states:
            return await self.states[self.current_state](blackboard)
        return Status.FAILURE


class EventDrivenController(BaseNode):
    """事件驱动控制器"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.event_queue = []
        self.event_handlers = {
            "emergency": self.handle_emergency,
            "normal": self.handle_normal,
            "maintenance": self.handle_maintenance
        }
    
    def add_event(self, event_type, priority=1):
        """添加事件到队列"""
        self.event_queue.append((priority, time.time(), event_type))
        self.event_queue.sort(key=lambda x: (-x[0], x[1]))  # 按优先级和时间排序
    
    async def handle_emergency(self, blackboard):
        """处理紧急事件"""
        print(f"事件控制器 {self.name}: 处理紧急事件")
        await asyncio.sleep(0.2)
        
        # 设置紧急状态
        blackboard.set("emergency_mode", True)
        blackboard.set("last_emergency", time.time())
        
        return Status.SUCCESS
    
    async def handle_normal(self, blackboard):
        """处理正常事件"""
        print(f"事件控制器 {self.name}: 处理正常事件")
        await asyncio.sleep(0.1)
        
        # 更新正常状态
        blackboard.set("normal_events_processed", blackboard.get("normal_events_processed", 0) + 1)
        
        return Status.SUCCESS
    
    async def handle_maintenance(self, blackboard):
        """处理维护事件"""
        print(f"事件控制器 {self.name}: 处理维护事件")
        await asyncio.sleep(0.3)
        
        # 执行维护
        blackboard.set("maintenance_done", True)
        blackboard.set("last_maintenance", time.time())
        
        return Status.SUCCESS
    
    async def tick(self, blackboard):
        """处理事件队列"""
        if not self.event_queue:
            return Status.SUCCESS
        
        # 获取最高优先级事件
        priority, timestamp, event_type = self.event_queue.pop(0)
        
        if event_type in self.event_handlers:
            return await self.event_handlers[event_type](blackboard)
        
        return Status.FAILURE


class PriorityQueue(BaseNode):
    """优先级队列"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.tasks = []
        self.current_task = None
    
    def add_task(self, task, priority=1):
        """添加任务到队列"""
        self.tasks.append((priority, time.time(), task))
        self.tasks.sort(key=lambda x: (-x[0], x[1]))
    
    async def tick(self, blackboard):
        """执行最高优先级任务"""
        if self.current_task:
            # 继续执行当前任务
            result = await self.current_task.tick(blackboard)
            if result != Status.RUNNING:
                self.current_task = None
            return result
        
        if not self.tasks:
            return Status.SUCCESS
        
        # 开始执行新任务
        priority, timestamp, task = self.tasks.pop(0)
        self.current_task = task
        
        print(f"优先级队列 {self.name}: 开始执行任务 {task.name} (优先级: {priority})")
        return await task.tick(blackboard)


class DynamicDecisionMaker(BaseNode):
    """动态决策器"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.decision_history = []
        self.adaptation_factor = 1.0
    
    async def tick(self, blackboard):
        """根据当前状态做出动态决策"""
        print(f"动态决策器 {self.name}: 分析当前状态")
        
        # 获取当前状态信息
        battery_level = blackboard.get("battery_level", 100)
        workload = blackboard.get("workload", 0)
        error_rate = blackboard.get("error_rate", 0)
        
        # 计算决策权重
        battery_weight = max(0, (100 - battery_level) / 100)
        workload_weight = workload / 100
        error_weight = error_rate / 100
        
        # 动态调整适应因子
        if error_rate > 0.5:
            self.adaptation_factor *= 0.9  # 降低适应因子
        elif error_rate < 0.1:
            self.adaptation_factor *= 1.1  # 提高适应因子
        
        self.adaptation_factor = max(0.1, min(2.0, self.adaptation_factor))
        
        # 根据权重做出决策
        if battery_weight > 0.7:
            decision = "charge"
        elif workload_weight > 0.8:
            decision = "optimize"
        elif error_weight > 0.6:
            decision = "maintenance"
        else:
            decision = "normal"
        
        # 记录决策历史
        self.decision_history.append({
            "timestamp": time.time(),
            "decision": decision,
            "factors": {
                "battery": battery_level,
                "workload": workload,
                "error_rate": error_rate
            }
        })
        
        # 限制历史记录长度
        if len(self.decision_history) > 10:
            self.decision_history.pop(0)
        
        # 设置决策结果
        blackboard.set("current_decision", decision)
        blackboard.set("adaptation_factor", self.adaptation_factor)
        
        print(f"动态决策器 {self.name}: 决策为 {decision}, 适应因子: {self.adaptation_factor:.2f}")
        
        return Status.SUCCESS


# 测试用的动作节点
class ChargeAction(Action):
    """充电动作"""
    
    async def execute(self, blackboard):
        print("执行充电操作...")
        await asyncio.sleep(0.5)
        
        current_battery = blackboard.get("battery_level", 0)
        new_battery = min(100, current_battery + 30)
        blackboard.set("battery_level", new_battery)
        
        print(f"充电完成，电池电量: {new_battery}%")
        return Status.SUCCESS


class OptimizeAction(Action):
    """优化动作"""
    
    async def execute(self, blackboard):
        print("执行优化操作...")
        await asyncio.sleep(0.3)
        
        current_workload = blackboard.get("workload", 0)
        new_workload = max(0, current_workload - 20)
        blackboard.set("workload", new_workload)
        
        print(f"优化完成，工作负载: {new_workload}%")
        return Status.SUCCESS


class MaintenanceAction(Action):
    """维护动作"""
    
    async def execute(self, blackboard):
        print("执行维护操作...")
        await asyncio.sleep(0.4)
        
        current_error_rate = blackboard.get("error_rate", 0)
        new_error_rate = max(0, current_error_rate - 0.3)
        blackboard.set("error_rate", new_error_rate)
        
        print(f"维护完成，错误率: {new_error_rate:.2f}")
        return Status.SUCCESS


async def main():
    """主函数 - 演示高级控制流"""
    
    # 注册自定义节点类型
    register_custom_nodes()
    
    print("=== ABTree 高级控制流示例 ===\n")
    
    # 1. 创建状态机
    state_machine = StateMachine("工作状态机")
    
    # 2. 创建事件驱动控制器
    event_controller = EventDrivenController("事件控制器")
    
    # 3. 创建优先级队列
    priority_queue = PriorityQueue("任务队列")
    
    # 4. 创建动态决策器
    decision_maker = DynamicDecisionMaker("决策器")
    
    # 5. 创建行为树
    root = Selector("高级控制流")
    
    # 状态机分支
    state_branch = Sequence("状态机分支")
    state_branch.add_child(state_machine)
    
    # 事件处理分支
    event_branch = Sequence("事件处理分支")
    event_branch.add_child(event_controller)
    
    # 优先级任务分支
    priority_branch = Sequence("优先级任务分支")
    priority_branch.add_child(priority_queue)
    
    # 动态决策分支
    decision_branch = Sequence("动态决策分支")
    decision_branch.add_child(decision_maker)
    
    # 6. 组装行为树
    root.add_child(state_branch)
    root.add_child(event_branch)
    root.add_child(priority_branch)
    root.add_child(decision_branch)
    
    # 3. Create behavior tree
    tree = BehaviorTree()
    tree.load_from_root(root)
    blackboard = tree.blackboard
    
    # 8. 初始化数据
    blackboard.set("battery_level", 60)
    blackboard.set("workload", 80)
    blackboard.set("error_rate", 0.3)
    blackboard.set("has_work", True)
    blackboard.set("work_progress", 0)
    
    # 9. 添加一些事件和任务
    event_controller.add_event("normal", 1)
    event_controller.add_event("maintenance", 2)
    
    priority_queue.add_task(ChargeAction("充电任务"), 3)
    priority_queue.add_task(OptimizeAction("优化任务"), 2)
    priority_queue.add_task(MaintenanceAction("维护任务"), 1)
    
    print("开始执行高级控制流...")
    print("=" * 50)
    
    # 10. 执行多轮测试
    for i in range(5):
        print(f"\n--- 第 {i+1} 轮执行 ---")
        result = await tree.tick()
        print(f"执行结果: {result}")
        
        # 更新状态
        blackboard.set("battery_level", max(0, blackboard.get("battery_level", 100) - 10))
        blackboard.set("workload", min(100, blackboard.get("workload", 0) + 5))
        blackboard.set("error_rate", min(1.0, blackboard.get("error_rate", 0) + 0.1))
        
        # 添加新事件
        if i % 2 == 0:
            event_controller.add_event("normal", 1)
        if i % 3 == 0:
            event_controller.add_event("emergency", 3)
    
    print("\n=== 最终状态 ===")
    print(f"电池电量: {blackboard.get('battery_level')}%")
    print(f"工作负载: {blackboard.get('workload')}%")
    print(f"错误率: {blackboard.get('error_rate'):.2f}")
    print(f"当前决策: {blackboard.get('current_decision')}")
    print(f"适应因子: {blackboard.get('adaptation_factor', 1.0):.2f}")
    
    # 11. 演示XML配置方式
    print("\n=== XML配置方式演示 ===")
    
    # XML字符串配置
    xml_config = '''
    <BehaviorTree name="ControlFlowAdvancedXML" description="XML配置的高级控制流示例">
        <Sequence name="根序列">
            <Selector name="高级控制流">
                <Sequence name="状态机分支">
                    <StateMachine name="工作状态机" />
                </Sequence>
                <Sequence name="事件处理分支">
                    <EventDrivenController name="事件控制器" />
                </Sequence>
                <Sequence name="优先级任务分支">
                    <PriorityQueue name="任务队列" />
                </Sequence>
                <Sequence name="动态决策分支">
                    <DynamicDecisionMaker name="决策器" />
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
    xml_blackboard.set("battery_level", 70)
    xml_blackboard.set("workload", 60)
    xml_blackboard.set("error_rate", 0.2)
    xml_blackboard.set("has_work", True)
    xml_blackboard.set("work_progress", 0)
    
    print("通过XML字符串配置的行为树:")
    print(xml_config.strip())
    print("\n开始执行XML配置的行为树...")
    xml_result = await xml_tree.tick()
    print(f"XML配置执行完成! 结果: {xml_result}")
    print(f"XML配置电池电量: {xml_blackboard.get('battery_level')}%")


if __name__ == "__main__":
    asyncio.run(main()) 