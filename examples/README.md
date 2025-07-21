# ABTree 学习指南 - 19个从入门到精通的例子

本目录包含了19个精心设计的ABTree学习例子，从最基础的Hello World到高级应用场景，帮助您逐步掌握ABTree框架。

## 🚀 快速开始

运行所有例子：
```bash
python examples/test_all_examples.py
```

## 📚 学习路径

### 🎯 基础入门模块 (5个例子)

#### 01. Hello World (`01_hello_world.py`)
**难度**: ⭐  
**学习目标**: 最基础的ABTree使用
- 创建第一个行为树
- 理解动作节点和条件节点
- 执行行为树
- 理解SUCCESS/FAILURE状态

**运行方式**:
```bash
python examples/01_hello_world.py
```

#### 02. 简单序列 (`02_simple_sequence.py`)
**难度**: ⭐⭐  
**学习目标**: 序列节点的基本使用
- Sequence节点的基本概念
- 顺序执行逻辑
- 节点组合和嵌套
- 执行状态管理

**运行方式**:
```bash
python examples/02_simple_sequence.py
```

#### 03. 选择器基础 (`03_selector_basic.py`)
**难度**: ⭐⭐  
**学习目标**: 选择器节点的使用
- Selector节点的基本概念
- 条件选择逻辑
- 优先级处理
- 失败回退机制

**运行方式**:
```bash
python examples/03_selector_basic.py
```

#### 04. 黑板基础 (`04_blackboard_basic.py`)
**难度**: ⭐⭐⭐  
**学习目标**: 黑板系统的使用
- 黑板的基本操作和数据共享
- 条件节点与黑板交互
- 动作节点修改黑板数据
- 复杂数据结构的处理

**运行方式**:
```bash
python examples/04_blackboard_basic.py
```

#### 05. 动作节点 (`05_action_nodes.py`)
**难度**: ⭐⭐⭐  
**学习目标**: 动作节点的详细使用
- 各种动作节点的实现
- 动作节点的状态管理
- 动作节点的参数传递
- 动作节点的错误处理

**运行方式**:
```bash
python examples/05_action_nodes.py
```

### 🔄 进阶模块 (5个例子)

#### 06. 条件节点 (`06_condition_nodes.py`)
**难度**: ⭐⭐⭐  
**学习目标**: 条件节点的使用
- 条件节点的实现
- 条件评估逻辑
- 条件节点的组合
- 动态条件判断

**运行方式**:
```bash
python examples/06_condition_nodes.py
```

#### 07. 装饰器节点 (`07_decorator_nodes.py`)
**难度**: ⭐⭐⭐  
**学习目标**: 装饰器节点的使用
- 装饰器节点的概念
- 各种装饰器类型
- 装饰器的组合使用
- 自定义装饰器

**运行方式**:
```bash
python examples/07_decorator_nodes.py
```

#### 08. 复合节点 (`08_composite_nodes.py`)
**难度**: ⭐⭐⭐  
**学习目标**: 复合节点的使用
- 复合节点的概念
- 各种复合节点类型
- 复合节点的嵌套
- 复合节点的优化

**运行方式**:
```bash
python examples/08_composite_nodes.py
```

#### 09. 控制流基础 (`09_control_flow_basic.py`)
**难度**: ⭐⭐⭐  
**学习目标**: 基础控制流模式
- 控制流的基本概念
- 顺序和选择逻辑
- 控制流的组合
- 控制流的调试

**运行方式**:
```bash
python examples/09_control_flow_basic.py
```

#### 10. 高级控制流 (`10_control_flow_advanced.py`)
**难度**: ⭐⭐⭐⭐  
**学习目标**: 高级控制流模式
- 复杂控制流设计
- 动态控制流调整
- 控制流优化
- 控制流监控

**运行方式**:
```bash
python examples/10_control_flow_advanced.py
```

### 🚀 高级应用模块 (9个例子)

#### 11. 行为森林 (`11_behavior_forest.py`)
**难度**: ⭐⭐⭐⭐  
**学习目标**: 行为森林的概念和使用
- 行为森林的基本概念
- 森林中的树管理
- 森林级别的控制
- 森林的优化

**运行方式**:
```bash
python examples/11_behavior_forest.py
```

#### 12. 森林管理器 (`12_forest_manager.py`)
**难度**: ⭐⭐⭐⭐  
**学习目标**: 森林管理器的使用
- 森林管理器的功能
- 森林的创建和管理
- 森林的监控和调试
- 森林的性能优化

**运行方式**:
```bash
python examples/12_forest_manager.py
```

#### 13. 高级森林特性 (`13_advanced_forest_features.py`)
**难度**: ⭐⭐⭐⭐  
**学习目标**: 森林的高级特性
- 森林的高级功能
- 森林的扩展性
- 森林的自定义
- 森林的集成

