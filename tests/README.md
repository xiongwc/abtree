# ABTree Test Suite

This directory contains comprehensive test cases for the ABTree behavior tree framework.

## Test Structure

### Core Tests (`test_core_status.py`)
- **Status Enum Tests**: Tests for `Status` and `Policy` enums
- **Enum Values**: Verifies all enum values and string representations
- **Enum Iteration**: Tests enum iteration and completeness

### Engine Tests (`test_engine.py`)
- **Blackboard Tests**: Tests data storage, retrieval, and async operations
- **Event System Tests**: Tests event emission, subscription, and management
- **Behavior Tree Tests**: Tests tree initialization, tick execution, and event integration

### Node Tests (`test_nodes.py`)
- **Base Node Tests**: Tests parent-child relationships, node traversal, and status management
- **Node Operations**: Tests adding/removing children, finding nodes, and reset functionality
- **Status Helpers**: Tests node status checking methods

### Forest Tests (`test_forest.py`)
- **Forest Node Tests**: Tests node capabilities, dependencies, and tick execution
- **Behavior Forest Tests**: Tests forest management, node addition/removal, and collaborative execution
- **Forest Operations**: Tests forest-level operations and middleware integration

### Parser Tests (`test_parser.py`)
- **XML Parser Tests**: Tests XML string and file parsing for behavior trees and forests
- **Error Handling**: Tests parser error handling for invalid XML structures
- **Tree/Forest Parsing**: Tests parsing of both single trees and multi-tree forests

### Registry Tests (`test_registry.py`)
- **Node Registry Tests**: Tests node registration, creation, and metadata management
- **Registry Operations**: Tests registry clearing, length checking, and node lookup

### Utils Tests (`test_utils.py`)
- **Validation Tests**: Tests tree and node validation functions
- **Error Detection**: Tests validation error detection for invalid structures
- **Warning Generation**: Tests validation warning generation for potential issues

## Test Coverage

Current test coverage: **44%**

### High Coverage Modules (>80%)
- `abtree/core/status.py`: 100%
- `abtree/engine/blackboard.py`: 83%
- `abtree/nodes/base.py`: 91%
- `abtree/registry/node_registry.py`: 79%

### Medium Coverage Modules (40-80%)
- `abtree/engine/behavior_tree.py`: 49%
- `abtree/engine/event_system.py`: 62%
- `abtree/forest/core.py`: 65%
- `abtree/parser/xml_parser.py`: 51%

### Low Coverage Modules (<40%)
- `abtree/forest/communication.py`: 31%
- `abtree/forest/performance.py`: 31%
- `abtree/forest/plugin_system.py`: 36%
- `abtree/forest/visualization.py`: 20%
- `abtree/nodes/composite.py`: 25%
- `abtree/nodes/decorator.py`: 28%
- `abtree/parser/tree_builder.py`: 13%

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=abtree --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_engine.py -v

# Run specific test function
python -m pytest tests/test_engine.py::test_blackboard_basic -v
```

## Test Design Principles

1. **Comprehensive Coverage**: Tests cover core functionality, edge cases, and error conditions
2. **Async Support**: Uses `@pytest.mark.asyncio` for testing async methods
3. **Mock Objects**: Uses dummy classes to test abstract interfaces
4. **Error Handling**: Tests both success and failure scenarios
5. **Boundary Testing**: Tests edge cases and boundary conditions

## Future Improvements

1. **Increase Coverage**: Add more tests for low-coverage modules
2. **Integration Tests**: Add end-to-end integration tests
3. **Performance Tests**: Add performance benchmarking tests
4. **Stress Tests**: Add tests for high-load scenarios
5. **Memory Tests**: Add memory leak detection tests 