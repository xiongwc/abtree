# 🚀 ABTree - Asynchronous Behavior Tree Framework

<div align="center">

**High-performance asynchronous behavior tree framework built on Python asyncio, designed for intelligent decision systems**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/abtree/abtree?style=social)](https://github.com/xiongwc/abtree/stargazers)[![Forks](https://img.shields.io/github/forks/abtree/abtree?style=social)](https://github.com/xiongwc/abtree/network/members)

<!-- Star section -->
<div align="center">
  <a href="https://github.com/xiongwc/abtree" target="_blank">
    <img src="https://img.shields.io/badge/🌟 Star%20abtree-Support%20Development-007ACC?style=for-the-badge&logo=github&logoColor=white&labelColor=24292F" alt="Star abtree on GitHub">
  </a>
</div>

[中文](README.CN.md) | **English**

</div>

---

## 📑 Table of Contents

- [✨ Core Features](#-core-features)
- [🎬 Quick Start](#-quick-start)
- [📖 Documentation](#-documentation)
- [🔧 Technology Stack](#-technology-stack)
- [🗺️ Roadmap](#️-roadmap)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)

---

## ✨ Core Features

<div align="center">

| 🚀 **Async Engine** | 🎯 **Node System** | 💾 **Data Management** | 🌲 **Behavior Forest** |
|:---:|:---:|:---:|:---:|
| Based on asyncio<br/>High Performance Concurrency | Rich Node Types<br/>Dynamic Registration | Blackboard System<br/>Event Driven | Multi-tree Collaboration<br/>Internal Communication Modes |

</div>

### ⚡ Asynchronous Behavior Tree Engine
- **High Performance Async Execution** - Concurrent node scheduling based on Python asyncio
- **Smart Tick Management** - Automated execution cycle management and resource control
- **Event Driven Architecture** - Asynchronous event system supporting real-time response
- **Memory Optimization** - Efficient state management and garbage collection

### 🎯 Rich Node System
- **Composite Nodes** - Sequence, Selector, Parallel and other classic control flows
- **Decorator Nodes** - Inverter, Repeater, UntilSuccess and other behavior modifiers
- **Action Nodes** - Action, Log, Wait, SetBlackboard and other execution units
- **Condition Nodes** - Condition, CheckBlackboard, Compare and other judgment logic
- **Dynamic Registration** - Runtime node type registration and extension mechanism

### 💾 Smart Data Management
- **Blackboard System** - Cross-node data sharing and state persistence
- **Event System** - Asynchronous event listening, publishing and subscription mechanism
- **State Management** - Complete tracking of behavior tree execution state
- **Data Validation** - Type-safe data access and modification

### 🌲 Behavior Forest Collaboration
- **Multi-tree Coordination** - Multiple behavior trees working together as a forest
- **Communication Modes** - Pub/Sub, Req/Resp, Shared Blackboard, State Monitoring, Behavior Invocation, Task Board
- **Forest Management** - Centralized forest configuration and lifecycle management
- **Performance Monitoring** - Real-time performance analysis and optimization suggestions
- **Visualization Support** - Forest structure and execution state visualization

---

## 🎬 Quick Start

### 🔧 Environment Setup

```bash
# Clone repository
git clone https://github.com/abtree/abtree.git
cd abtree

# Install dependencies
pip install -e .
```

### 📝 Basic Usage

#### 🚀 Method 1: Programmatic Building

```python
import asyncio
from abtree import BehaviorTree, Sequence, Selector, Action, Condition
from abtree.core import Status

# Define action nodes
class OpenDoor(Action):
    async def execute(self, blackboard):
        print("Opening door")
        return Status.SUCCESS

class CloseDoor(Action):
    async def execute(self, blackboard):
        print("Closing door")
        return Status.SUCCESS

# Define condition nodes
class IsDoorOpen(Condition):
    async def evaluate(self, blackboard):
        return blackboard.get("door_open", False)

# Build behavior tree
root = Selector("Robot Decision")
root.add_child(Sequence("Door Control Sequence"))
root.children[0].add_child(IsDoorOpen("Check Door Status"))
root.children[0].add_child(CloseDoor("Close Door"))

# Create behavior tree instance
tree = BehaviorTree(root)

# Execute
async def main():
    blackboard = tree.blackboard
    blackboard.set("door_open", True)
    
    result = await tree.tick()
    print(f"Execution result: {result}")

asyncio.run(main())
```

#### 📄 Method 2: XML Configuration

```python
import asyncio
from abtree import load_from_xml_string

# Define XML string
xml_string = '''<BehaviorTree name="Robot Decision">
    <Selector name="Robot Decision">
        <Sequence name="Door Control Sequence">
            <CheckBlackboard name="Check Door Status" key="door_open" expected_value="true" />
            <Log name="Close Door Log" message="Door detected open, preparing to close" />
            <Wait name="Close Door Wait" duration="1.0" />
        </Sequence>
    </Selector>
</BehaviorTree>'''

# Load behavior tree from XML string
tree = load_from_xml_string(xml_string)

# Execute
async def main():
    blackboard = tree.blackboard
    blackboard.set("door_open", True)
    
    result = await tree.tick()
    print(f"Execution result: {result}")

asyncio.run(main())
```

### 🌲 Behavior Forest Example

```python
import asyncio
from abtree import (
    BehaviorForest, ForestNode, ForestNodeType,
    PubSubMiddleware, SharedBlackboardMiddleware
)

# Create behavior forest
forest = BehaviorForest("Robot Collaboration Forest")

# Add communication middleware
forest.add_middleware(PubSubMiddleware("PubSub"))
forest.add_middleware(SharedBlackboardMiddleware("Shared Blackboard"))

# Add robot nodes to forest
for robot_id in ["R1", "R2", "R3"]:
    tree = create_robot_tree(robot_id)  # Create robot behavior tree
    node = ForestNode(
        name=f"Robot_{robot_id}",
        tree=tree,
        node_type=ForestNodeType.WORKER,
        capabilities={"cleaning", "navigation", "emergency"}
    )
    forest.add_node(node)

# Start forest
async def main():
    await forest.start()
    
    # Run several ticks
    for i in range(5):
        results = await forest.tick()
        print(f"Tick {i+1}: {results}")
        await asyncio.sleep(1.0)
    
    await forest.stop()

asyncio.run(main())
```

---

## 📖 Documentation

- **📚 Quick Start**: [examples/](examples/)
- **🔧 API Reference**: [docs/api.md](docs/api.md)
- **🛠️ CLI Tools**: [cli/](cli/)
- **🧪 Testing**: [tests/](tests/)

### 📁 Project Structure

```
abtree/
├── abtree/                     # 📦 Core package
│   ├── core/                   # 🔧 Core functionality
│   ├── engine/                 # ⚙️ Engine system
│   ├── forest/                 # 🌲 Behavior forest
│   ├── nodes/                  # 🎯 Node implementations
│   ├── parser/                 # 📝 Configuration parsing
│   ├── registry/               # 📋 Node registration
│   ├── ui/                     # 🖥️ User interface
│   └── utils/                  # 🔧 Utilities
├── cli/                        # 🖥️ Command line tools
├── docs/                       # 📖 Documentation
├── examples/                   # 📚 Example code
├── tests/                      # 🧪 Test suite
├── scripts/                    # 📜 Script tools
├── test_reports/               # 📊 Test reports
└── pyproject.toml              # ⚙️ Build and dependency configuration
```

---



---

## 🔧 Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Language** | Python | 3.8+ |
| **Async Framework** | asyncio | Built-in |
| **Data Validation** | Pydantic | 2.0+ |
| **XML Processing** | xml.etree | Built-in |
| **Testing** | pytest | 7.0+ |
| **Code Formatting** | isort | 5.0+ |
| **Type Checking** | mypy | 1.0+ |

### 📋 Code Standards

- Follow **PEP 8** coding standards
- Use **Google style** docstrings
- Add **type annotations** for all functions
- Write **unit tests** for key functionality

---

## 🗺️ Roadmap

- [x] ✅ **v1.0** - Core asynchronous behavior tree framework
- [x] ✅ **v1.1** - XML configuration support
- [x] ✅ **v1.2** - Event system and blackboard optimization
- [ ] 🎯 **v1.3** - Advanced node types
- [ ] 📊 **v1.4** - Performance monitoring
- [ ] 🖼️ **v1.5** - Visual editor integration

---

## 🤝 Contributing

1. Fork the project repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**⭐ If this project helps you, please give us a Star to support development! ⭐**

<div align="center">
  <a href="https://github.com/xiongwc/abtree" target="_blank">
    <img src="https://img.shields.io/badge/🌟 Star%20abtree-Support%20Development-007ACC?style=for-the-badge&logo=github&logoColor=white&labelColor=24292F" alt="Star abtree on GitHub">
  </a>
</div>

[![GitHub Discussions](https://img.shields.io/github/discussions/abtree/abtree?color=blue&logo=github)](https://github.com/xiongwc/abtree/discussions)[![GitHub Issues](https://img.shields.io/github/issues/abtree/abtree?color=green&logo=github)](https://github.com/xiongwc/abtree/issues)[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/abtree/abtree?color=orange&logo=github)](https://github.com/abtree/xiongwc/pulls)

</div>