**运行方式**:
```bash
python examples/13_advanced_forest_features.py
```

#### 14. 状态管理 (`14_state_management.py`)
**难度**: ⭐⭐⭐⭐  
**学习目标**: 复杂状态管理
- 状态转换逻辑
- 状态持久化
- 状态同步
- 状态恢复
- 状态监控

**运行方式**:
```bash
python examples/14_state_management.py
```

#### 15. 事件系统 (`15_event_system.py`)
**难度**: ⭐⭐⭐⭐  
**学习目标**: 事件驱动的行为树
- 事件监听和处理机制
- 异步事件系统
- 事件优先级
- 事件过滤和处理

**运行方式**:
```bash
python examples/15_event_system.py
```

#### 16. 自动化测试 (`16_automation_testing.py`)
**难度**: ⭐⭐⭐⭐⭐  
**学习目标**: 自动化测试系统的行为树设计
- 测试用例管理
- 测试执行流程
- 错误检测和报告
- 测试数据管理
- 持续集成

**运行方式**:
```bash
python examples/16_automation_testing.py
```

#### 17. 机器人控制 (`17_robot_control.py`)
**难度**: ⭐⭐⭐⭐⭐  
**学习目标**: 机器人控制系统的行为树建模
- 传感器数据处理
- 运动控制
- 路径规划
- 避障算法
- 任务调度

**运行方式**:
```bash
python examples/17_robot_control.py
```

#### 18. 智能家居系统 (`18_smart_home.py`)
**难度**: ⭐⭐⭐⭐⭐  
**学习目标**: 智能家居应用
- 设备控制
- 环境监控
- 用户交互
- 节能优化
- 安全监控

**运行方式**:
```bash
python examples/18_smart_home.py
```

#### 19. 游戏AI (`19_game_ai.py`)
**难度**: ⭐⭐⭐⭐⭐  
**学习目标**: 游戏AI的行为树实现
- 角色行为决策
- 战斗AI
- 寻路算法
- 团队协作
- 动态难度调整

**运行方式**:
```bash
python examples/19_game_ai.py
```

## 🎯 学习建议

### 1. 循序渐进
- 从01开始，按顺序学习
- 每个例子都要理解透彻再进入下一个
- 可以修改参数观察不同结果

### 2. 实践为主
- 运行每个例子
- 尝试修改代码
- 观察输出结果
- 理解执行流程

### 3. 深入理解
- 理解每个节点的作用
- 掌握控制流逻辑
- 学会调试和优化
- 思考实际应用场景

### 4. 项目实践
- 基于例子创建自己的项目
- 结合实际需求
- 优化和扩展功能
- 分享和交流经验

## 🔧 运行环境

### 系统要求
- Python 3.8+
- asyncio支持
- 推荐使用虚拟环境

### 安装依赖
```bash
pip install abtree
```

### 运行所有例子
```bash
python examples/test_all_examples.py
```

## 📖 学习资源

### 官方文档
- [ABTree API文档](docs/api.md)
- [核心概念](docs/concepts.md)
- [最佳实践](docs/best_practices.md)

### 社区资源
- [GitHub仓库](https://github.com/abtree/abtree)
- [问题反馈](https://github.com/abtree/abtree/issues)
- [讨论区](https://github.com/abtree/abtree/discussions)

## 🤝 贡献指南

欢迎贡献新的例子和改进现有例子！

### 贡献方式
1. Fork项目
2. 创建特性分支
3. 提交更改
4. 发起Pull Request

### 例子规范
- 清晰的文档说明
- 完整的代码注释
- 可运行的示例
- 合理的难度梯度

## 📞 联系方式

- 项目主页: https://github.com/abtree/abtree
- 问题反馈: https://github.com/abtree/abtree/issues
- 邮箱: support@abtree.org

---

**祝您学习愉快！** 🎉 

## 🎯 学习目标

通过这19个例子的学习，您将掌握：

### 基础技能
- ✅ 行为树的基本概念和原理
- ✅ 各种节点类型的使用方法
- ✅ 控制流和决策逻辑
- ✅ 黑板系统和数据共享

### 进阶技能
- ✅ 装饰器和复合节点
- ✅ 高级控制流模式
- ✅ 行为森林管理
- ✅ 事件驱动编程

### 高级技能
- ✅ 复杂状态管理
- ✅ 实际应用场景
- ✅ 系统集成和优化
- ✅ 多领域应用

## 📚 参考资料

- [ABTree官方文档](../docs/README.md)
- [API参考文档](../docs/api.md)
- [最佳实践指南](../docs/best_practices.md)
- [常见问题解答](../docs/faq.md)

## 🤝 贡献

欢迎提交新的例子和改进建议！

---

**祝您学习愉快！** 🚀 