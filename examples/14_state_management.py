#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 12: State Management – Complex State Handling

Demonstrates how to use ABTree for advanced state management, including transitions, persistence, and synchronization.
State management is a critical part of complex systems.

Key Learning Points:

    State transition logic

    State persistence

    State synchronization

    State recovery

    State monitoring

    How to configure state management using XML strings
"""

import asyncio
import json
import time
import random
from pathlib import Path
from abtree import BehaviorTree, Sequence, Selector, Action, Condition, register_node
from abtree.core import Status
from abtree.nodes.base import BaseNode
from abtree.parser.xml_parser import XMLParser


# 注册自定义节点类型
def register_custom_nodes():
    """注册自定义节点类型"""
    register_node("StateTransitionAction", StateTransitionAction)
    register_node("StateCondition", StateCondition)
    register_node("StateMonitoringAction", StateMonitoringAction)
    register_node("StateRecoveryAction", StateRecoveryAction)
    register_node("StatePersistenceAction", StatePersistenceAction)
    register_node("StateLoadAction", StateLoadAction)
    register_node("ErrorDetectionCondition", ErrorDetectionCondition)
    register_node("MaintenanceRequiredCondition", MaintenanceRequiredCondition)
    register_node("WorkingStateAction", WorkingStateAction)
    register_node("MaintenanceAction", MaintenanceAction)


class StateManager:
    """状态管理器 - 管理复杂的状态转换和持久化"""
    
    def __init__(self, name, initial_state="idle"):
        self.name = name
        self.current_state = initial_state
        self.previous_state = None
        self.state_history = []
        self.state_transitions = {
            "idle": ["working", "maintenance", "error"],
            "working": ["idle", "maintenance", "error", "paused"],
            "maintenance": ["idle", "working"],
            "error": ["idle", "maintenance"],
            "paused": ["working", "idle"]
        }
        self.state_data = {}
        self.last_state_change = time.time()
    
    def can_transition_to(self, target_state):
        """检查是否可以转换到目标状态"""
        if self.current_state in self.state_transitions:
            return target_state in self.state_transitions[self.current_state]
        return False
    
    def transition_to(self, new_state, data=None):
        """转换到新状态"""
        if self.can_transition_to(new_state):
            self.previous_state = self.current_state
            self.current_state = new_state
            self.last_state_change = time.time()
            
            # 记录状态历史
            self.state_history.append({
                'from_state': self.previous_state,
                'to_state': new_state,
                'timestamp': time.time(),
                'data': data
            })
            
            # 限制历史记录长度
            if len(self.state_history) > 50:
                self.state_history.pop(0)
            
            print(f"状态管理器 {self.name}: {self.previous_state} -> {new_state}")
            return True
        else:
            print(f"状态管理器 {self.name}: 无法从 {self.current_state} 转换到 {new_state}")
            return False
    
    def get_state_duration(self):
        """获取当前状态持续时间"""
        return time.time() - self.last_state_change
    
    def save_state(self, filepath):
        """保存状态到文件"""
        state_data = {
            'current_state': self.current_state,
            'previous_state': self.previous_state,
            'last_state_change': self.last_state_change,
            'state_data': self.state_data,
            'state_history': self.state_history[-10:]  # 只保存最近10条
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            print(f"状态管理器 {self.name}: 状态已保存到 {filepath}")
            return True
        except Exception as e:
            print(f"状态管理器 {self.name}: 保存状态失败: {e}")
            return False
    
    def load_state(self, filepath):
        """从文件加载状态"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            self.current_state = state_data.get('current_state', 'idle')
            self.previous_state = state_data.get('previous_state', None)
            self.last_state_change = state_data.get('last_state_change', time.time())
            self.state_data = state_data.get('state_data', {})
            self.state_history = state_data.get('state_history', [])
            
            print(f"状态管理器 {self.name}: 状态已从 {filepath} 加载")
            return True
        except Exception as e:
            print(f"状态管理器 {self.name}: 加载状态失败: {e}")
            return False


