<div align="center">
  <h1>🚀 ABTree</h1>
</div>

<div align="center">

**Asynchronous behavior tree framework built on Python asyncio, designed for intelligent decision systems with declarative programming paradigm**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/xiongwc/abtree?style=social)](https://github.com/xiongwc/abtree/stargazers)[![Forks](https://img.shields.io/github/forks/xiongwc/abtree?style=social)](https://github.com/xiongwc/abtree/network/members)

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

---

## 🎬 Quick Start

### 🔧 Environment Setup

#### Development Environment Installation
For source code development, debugging, and contributing:
```bash
git clone https://github.com/xiongwc/abtree.git
cd abtree
pip install -e .
```

#### Production Environment Installation
For production deployment and daily use:
```bash
pip install abtree
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
tree = BehaviorTree()
tree.load_from_node(root)

# Execute
async def main():
    blackboard = tree.blackboard
    blackboard.set("door_open", True)
    
    result = await tree.tick()
    print(f"Execution result: {result}")

asyncio.run(main())
```

#### 📄 Method 2: Declarative XML Configuration

```python
import asyncio
from abtree import load_tree_from_string

# Declarative XML: Express behavior logic in a readable, structured format
xml_string = '''<BehaviorTree name="Robot Decision">
    <Selector name="Robot Decision">
        <Sequence name="Door Control Sequence">
            <CheckBlackboard name="Check Door Status" key="door_open" expected_value="true" />
            <Log name="Close Door Log" message="Door detected open, preparing to close" />
            <Wait name="Close Door Wait" duration="1.0" />
        </Sequence>
    </Selector>
</BehaviorTree>'''

# Load behavior tree from declarative XML configuration
tree = load_tree_from_string(xml_string)

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
    PubSubMiddleware, SharedBlackboardMiddleware,
    BehaviorTree, Sequence, Selector, Action, Condition
)
from abtree.core import Status

# Simple robot action node
class RobotAction(Action):
    def __init__(self, name: str, action_type: str):
        super().__init__(name)
        self.action_type = action_type
    
    async def execute(self, blackboard):
        print(f"Robot {self.action_type}")
        if self.action_type == "cleaning":
            blackboard.set("cleaning_needed", False)
        return Status.SUCCESS

# Simple condition node
class SimpleCondition(Condition):
    def __init__(self, name: str, key: str, default: bool = True):
        super().__init__(name)
        self.key = key
        self.default = default
    
    async def evaluate(self, blackboard):
        return blackboard.get(self.key, self.default)

def create_robot_tree(robot_id: str) -> BehaviorTree:
    """Create a simple robot behavior tree"""
    root = Selector(f"Robot_{robot_id}")
    
    # Cleaning sequence
    cleaning_seq = Sequence("Cleaning")
    cleaning_seq.add_child(SimpleCondition("Check Cleaning", "cleaning_needed"))
    cleaning_seq.add_child(RobotAction("Clean", "cleaning"))
    cleaning_seq.add_child(RobotAction("Navigate", "navigating"))
    root.add_child(cleaning_seq)
    
    tree = BehaviorTree()
    tree.load_from_node(root)
    return tree

async def main():
    # Create behavior forest
    forest = BehaviorForest("Robot Forest")
    
    # Add robot nodes
    for robot_id in ["R1", "R2", "R3"]:
        tree = create_robot_tree(robot_id)
        node = ForestNode(
            name=f"Robot_{robot_id}",
            tree=tree,
            node_type=ForestNodeType.WORKER,
            capabilities={"cleaning", "navigation"}
        )
        forest.add_node(node)
    
    # Start forest
    await forest.start()
    
    # Execute ticks
    for i in range(3):
        results = await forest.tick()
        print(f"Tick {i+1}: {results}")
        await asyncio.sleep(0.5)
    
    await forest.stop()

if __name__ == "__main__":
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

## 🔧 Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Language** | Python | 3.8+ |
| **Async Framework** | asyncio | Built-in |
| **XML Processing** | xml.etree | Built-in |
| **Testing** | pytest | 7.0+ |
| **Type Checking** | mypy | 1.0+ |

### 📋 Code Standards

- Follow **PEP 8** coding standards
- Use **Google style** docstrings
- Add **type annotations** for all functions
- Write **unit tests** for key functionality

---

## 🗺️ Roadmap

- [x] ✅ **v0.1** - Core asynchronous behavior tree framework
- [x] ✅ **v0.2** - XML configuration support
- [x] ✅ **v0.3** - Event system and blackboard optimization
- [ ] 🎯 **v0.4** - Advanced node types

---

## 🤝 Contributing

1. Fork the project repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🙏 Acknowledgments

Inspiration from [BehaviorTree.CPP](https://github.com/BehaviorTree/BehaviorTree.CPP).

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

[![GitHub Discussions](https://img.shields.io/github/discussions/xiongwc/abtree?color=blue&logo=github)](https://github.com/xiongwc/abtree/discussions)[![GitHub Issues](https://img.shields.io/github/issues/xiongwc/abtree?color=green&logo=github)](https://github.com/xiongwc/abtree/issues)[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/xiongwc/abtree?color=orange&logo=github)](https://github.com/xiongwc/abtree/pulls)

</div>