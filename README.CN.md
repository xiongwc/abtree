# 🚀 ABTree - 异步行为树框架

<div align="center">

**基于Python asyncio构建的高性能异步行为树框架，专为智能决策系统设计**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/abtree/abtree?style=social)](https://github.com/xiongwc/abtree/stargazers)[![Forks](https://img.shields.io/github/forks/abtree/abtree?style=social)](https://github.com/xiongwc/abtree/network/members)

<!-- Star section -->
<div align="center">
  <a href="https://github.com/xiongwc/abtree" target="_blank">
    <img src="https://img.shields.io/badge/🌟 Star%20abtree-Support%20Development-007ACC?style=for-the-badge&logo=github&logoColor=white&labelColor=24292F" alt="Star abtree on GitHub">
  </a>
</div>

**中文** | [English](README.md)

</div>

---

## 📑 目录

- [✨ 核心特性](#-核心特性)
- [🎬 快速开始](#-快速开始)
- [📖 文档](#-文档)
- [🔧 技术栈](#-技术栈)
- [🗺️ 路线图](#-路线图)
- [🤝 贡献](#-贡献)
- [📜 许可证](#-许可证)

---

## ✨ 核心特性

<div align="center">

| 🚀 **异步引擎** | 🎯 **节点系统** | 💾 **数据管理** | 🌲 **行为森林** |
|:---:|:---:|:---:|:---:|
| 基于asyncio<br/>高性能并发 | 丰富节点类型<br/>动态注册 | 黑板系统<br/>事件驱动 | 多树协作<br/>内部通信模式 |

</div>

### ⚡ 异步行为树引擎
- **高性能异步执行** - 基于Python asyncio的并发节点调度
- **智能Tick管理** - 自动化的执行周期管理和资源控制
- **事件驱动架构** - 异步事件系统支持实时响应
- **内存优化** - 高效的状态管理和垃圾回收

### 🎯 丰富的节点系统
- **复合节点** - Sequence、Selector、Parallel等经典控制流
- **装饰器节点** - Inverter、Repeater、UntilSuccess等行为修饰
- **动作节点** - Action、Log、Wait、SetBlackboard等执行单元
- **条件节点** - Condition、CheckBlackboard、Compare等判断逻辑
- **动态注册** - 运行时节点类型注册和扩展机制

### 💾 智能数据管理
- **黑板系统** - 跨节点数据共享和状态持久化
- **事件系统** - 异步事件监听、发布和订阅机制
- **状态管理** - 行为树执行状态的完整跟踪
- **数据验证** - 类型安全的数据访问和修改

### 🌲 行为森林协作
- **多树协同** - 多个行为树组成森林协同工作
- **通信模式** - Pub/Sub、Req/Resp、共享黑板、状态监视、行为调用、任务板
- **森林管理** - 集中化的森林配置和生命周期管理
- **性能监控** - 实时性能分析和优化建议
- **可视化支持** - 森林结构和执行状态的可视化展示

---

## 🎬 快速开始

### 🔧 环境设置

```bash
# 克隆仓库
git clone https://github.com/abtree/abtree.git
cd abtree

# 安装依赖
pip install -e .
```

### 📝 基础用法

#### 🚀 方法1: 编程构建

```python
import asyncio
from abtree import BehaviorTree, Sequence, Selector, Action, Condition
from abtree.core import Status

# 定义动作节点
class OpenDoor(Action):
    async def execute(self, blackboard):
        print("开门")
        return Status.SUCCESS

class CloseDoor(Action):
    async def execute(self, blackboard):
        print("关门")
        return Status.SUCCESS

# 定义条件节点
class IsDoorOpen(Condition):
    async def evaluate(self, blackboard):
        return blackboard.get("door_open", False)

# 构建行为树
root = Selector("机器人决策")
root.add_child(Sequence("门控制序列"))
root.children[0].add_child(IsDoorOpen("检查门状态"))
root.children[0].add_child(CloseDoor("关门"))

# 创建行为树实例
tree = BehaviorTree(root)

# 执行
async def main():
    blackboard = tree.blackboard
    blackboard.set("door_open", True)
    
    result = await tree.tick()
    print(f"执行结果: {result}")

asyncio.run(main())
```

#### 📄 方法2: XML配置

```python
import asyncio
from abtree import load_from_xml_string

# 定义XML字符串
xml_string = '''<BehaviorTree name="机器人决策">
    <Selector name="机器人决策">
        <Sequence name="门控制序列">
            <CheckBlackboard name="检查门状态" key="door_open" expected_value="true" />
            <Log name="关门日志" message="检测到门开着，准备关门" />
            <Wait name="关门等待" duration="1.0" />
        </Sequence>
    </Selector>
</BehaviorTree>'''

# 从XML字符串加载行为树
tree = load_from_xml_string(xml_string)

# 执行
async def main():
    blackboard = tree.blackboard
    blackboard.set("door_open", True)
    
    result = await tree.tick()
    print(f"执行结果: {result}")

asyncio.run(main())
```

### 🌲 行为森林示例

```python
import asyncio
from abtree import (
    BehaviorForest, ForestNode, ForestNodeType,
    PubSubMiddleware, SharedBlackboardMiddleware
)

# 创建行为森林
forest = BehaviorForest("机器人协作森林")

# 添加通信中间件
forest.add_middleware(PubSubMiddleware("PubSub"))
forest.add_middleware(SharedBlackboardMiddleware("共享黑板"))

# 添加机器人节点到森林
for robot_id in ["R1", "R2", "R3"]:
    tree = create_robot_tree(robot_id)  # 创建机器人行为树
    node = ForestNode(
        name=f"Robot_{robot_id}",
        tree=tree,
        node_type=ForestNodeType.WORKER,
        capabilities={"清洁", "导航", "紧急"}
    )
    forest.add_node(node)

# 启动森林
async def main():
    await forest.start()
    
    # 运行几个tick
    for i in range(5):
        results = await forest.tick()
        print(f"Tick {i+1}: {results}")
        await asyncio.sleep(1.0)
    
    await forest.stop()

asyncio.run(main())
```

---


## 📖 文档

- **📚 快速开始**: [examples/](examples/)
- **🔧 API参考**: [docs/api.md](docs/api.md)
- **🛠️ CLI工具**: [cli/](cli/)
- **🧪 测试**: [tests/](tests/)

### 📁 项目结构

```
abtree/
├── abtree/                     # 📦 核心包
│   ├── core/                   # 🔧 核心功能
│   ├── engine/                 # ⚙️ 引擎系统
│   ├── forest/                 # 🌲 行为森林
│   ├── nodes/                  # 🎯 节点实现
│   ├── parser/                 # 📝 配置解析
│   ├── registry/               # 📋 节点注册
│   ├── ui/                     # 🖥️ 用户界面
│   └── utils/                  # 🔧 工具
├── cli/                        # 🖥️ 命令行工具
├── docs/                       # 📖 文档
├── examples/                   # 📚 示例代码
├── tests/                      # 🧪 测试套件
├── scripts/                    # 📜 脚本工具
├── test_reports/               # 📊 测试报告
└── pyproject.toml              # ⚙️ 构建与依赖配置
```

---

### 🔧 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| **语言** | Python | 3.8+ |
| **异步框架** | asyncio | 内置 |
| **数据验证** | Pydantic | 2.0+ |
| **XML处理** | xml.etree | 内置 |
| **测试** | pytest | 7.0+ |
| **代码格式化** | isort | 5.0+ |
| **类型检查** | mypy | 1.0+ |

---

### 📋 代码标准

- 遵循 **PEP 8** 编码标准
- 使用 **Google风格** 文档字符串
- 为所有函数添加 **类型注解**
- 为关键功能编写 **单元测试**

---

## 🗺️ 路线图

- [x] ✅ **v1.0** - 核心异步行为树框架
- [x] ✅ **v1.1** - XML配置支持
- [x] ✅ **v1.2** - 事件系统和黑板优化
- [ ] 🎯 **v1.3** - 高级节点类型
- [ ] 📊 **v1.4** - 性能监控
- [ ] 🖼️ **v1.5** - 可视化编辑器集成

---

## 🤝 贡献

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交改动 (`git commit -m 'Add some amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📜 许可证

本项目采用 [MIT许可证](LICENSE)。

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个Star来支持开发！ ⭐**

<div align="center">
  <a href="https://github.com/xiongwc/abtree" target="_blank">
    <img src="https://img.shields.io/badge/🌟 Star%20abtree-Support%20Development-007ACC?style=for-the-badge&logo=github&logoColor=white&labelColor=24292F" alt="Star abtree on GitHub">
  </a>
</div>

[![GitHub Discussions](https://img.shields.io/github/discussions/abtree/abtree?color=blue&logo=github)](https://github.com/abtree/abtree/discussions)[![GitHub Issues](https://img.shields.io/github/issues/abtree/abtree?color=green&logo=github)](https://github.com/abtree/abtree/issues)[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/abtree/abtree?color=orange&logo=github)](https://github.com/abtree/abtree/pulls)

</div> 