class StateTransitionAction(Action):
    """状态转换动作"""
    
    def __init__(self, name, target_state, state_manager=None, condition_func=None, **kwargs):
        super().__init__(name, **kwargs)
        self.state_manager = state_manager
        self.target_state = target_state
        self.condition_func = condition_func
    
    async def execute(self, blackboard):
        if self.state_manager is None:
            print(f"状态转换动作 {self.name}: 无状态管理器")
            return Status.FAILURE
        
        print(f"状态转换动作 {self.name}: 尝试转换到 {self.target_state}")
        
        # 检查转换条件
        if self.condition_func and not self.condition_func(blackboard):
            print(f"状态转换动作 {self.name}: 转换条件不满足")
            return Status.FAILURE
        
        # 执行状态转换
        if self.state_manager.transition_to(self.target_state):
            print(f"状态转换动作 {self.name}: 转换成功")
            return Status.SUCCESS
        else:
            print(f"状态转换动作 {self.name}: 转换失败")
            return Status.FAILURE


class StateCondition(Condition):
    """状态条件节点"""
    
    def __init__(self, name, expected_state, state_manager=None, duration_check=None, **kwargs):
        super().__init__(name, **kwargs)
        self.state_manager = state_manager
        self.expected_state = expected_state
        self.duration_check = duration_check  # 最小持续时间
    
    async def evaluate(self, blackboard):
        if self.state_manager is None:
            print(f"状态条件 {self.name}: 无状态管理器")
            return False
        
        current_state = self.state_manager.current_state
        state_match = current_state == self.expected_state
        
        if state_match and self.duration_check:
            duration = self.state_manager.get_state_duration()
            duration_ok = duration >= self.duration_check
            print(f"状态条件 {self.name}: 状态={current_state}, 持续时间={duration:.1f}s")
            return duration_ok
        else:
            print(f"状态条件 {self.name}: 当前状态={current_state}, 期望状态={self.expected_state}")
            return state_match


class StateMonitoringAction(Action):
    """状态监控动作"""
    
    def __init__(self, name, state_manager=None, **kwargs):
        super().__init__(name, **kwargs)
        self.state_manager = state_manager
    
    async def execute(self, blackboard):
        if self.state_manager is None:
            print(f"状态监控动作 {self.name}: 无状态管理器")
            return Status.FAILURE
        
        print(f"状态监控动作 {self.name}: 监控当前状态")
        
        # 收集状态信息
        state_info = {
            'current_state': self.state_manager.current_state,
            'previous_state': self.state_manager.previous_state,
            'state_duration': self.state_manager.get_state_duration(),
            'history_count': len(self.state_manager.state_history),
            'timestamp': time.time()
        }
        
        # 更新黑板
        blackboard.set("state_info", state_info)
        blackboard.set("last_monitoring", time.time())
        
        print(f"状态监控动作 {self.name}: 状态信息已更新")
        return Status.SUCCESS


class StateRecoveryAction(Action):
    """状态恢复动作"""
    
    def __init__(self, name, recovery_state="idle", state_manager=None, **kwargs):
        super().__init__(name, **kwargs)
        self.state_manager = state_manager
        self.recovery_state = recovery_state
    
    async def execute(self, blackboard):
        if self.state_manager is None:
            print(f"状态恢复动作 {self.name}: 无状态管理器")
            return Status.FAILURE
        
        print(f"状态恢复动作 {self.name}: 尝试恢复到 {self.recovery_state}")
        
        # 检查当前状态是否为错误状态
        if self.state_manager.current_state == "error":
            # 尝试恢复
            if self.state_manager.transition_to(self.recovery_state):
                print(f"状态恢复动作 {self.name}: 恢复成功")
                blackboard.set("recovery_successful", True)
                return Status.SUCCESS
            else:
                print(f"状态恢复动作 {self.name}: 恢复失败")
                blackboard.set("recovery_successful", False)
                return Status.FAILURE
        else:
            print(f"状态恢复动作 {self.name}: 当前不是错误状态，无需恢复")
            return Status.SUCCESS


class StatePersistenceAction(Action):
    """状态持久化动作"""
    
    def __init__(self, name, filepath, state_manager=None, **kwargs):
        super().__init__(name, **kwargs)
        self.state_manager = state_manager
        self.filepath = filepath
    
    async def execute(self, blackboard):
        if self.state_manager is None:
            print(f"状态持久化动作 {self.name}: 无状态管理器")
            return Status.FAILURE
        
        print(f"状态持久化动作 {self.name}: 保存状态到 {self.filepath}")
        
        success = self.state_manager.save_state(self.filepath)
        blackboard.set("state_saved", success)
        
        if success:
            print(f"状态持久化动作 {self.name}: 保存成功")
            return Status.SUCCESS
        else:
            print(f"状态持久化动作 {self.name}: 保存失败")
            return Status.FAILURE


