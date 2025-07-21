#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 08: Composite Nodes in Depth – Using Various Composite Nodes

Demonstrates how to create and use different types of composite nodes.
Composite nodes combine multiple child nodes to implement complex control logic.

Key Learning Points:

    Basic structure of composite nodes

    Parallel execution mechanisms

    Priority handling

    Child node management

    Complex combination logic

    How to configure composite nodes using XML strings
"""

import asyncio
import random
from abtree import BehaviorTree, Sequence, Selector, Action, Condition, register_node
from abtree.core import Status
from abtree.parser.xml_parser import XMLParser


# 注册自定义节点类型
def register_custom_nodes():
    """注册自定义节点类型"""
    register_node("TestAction", TestAction)
    register_node("TestCondition", TestCondition)


class ParallelNode:
    """并行节点 - 同时执行多个子节点"""
    
    def __init__(self, name, children=None, success_policy="ALL", failure_policy="ANY"):
        self.name = name
        self.children = children or []
        self.success_policy = success_policy  # "ALL", "ANY", "MAJORITY"
        self.failure_policy = failure_policy  # "ALL", "ANY", "MAJORITY"
    
    def add_child(self, child):
        self.children.append(child)
    
    async def tick(self, blackboard):
        print(f"并行节点 {self.name}: 开始执行 {len(self.children)} 个子节点")
        
        # 同时执行所有子节点
        tasks = [child.tick(blackboard) for child in self.children]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
        success_count = sum(1 for r in results if r == Status.SUCCESS)
        failure_count = sum(1 for r in results if r == Status.FAILURE)
        running_count = sum(1 for r in results if r == Status.RUNNING)
        
        print(f"并行节点 {self.name}: 成功={success_count}, 失败={failure_count}, 运行中={running_count}")
        
        # 根据策略决定最终结果
        if self.success_policy == "ALL":
            success = success_count == len(self.children)
        elif self.success_policy == "ANY":
            success = success_count > 0
        elif self.success_policy == "MAJORITY":
            success = success_count > len(self.children) // 2
        else:
            success = False
        
        if self.failure_policy == "ALL":
            failure = failure_count == len(self.children)
        elif self.failure_policy == "ANY":
            failure = failure_count > 0
        elif self.failure_policy == "MAJORITY":
            failure = failure_count > len(self.children) // 2
        else:
            failure = False
        
        if failure:
            return Status.FAILURE
        elif success:
            return Status.SUCCESS
        else:
            return Status.RUNNING


class PriorityNode:
    """优先级节点 - 按优先级顺序执行子节点"""
    
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []
        self.current_index = 0
    
    def add_child(self, child):
        self.children.append(child)
    
    async def tick(self, blackboard):
        print(f"优先级节点 {self.name}: 当前索引 {self.current_index}")
        
        # 从当前索引开始尝试执行子节点
        for i in range(self.current_index, len(self.children)):
            child = self.children[i]
            print(f"优先级节点 {self.name}: 尝试执行子节点 {i}: {child.name}")
            
            result = await child.tick(blackboard)
            
            if result == Status.SUCCESS:
                print(f"优先级节点 {self.name}: 子节点 {i} 成功，重置索引")
                self.current_index = 0
                return Status.SUCCESS
            elif result == Status.RUNNING:
                print(f"优先级节点 {self.name}: 子节点 {i} 运行中，保持索引")
                self.current_index = i
                return Status.RUNNING
            else:  # FAILURE
                print(f"优先级节点 {self.name}: 子节点 {i} 失败，尝试下一个")
                continue
        
        # 所有子节点都失败
        print(f"优先级节点 {self.name}: 所有子节点都失败")
        self.current_index = 0
        return Status.FAILURE


class RandomSelector:
    """随机选择器 - 随机选择一个子节点执行"""
    
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []
    
    def add_child(self, child):
        self.children.append(child)
    
    async def tick(self, blackboard):
        if not self.children:
            return Status.FAILURE
        
        # 随机选择一个子节点
        selected_child = random.choice(self.children)
        print(f"随机选择器 {self.name}: 选择子节点 {selected_child.name}")
        
        result = await selected_child.tick(blackboard)
        print(f"随机选择器 {self.name}: 子节点返回 {result}")
        
        return result


class MemorySequence:
    """记忆序列 - 记住上次执行的位置"""
    
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []
        self.current_index = 0
    
    def add_child(self, child):
        self.children.append(child)
    
    async def tick(self, blackboard):
        print(f"记忆序列 {self.name}: 从位置 {self.current_index} 开始")
        
        # 从记忆的位置开始执行
        for i in range(self.current_index, len(self.children)):
            child = self.children[i]
            print(f"记忆序列 {self.name}: 执行子节点 {i}: {child.name}")
            
            result = await child.tick(blackboard)
            
            if result == Status.SUCCESS:
                print(f"记忆序列 {self.name}: 子节点 {i} 成功，继续下一个")
                continue
            elif result == Status.RUNNING:
                print(f"记忆序列 {self.name}: 子节点 {i} 运行中，记住位置")
                self.current_index = i
                return Status.RUNNING
            else:  # FAILURE
                print(f"记忆序列 {self.name}: 子节点 {i} 失败，重置位置")
                self.current_index = 0
                return Status.FAILURE
        
        # 所有子节点都成功
        print(f"记忆序列 {self.name}: 所有子节点都成功，重置位置")
        self.current_index = 0
        return Status.SUCCESS


class WeightedSelector:
    """加权选择器 - 根据权重选择子节点"""
    
    def __init__(self, name, children=None, weights=None):
        self.name = name
        self.children = children or []
        self.weights = weights or [1] * len(self.children)
    
    def add_child(self, child, weight=1):
        self.children.append(child)
        self.weights.append(weight)
    
    async def tick(self, blackboard):
        if not self.children:
            return Status.FAILURE
        
        # 根据权重随机选择
        total_weight = sum(self.weights)
        rand_val = random.uniform(0, total_weight)
        
        cumulative_weight = 0
        selected_index = 0
        
        for i, weight in enumerate(self.weights):
            cumulative_weight += weight
            if rand_val <= cumulative_weight:
                selected_index = i
                break
        
        selected_child = self.children[selected_index]
        print(f"加权选择器 {self.name}: 选择子节点 {selected_child.name} (权重: {self.weights[selected_index]})")
        
        result = await selected_child.tick(blackboard)
        print(f"加权选择器 {self.name}: 子节点返回 {result}")
        
        return result


# 测试用的动作和条件节点
class TestAction(Action):
    """测试动作节点"""
    
    def __init__(self, name, success_rate=0.8, duration=0.5):
        super().__init__(name)
        self.success_rate = success_rate
        self.duration = duration
    
    async def execute(self, blackboard):
        print(f"执行测试动作: {self.name}")
        await asyncio.sleep(self.duration)
        
        success = random.random() < self.success_rate
        result = Status.SUCCESS if success else Status.FAILURE
        print(f"测试动作 {self.name}: {'成功' if success else '失败'}")
        
        return result


class TestCondition(Condition):
    """测试条件节点"""
    
    def __init__(self, name, success_rate=0.7):
        super().__init__(name)
        self.success_rate = success_rate
    
    async def evaluate(self, blackboard):
        print(f"检查测试条件: {self.name}")
        
        success = random.random() < self.success_rate
        print(f"测试条件 {self.name}: {'满足' if success else '不满足'}")
        
        return success


async def main():
    """主函数 - 演示各种复合节点的使用"""
    
    # 注册自定义节点类型
    register_custom_nodes()
    
    print("=== ABTree 复合节点详解示例 ===\n")
    
    # 1. 测试并行节点
    print("=== 并行节点测试 ===")
    parallel = ParallelNode("并行测试", success_policy="ANY", failure_policy="ANY")
    parallel.add_child(TestAction("并行动作1", 0.8, 0.3))
    parallel.add_child(TestAction("并行动作2", 0.6, 0.4))
    parallel.add_child(TestAction("并行动作3", 0.9, 0.2))
    
    tree1 = BehaviorTree()
    tree1.load_from_root(parallel)
    result1 = await tree1.tick()
    print(f"并行节点结果: {result1}\n")
    
    # 2. 测试优先级节点
    print("=== 优先级节点测试 ===")
    priority = PriorityNode("优先级测试")
    priority.add_child(TestAction("高优先级动作", 0.3, 0.2))  # 低成功率
    priority.add_child(TestAction("中优先级动作", 0.7, 0.2))
    priority.add_child(TestAction("低优先级动作", 0.9, 0.2))
    
    tree2 = BehaviorTree()
    tree2.load_from_root(priority)
    result2 = await tree2.tick()
    print(f"优先级节点结果: {result2}\n")
    
    # 3. 测试随机选择器
    print("=== 随机选择器测试 ===")
    random_selector = RandomSelector("随机测试")
    random_selector.add_child(TestAction("随机动作1", 0.8, 0.2))
    random_selector.add_child(TestAction("随机动作2", 0.8, 0.2))
    random_selector.add_child(TestAction("随机动作3", 0.8, 0.2))
    
    tree3 = BehaviorTree()
    tree3.load_from_root(random_selector)
    result3 = await tree3.tick()
    print(f"随机选择器结果: {result3}\n")
    
    # 4. 测试记忆序列
    print("=== 记忆序列测试 ===")
    memory_sequence = MemorySequence("记忆测试")
    memory_sequence.add_child(TestAction("记忆动作1", 0.9, 0.2))
    memory_sequence.add_child(TestAction("记忆动作2", 0.9, 0.2))
    memory_sequence.add_child(TestAction("记忆动作3", 0.9, 0.2))
    
    tree4 = BehaviorTree()
    tree4.load_from_root(memory_sequence)
    result4 = await tree4.tick()
    print(f"记忆序列结果: {result4}\n")
    
    # 5. 测试加权选择器
    print("=== 加权选择器测试 ===")
    weighted_selector = WeightedSelector("加权测试")
    weighted_selector.add_child(TestAction("高权重动作", 0.8, 0.2), 3)
    weighted_selector.add_child(TestAction("中权重动作", 0.8, 0.2), 2)
    weighted_selector.add_child(TestAction("低权重动作", 0.8, 0.2), 1)
    
    tree5 = BehaviorTree()
    tree5.load_from_root(weighted_selector)
    result5 = await tree5.tick()
    print(f"加权选择器结果: {result5}\n")
    
    print("所有复合节点测试完成!")
    
    # 6. 演示XML配置方式
    print("\n=== XML配置方式演示 ===")
    
    # XML字符串配置
    xml_config = '''
    <BehaviorTree name="CompositeNodesXML" description="XML配置的复合节点示例">
        <Sequence name="根序列">
            <Selector name="复合节点测试">
                <Sequence name="基础序列">
                    <TestCondition name="测试条件1" success_rate="0.8" />
                    <TestAction name="测试动作1" success_rate="0.9" duration="0.3" />
                    <TestAction name="测试动作2" success_rate="0.8" duration="0.2" />
                </Sequence>
                <Sequence name="备用序列">
                    <TestAction name="备用动作1" success_rate="0.7" duration="0.2" />
                    <TestAction name="备用动作2" success_rate="0.8" duration="0.3" />
                </Sequence>
            </Selector>
        </Sequence>
    </BehaviorTree>
    '''
    
    # 解析XML配置
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    
    print("通过XML字符串配置的行为树:")
    print(xml_config.strip())
    print("\n开始执行XML配置的行为树...")
    xml_result = await xml_tree.tick()
    print(f"XML配置执行完成! 结果: {xml_result}")


if __name__ == "__main__":
    asyncio.run(main()) 