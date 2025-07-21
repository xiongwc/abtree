#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 09: Control Flow Basics – Understanding Basic Control Flow Concepts

Demonstrates the basic control flow concepts in behavior trees, including sequence, conditional branching, and loops.
This is the foundation for understanding complex control flows.

Key Learning Points:

    Sequential control flow

    Conditional branching control

    Looping control

    State management

    Error handling workflows

    How to configure control flows using XML strings
"""

import asyncio
import random
from abtree import BehaviorTree, Sequence, Selector, Action, Condition, register_node
from abtree.core import Status
from abtree.parser.xml_parser import XMLParser


# 注册自定义节点类型
def register_custom_nodes():
    """Register custom node types"""
    register_node("InitializeSystemAction", InitializeSystemAction)
    register_node("CheckSystemStatusCondition", CheckSystemStatusCondition)
    register_node("LoadConfigurationAction", LoadConfigurationAction)
    register_node("CheckConfigCondition", CheckConfigCondition)
    register_node("StartServicesAction", StartServicesAction)
    register_node("CheckServicesCondition", CheckServicesCondition)
    register_node("HealthCheckAction", HealthCheckAction)
    register_node("RetryAction", RetryAction)
    register_node("FallbackAction", FallbackAction)
    register_node("SystemReadyCondition", SystemReadyCondition)
    register_node("LogStatusAction", LogStatusAction)


class InitializeSystemAction(Action):
    """Initialize system"""
    
    async def execute(self, blackboard):
        print("Step 1: Initializing system...")
        await asyncio.sleep(0.5)
        
        # Set system status
        blackboard.set("system_initialized", True)
        blackboard.set("init_step", 1)
        
        print("System initialization completed")
        return Status.SUCCESS


class CheckSystemStatusCondition(Condition):
    """Check system status"""
    
    async def evaluate(self, blackboard):
        initialized = blackboard.get("system_initialized", False)
        print(f"Checking system status: {'Initialized' if initialized else 'Not initialized'}")
        return initialized


class LoadConfigurationAction(Action):
    """Load configuration"""
    
    async def execute(self, blackboard):
        print("Step 2: Loading configuration file...")
        await asyncio.sleep(0.3)
        
        # Simulate loading configuration
        config_loaded = random.random() > 0.2  # 80% success rate
        
        if config_loaded:
            blackboard.set("config_loaded", True)
            blackboard.set("init_step", 2)
            print("Configuration loaded successfully")
            return Status.SUCCESS
        else:
            print("Configuration loading failed")
            return Status.FAILURE


class CheckConfigCondition(Condition):
    """Check configuration status"""
    
    async def evaluate(self, blackboard):
        config_loaded = blackboard.get("config_loaded", False)
        print(f"Checking configuration status: {'Loaded' if config_loaded else 'Not loaded'}")
        return config_loaded


class StartServicesAction(Action):
    """Start services"""
    
    async def execute(self, blackboard):
        print("Step 3: Starting system services...")
        await asyncio.sleep(0.4)
        
        # Simulate starting services
        services_started = random.random() > 0.1  # 90% success rate
        
        if services_started:
            blackboard.set("services_running", True)
            blackboard.set("init_step", 3)
            print("Services started successfully")
            return Status.SUCCESS
        else:
            print("Services failed to start")
            return Status.FAILURE


class CheckServicesCondition(Condition):
    """Check services status"""
    
    async def evaluate(self, blackboard):
        services_running = blackboard.get("services_running", False)
        print(f"Checking services status: {'Running' if services_running else 'Not running'}")
        return services_running


class HealthCheckAction(Action):
    """Health check"""
    
    async def execute(self, blackboard):
        print("Step 4: Performing health check...")
        await asyncio.sleep(0.2)
        
        # Simulate health check
        health_ok = random.random() > 0.05  # 95% success rate
        
        if health_ok:
            blackboard.set("health_check_passed", True)
            blackboard.set("init_step", 4)
            print("健康检查通过")
            return Status.SUCCESS
        else:
            print("健康检查失败")
            return Status.FAILURE


class RetryAction(Action):
    """重试操作"""
    
    def __init__(self, name, max_retries=3):
        super().__init__(name)
        self.max_retries = max_retries
        self.retry_count = 0
    
    async def execute(self, blackboard):
        self.retry_count += 1
        print(f"重试操作 {self.name}: 第 {self.retry_count}/{self.max_retries} 次")
        
        # 模拟重试操作
        await asyncio.sleep(0.3)
        success = random.random() > 0.5  # 50%成功率
        
        if success:
            print(f"重试操作 {self.name}: 成功")
            self.retry_count = 0
            return Status.SUCCESS
        elif self.retry_count >= self.max_retries:
            print(f"重试操作 {self.name}: 达到最大重试次数，失败")
            self.retry_count = 0
            return Status.FAILURE
        else:
            print(f"重试操作 {self.name}: 失败，准备重试")
            return Status.RUNNING


class FallbackAction(Action):
    """备用操作"""
    
    async def execute(self, blackboard):
        print("执行备用操作...")
        await asyncio.sleep(0.5)
        
        # 设置备用状态
        blackboard.set("fallback_used", True)
        blackboard.set("system_status", "fallback_mode")
        
        print("备用操作完成")
        return Status.SUCCESS


class SystemReadyCondition(Condition):
    """检查系统是否就绪"""
    
    async def evaluate(self, blackboard):
        step = blackboard.get("init_step", 0)
        ready = step >= 4
        
        print(f"检查系统就绪状态: 步骤 {step}/4, {'就绪' if ready else '未就绪'}")
        return ready


class LogStatusAction(Action):
    """记录状态"""
    
    async def execute(self, blackboard):
        step = blackboard.get("init_step", 0)
        fallback_used = blackboard.get("fallback_used", False)
        
        print(f"记录系统状态: 步骤 {step}, 备用模式: {fallback_used}")
        await asyncio.sleep(0.1)
        
        return Status.SUCCESS


async def main():
    """主函数 - 演示基本控制流"""
    
    # 注册自定义节点类型
    register_custom_nodes()
    
    print("=== ABTree 控制流基础示例 ===\n")
    
    # 1. 创建主控制流
    root = Selector("系统启动控制流")
    
    # 2. 创建正常启动流程
    normal_startup = Sequence("正常启动流程")
    
    # 初始化序列
    init_sequence = Sequence("初始化序列")
    init_sequence.add_child(InitializeSystemAction("初始化"))
    init_sequence.add_child(CheckSystemStatusCondition("检查系统"))
    init_sequence.add_child(LoadConfigurationAction("加载配置"))
    init_sequence.add_child(CheckConfigCondition("检查配置"))
    init_sequence.add_child(StartServicesAction("启动服务"))
    init_sequence.add_child(CheckServicesCondition("检查服务"))
    init_sequence.add_child(HealthCheckAction("健康检查"))
    
    # 重试机制
    retry_sequence = Sequence("重试机制")
    retry_sequence.add_child(RetryAction("重试操作", 3))
    
    # 备用流程
    fallback_sequence = Sequence("备用流程")
    fallback_sequence.add_child(FallbackAction("备用操作"))
    
    # 状态记录
    status_sequence = Sequence("状态记录")
    status_sequence.add_child(SystemReadyCondition("检查就绪"))
    status_sequence.add_child(LogStatusAction("记录状态"))
    
    # 3. 组装控制流
    normal_startup.add_child(init_sequence)
    normal_startup.add_child(retry_sequence)
    normal_startup.add_child(status_sequence)
    
    # 4. 添加到根节点
    root.add_child(normal_startup)
    root.add_child(fallback_sequence)
    
    # 3. Create behavior tree
    tree = BehaviorTree()
    tree.load_from_root(root)
    blackboard = tree.blackboard
    
    # 6. 初始化黑板数据
    blackboard.set("system_initialized", False)
    blackboard.set("config_loaded", False)
    blackboard.set("services_running", False)
    blackboard.set("health_check_passed", False)
    blackboard.set("fallback_used", False)
    blackboard.set("init_step", 0)
    
    print("开始执行系统启动控制流...")
    print("=" * 50)
    
    # 7. 执行行为树
    result = await tree.tick()
    
    # 8. 显示最终状态
    print("=" * 50)
    print(f"控制流执行结果: {result}")
    print(f"初始化步骤: {blackboard.get('init_step')}/4")
    print(f"系统状态: {blackboard.get('system_status', 'normal')}")
    print(f"是否使用备用模式: {blackboard.get('fallback_used')}")
    
    # 9. 演示错误处理流程
    print("\n=== 演示错误处理流程 ===")
    
    # 重置状态
    blackboard.set("system_initialized", False)
    blackboard.set("config_loaded", False)
    blackboard.set("services_running", False)
    blackboard.set("health_check_passed", False)
    blackboard.set("fallback_used", False)
    blackboard.set("init_step", 0)
    
    print("模拟配置加载失败的情况...")
    result2 = await tree.tick()
    print(f"错误处理结果: {result2}")
    
    # 10. 演示XML配置方式
    print("\n=== XML配置方式演示 ===")
    
    # XML字符串配置
    xml_config = '''
    <BehaviorTree name="ControlFlowBasicXML" description="XML配置的控制流基础示例">
        <Sequence name="根序列">
            <Selector name="系统启动控制流">
                <Sequence name="正常启动流程">
                    <Sequence name="初始化序列">
                        <InitializeSystemAction name="初始化" />
                        <CheckSystemStatusCondition name="检查系统" />
                        <LoadConfigurationAction name="加载配置" />
                        <CheckConfigCondition name="检查配置" />
                    </Sequence>
                    <Sequence name="重试机制">
                        <RetryAction name="重试操作" max_retries="3" />
                    </Sequence>
                    <Sequence name="状态记录">
                        <SystemReadyCondition name="检查就绪" />
                        <LogStatusAction name="记录状态" />
                    </Sequence>
                </Sequence>
                <Sequence name="备用流程">
                    <FallbackAction name="备用操作" />
                </Sequence>
            </Selector>
        </Sequence>
    </BehaviorTree>
    '''
    
    # 解析XML配置
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    xml_blackboard = xml_tree.blackboard
    
    # 初始化XML配置的黑板数据
    xml_blackboard.set("system_initialized", False)
    xml_blackboard.set("config_loaded", False)
    xml_blackboard.set("services_running", False)
    xml_blackboard.set("health_check_passed", False)
    xml_blackboard.set("fallback_used", False)
    xml_blackboard.set("init_step", 0)
    
    print("通过XML字符串配置的行为树:")
    print(xml_config.strip())
    print("\n开始执行XML配置的行为树...")
    xml_result = await xml_tree.tick()
    print(f"XML配置执行完成! 结果: {xml_result}")
    print(f"XML配置初始化步骤: {xml_blackboard.get('init_step')}/4")


if __name__ == "__main__":
    asyncio.run(main()) 