class StateLoadAction(Action):
    """状态加载动作"""
    
    def __init__(self, name, filepath, state_manager=None, **kwargs):
        super().__init__(name, **kwargs)
        self.state_manager = state_manager
        self.filepath = filepath
    
    async def execute(self, blackboard):
        if self.state_manager is None:
            print(f"状态加载动作 {self.name}: 无状态管理器")
            return Status.FAILURE
        
        print(f"状态加载动作 {self.name}: 从 {self.filepath} 加载状态")
        
        success = self.state_manager.load_state(self.filepath)
        blackboard.set("state_loaded", success)
        
        if success:
            print(f"状态加载动作 {self.name}: 加载成功")
            return Status.SUCCESS
        else:
            print(f"状态加载动作 {self.name}: 加载失败")
            return Status.FAILURE


class ErrorDetectionCondition(Condition):
    """错误检测条件"""
    
    def __init__(self, name, error_threshold=3):
        super().__init__(name)
        self.error_threshold = error_threshold
    
    async def evaluate(self, blackboard):
        error_count = blackboard.get("error_count", 0)
        print(f"错误检测条件 {self.name}: 错误计数={error_count}, 阈值={self.error_threshold}")
        return error_count >= self.error_threshold


class MaintenanceRequiredCondition(Condition):
    """维护需求条件"""
    
    def __init__(self, name, maintenance_interval=300):  # 5分钟
        super().__init__(name)
        self.maintenance_interval = maintenance_interval
    
    async def evaluate(self, blackboard):
        last_maintenance = blackboard.get("last_maintenance", 0)
        current_time = time.time()
        time_since_maintenance = current_time - last_maintenance
        
        print(f"维护需求条件 {self.name}: 距离上次维护 {time_since_maintenance:.1f}s")
        return time_since_maintenance >= self.maintenance_interval


class WorkingStateAction(Action):
    """工作状态动作"""
    
    async def execute(self, blackboard):
        print("执行工作状态动作...")
        await asyncio.sleep(0.3)
        
        # 模拟工作过程
        work_progress = blackboard.get("work_progress", 0)
        work_progress += random.randint(5, 15)
        blackboard.set("work_progress", work_progress)
        
        # 模拟可能的错误
        if random.random() < 0.1:  # 10%错误概率
            error_count = blackboard.get("error_count", 0) + 1
            blackboard.set("error_count", error_count)
            print(f"工作过程中发生错误，错误计数: {error_count}")
        
        print(f"工作进度: {work_progress}%")
        return Status.SUCCESS


class MaintenanceAction(Action):
    """维护动作"""
    
    async def execute(self, blackboard):
        print("执行维护动作...")
        await asyncio.sleep(0.5)
        
        # 执行维护
        blackboard.set("last_maintenance", time.time())
        blackboard.set("maintenance_count", blackboard.get("maintenance_count", 0) + 1)
        blackboard.set("error_count", 0)  # 重置错误计数
        
        print("维护完成")
        return Status.SUCCESS


