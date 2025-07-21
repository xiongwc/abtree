# ABTree 测试目录

本目录包含了 ABTree 的完整测试套件，包括单元测试、集成测试和测试工具。

## 📁 目录结构

```
tests/
├── __init__.py              # 测试模块初始化
├── conftest.py              # Pytest 配置文件
├── test_core.py             # 核心模块单元测试
├── test_nodes.py            # 节点模块单元测试
├── test_behavior_tree.py    # 行为树集成测试
├── run_tests.py             # 测试运行脚本
└── README.md                # 本文件
```

## 🧪 测试类型

### 1. 单元测试 (`test_core.py`, `test_nodes.py`)

**测试范围**:
- 核心功能模块 (Status, Policy, Blackboard, EventSystem, TickManager)
- 各种节点类型 (Action, Condition, Sequence, Selector, Parallel, Inverter, Repeater)

**特点**:
- 快速执行
- 独立测试
- 详细断言
- 模拟对象

### 2. 集成测试 (`test_behavior_tree.py`)

**测试范围**:
- 完整行为树功能
- 复杂场景测试
- 状态管理
- 执行流程

**特点**:
- 端到端测试
- 真实场景模拟
- 性能测试
- 错误处理

## 🚀 运行测试

### 基本命令

```bash
# 运行所有测试
python tests/run_tests.py

# 运行单元测试
python tests/run_tests.py --unit

# 运行集成测试
python tests/run_tests.py --integration

# 运行覆盖率测试
python tests/run_tests.py --coverage

# 并行运行测试
python tests/run_tests.py --parallel
```

### 高级选项

```bash
# 运行特定测试文件
python tests/run_tests.py --file tests/test_core.py

# 运行标记的测试
python tests/run_tests.py --marker unit

# 运行慢速测试
python tests/run_tests.py --slow

# 运行快速测试
python tests/run_tests.py --fast

# 生成HTML报告
python tests/run_tests.py --html

# 检查测试环境
python tests/run_tests.py --check
```

### 直接使用 pytest

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_core.py

# 运行标记的测试
pytest tests/ -m unit

# 生成覆盖率报告
pytest tests/ --cov=abtree --cov-report=html

# 并行运行
pytest tests/ -n auto
```

## 📊 测试覆盖率

### 目标覆盖率

- **核心模块**: 95%+
- **节点模块**: 90%+
- **集成测试**: 85%+
- **总体覆盖率**: 80%+

### 覆盖率报告

运行覆盖率测试后，会生成以下报告：

1. **终端报告**: 显示缺失的代码行
2. **HTML报告**: 详细的覆盖率分析页面
3. **XML报告**: 用于CI/CD集成

## 🏷️ 测试标记

### 内置标记

- `@pytest.mark.unit`: 单元测试
- `@pytest.mark.integration`: 集成测试
- `@pytest.mark.slow`: 慢速测试

### 自定义标记

```python
@pytest.mark.unit
def test_simple_function():
    """单元测试示例"""
    pass

@pytest.mark.integration
def test_complex_scenario():
    """集成测试示例"""
    pass

@pytest.mark.slow
def test_performance():
    """性能测试示例"""
    pass
```

## 🔧 测试配置

### Pytest 配置

测试配置在 `conftest.py` 中定义：

- **共享 Fixture**: 提供常用的测试对象
- **测试标记**: 定义测试分类
- **报告配置**: 自定义测试报告
- **环境检查**: 验证测试环境

### 环境要求

```bash
# 安装测试依赖
pip install pytest pytest-cov pytest-html pytest-xdist

# 开发依赖
pip install pytest-mock pytest-asyncio
```

## 📈 测试报告

### HTML 报告

运行测试后生成的 HTML 报告包含：

- 测试结果概览
- 详细的测试日志
- 失败测试的堆栈跟踪
- 测试执行时间统计

### 覆盖率报告

覆盖率报告显示：

- 代码覆盖率百分比
- 未覆盖的代码行
- 分支覆盖率
- 函数覆盖率

## 🐛 调试测试

### 常见问题

1. **导入错误**: 确保项目已正确安装
2. **异步测试**: 使用 `asyncio.run()` 运行异步测试
3. **环境问题**: 运行 `--check` 检查测试环境

### 调试技巧

```bash
# 详细输出
pytest tests/ -v -s

# 只运行失败的测试
pytest tests/ --lf

# 在失败时停止
pytest tests/ -x

# 显示最慢的测试
pytest tests/ --durations=10
```

## 📝 添加新测试

### 测试文件命名

- 单元测试: `test_<module>.py`
- 集成测试: `test_<feature>_integration.py`
- 性能测试: `test_<feature>_performance.py`

### 测试类命名

```python
class TestFeatureName:
    """测试功能描述"""
    
    def test_specific_behavior(self):
        """测试特定行为"""
        pass
```

### 测试方法命名

- `test_<function_name>`: 测试函数
- `test_<class_name>`: 测试类
- `test_<scenario>`: 测试场景

## 🔄 CI/CD 集成

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: python tests/run_tests.py --coverage
```

### 本地开发

```bash
# 开发时运行快速测试
python tests/run_tests.py --fast

# 提交前运行完整测试
python tests/run_tests.py --coverage
```

## 📚 最佳实践

1. **测试驱动开发**: 先写测试，再写代码
2. **测试隔离**: 每个测试独立运行
3. **模拟外部依赖**: 使用 mock 对象
4. **测试覆盖率**: 保持高覆盖率
5. **持续集成**: 自动化测试流程 