async def main():
    """主函数 - 演示状态管理"""
    
    # 注册自定义节点类型
    register_custom_nodes()
    
    print("=== ABTree 状态管理示例 ===\n")
    
    # 1. 创建状态管理器
    state_manager = StateManager("系统状态管理器", "idle")
    
    # 2. 创建行为树
    root = Selector("状态管理系统")
    
    # 3. 创建各种状态分支
    # 错误恢复分支
    error_recovery = Sequence("错误恢复")
    error_recovery.add_child(ErrorDetectionCondition("检测错误", 2))
    error_transition = StateTransitionAction("转换到错误状态", "error")
    error_transition.state_manager = state_manager
    error_recovery.add_child(error_transition)
    error_recovery_action = StateRecoveryAction("恢复状态", "idle")
    error_recovery_action.state_manager = state_manager
    error_recovery.add_child(error_recovery_action)
    
    # 维护分支
    maintenance_branch = Sequence("维护分支")
    maintenance_branch.add_child(MaintenanceRequiredCondition("检查维护需求", 60))  # 1分钟
    maintenance_transition = StateTransitionAction("转换到维护状态", "maintenance")
    maintenance_transition.state_manager = state_manager
    maintenance_branch.add_child(maintenance_transition)
    maintenance_branch.add_child(MaintenanceAction("执行维护"))
    work_transition = StateTransitionAction("转换到工作状态", "working")
    work_transition.state_manager = state_manager
    maintenance_branch.add_child(work_transition)
    
    # 工作分支
    work_branch = Sequence("工作分支")
    state_condition = StateCondition("检查是否空闲", "idle")
    state_condition.state_manager = state_manager
    work_branch.add_child(state_condition)
    start_work_transition = StateTransitionAction("开始工作", "working")
    start_work_transition.state_manager = state_manager
    work_branch.add_child(start_work_transition)
    work_branch.add_child(WorkingStateAction("执行工作"))
    
    # 状态监控分支
    monitoring_branch = Sequence("状态监控")
    monitoring_action = StateMonitoringAction("监控状态")
    monitoring_action.state_manager = state_manager
    monitoring_branch.add_child(monitoring_action)
    
    # 状态持久化分支
    persistence_branch = Sequence("状态持久化")
    persistence_action = StatePersistenceAction("保存状态", "state_backup.json")
    persistence_action.state_manager = state_manager
    persistence_branch.add_child(persistence_action)
    
    # 4. 组装行为树
    root.add_child(error_recovery)
    root.add_child(maintenance_branch)
    root.add_child(work_branch)
    root.add_child(monitoring_branch)
    root.add_child(persistence_branch)
    
    # 5. 创建行为树实例
    tree = BehaviorTree()
    tree.load_from_root(root)
    blackboard = tree.blackboard
    
    # 6. 初始化数据
    blackboard.set("work_progress", 0)
    blackboard.set("error_count", 0)
    blackboard.set("maintenance_count", 0)
    blackboard.set("last_maintenance", time.time())
    
    print("开始执行状态管理系统...")
    print("=" * 50)
    
    # 7. 执行多轮测试
    for i in range(15):
        print(f"\n--- 第 {i+1} 轮执行 ---")
        
        # 执行行为树
        result = await tree.tick()
        print(f"执行结果: {result}")
        
        # 显示当前状态
        state_info = blackboard.get("state_info", {})
        print(f"当前状态: {state_info.get('current_state', 'unknown')}")
        print(f"工作进度: {blackboard.get('work_progress')}%")
        print(f"错误计数: {blackboard.get('error_count')}")
        print(f"维护次数: {blackboard.get('maintenance_count')}")
        
        # 模拟一些外部事件
        if i % 3 == 0:
            # 模拟错误
            error_count = blackboard.get("error_count", 0) + 1
            blackboard.set("error_count", error_count)
            print(f"模拟错误发生，错误计数: {error_count}")
        
        await asyncio.sleep(0.3)
    
    # 8. 演示状态加载
    print("\n=== 演示状态加载 ===")
    if Path("state_backup.json").exists():
        load_action = StateLoadAction("加载状态", "state_backup.json")
        load_action.state_manager = state_manager
        await load_action.execute(blackboard)
        print(f"加载后的状态: {state_manager.current_state}")
    
    print("\n=== 最终状态 ===")
    print(f"最终状态: {state_manager.current_state}")
    print(f"状态历史记录数: {len(state_manager.state_history)}")
    print(f"总工作进度: {blackboard.get('work_progress')}%")
    print(f"总错误次数: {blackboard.get('error_count')}")
    print(f"总维护次数: {blackboard.get('maintenance_count')}")
    
    # 9. 演示XML配置方式
    print("\n=== XML配置方式演示 ===")
    
    # XML字符串配置
    xml_config = '''
    <BehaviorTree name="StateManagementXML" description="XML配置的状态管理示例">
        <Sequence name="根序列">
            <Selector name="状态管理系统">
                <Sequence name="工作分支">
                    <StateCondition name="检查是否空闲" expected_state="idle" />
                    <StateTransitionAction name="开始工作" target_state="working" />
                    <WorkingStateAction name="执行工作" />
                </Sequence>
                <Sequence name="状态监控">
                    <StateMonitoringAction name="监控状态" />
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
    xml_blackboard.set("work_progress", 0)
    xml_blackboard.set("error_count", 0)
    xml_blackboard.set("maintenance_count", 0)
    xml_blackboard.set("last_maintenance", time.time())
    
    print("通过XML字符串配置的行为树:")
    print(xml_config.strip())
    print("\n开始执行XML配置的行为树...")
    xml_result = await xml_tree.tick()
    print(f"XML配置执行完成! 结果: {xml_result}")
    print(f"XML配置工作进度: {xml_blackboard.get('work_progress')}%")


if __name__ == "__main__":
    asyncio.run(main()) 