"""
Composite Nodes Example

This example demonstrates the usage of various composite nodes in the behavior tree.
Composite nodes contain multiple child nodes and control their execution flow.
"""

import asyncio
from abtree.engine.behavior_tree import BehaviorTree
from abtree.engine.blackboard import Blackboard
from abtree.core.status import Status
from abtree.nodes.base import BaseNode
from abtree.nodes.composite import Sequence, Selector, Parallel


# Custom action node for demonstration
class SimpleAction(BaseNode):
    def __init__(self, name: str, should_succeed: bool = True, delay: float = 0.1):
        super().__init__(name)
        self.should_succeed = should_succeed
        self.delay = delay
        self.execution_count = 0

    async def tick(self):
        self.execution_count += 1
        print(f"  {self.name} executed (count: {self.execution_count})")
        
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        
        if self.should_succeed:
            return Status.SUCCESS
        else:
            return Status.FAILURE


# Custom composite node that executes children in random order
class RandomSelector(BaseNode):
    def __init__(self, name: str, children: list = None):
        super().__init__(name, children)
        self.executed_children = set()

    async def tick(self):
        if not self.children:
            return Status.FAILURE
        
        # Get unexecuted children
        available_children = [child for child in self.children 
                            if child not in self.executed_children]
        
        if not available_children:
            # All children executed, reset and return success
            self.executed_children.clear()
            return Status.SUCCESS
        
        # Select random child
        import random
        selected_child = random.choice(available_children)
        self.executed_children.add(selected_child)
        
        result = await selected_child.tick()
        return result


# Custom composite node that executes children in priority order
class PrioritySelector(BaseNode):
    def __init__(self, name: str, children: list = None):
        super().__init__(name, children)

    async def tick(self):
        if not self.children:
            return Status.FAILURE
        
        # Execute children in order until one succeeds
        for child in self.children:
            result = await child.tick()
            if result == Status.SUCCESS:
                return Status.SUCCESS
            elif result == Status.RUNNING:
                return Status.RUNNING
        
        return Status.FAILURE


# Custom composite node that executes children with timeout
class TimeoutSequence(BaseNode):
    def __init__(self, name: str, timeout: float = 2.0, children: list = None):
        super().__init__(name, children)
        self.timeout = timeout
        self.start_time = None

    async def tick(self):
        if not self.children:
            return Status.SUCCESS
        
        if self.start_time is None:
            self.start_time = asyncio.get_event_loop().time()
        
        # Check timeout
        current_time = asyncio.get_event_loop().time()
        if current_time - self.start_time > self.timeout:
            print(f"  {self.name} timeout reached")
            self.start_time = None
            return Status.FAILURE
        
        # Execute children in sequence
        for child in self.children:
            result = await child.tick()
            if result == Status.FAILURE:
                self.start_time = None
                return Status.FAILURE
            elif result == Status.RUNNING:
                return Status.RUNNING
        
        self.start_time = None
        return Status.SUCCESS


async def main():
    print("=== Composite Nodes Example ===\n")

    # Create blackboard
    blackboard = Blackboard()

    # 1. Sequence Node
    print("1. Sequence Node")
    print("   Executes children in order, fails if any child fails")
    
    seq = Sequence("TestSequence", [
        SimpleAction("Action1", should_succeed=True),
        SimpleAction("Action2", should_succeed=True),
        SimpleAction("Action3", should_succeed=True)
    ])
    seq.set_blackboard(blackboard)
    
    result = await seq.tick()
    print(f"   Sequence result: {result}\n")
    
    # Sequence with failure
    seq_fail = Sequence("TestSequenceFail", [
        SimpleAction("Action1", should_succeed=True),
        SimpleAction("Action2", should_succeed=False),
        SimpleAction("Action3", should_succeed=True)
    ])
    seq_fail.set_blackboard(blackboard)
    
    result = await seq_fail.tick()
    print(f"   Sequence with failure result: {result}\n")

    # 2. Selector Node
    print("2. Selector Node")
    print("   Executes children in order, succeeds if any child succeeds")
    
    sel = Selector("TestSelector", [
        SimpleAction("Action1", should_succeed=False),
        SimpleAction("Action2", should_succeed=True),
        SimpleAction("Action3", should_succeed=False)
    ])
    sel.set_blackboard(blackboard)
    
    result = await sel.tick()
    print(f"   Selector result: {result}\n")
    
    # Selector with all failures
    sel_fail = Selector("TestSelectorFail", [
        SimpleAction("Action1", should_succeed=False),
        SimpleAction("Action2", should_succeed=False),
        SimpleAction("Action3", should_succeed=False)
    ])
    sel_fail.set_blackboard(blackboard)
    
    result = await sel_fail.tick()
    print(f"   Selector with all failures result: {result}\n")

    # 3. Parallel Node
    print("3. Parallel Node")
    print("   Executes all children concurrently")
    
    par = Parallel("TestParallel", [
        SimpleAction("Action1", should_succeed=True, delay=0.2),
        SimpleAction("Action2", should_succeed=True, delay=0.1),
        SimpleAction("Action3", should_succeed=True, delay=0.3)
    ])
    par.set_blackboard(blackboard)
    
    result = await par.tick()
    print(f"   Parallel result: {result}\n")
    
    # Parallel with mixed results
    par_mixed = Parallel("TestParallelMixed", [
        SimpleAction("Action1", should_succeed=True, delay=0.1),
        SimpleAction("Action2", should_succeed=False, delay=0.1),
        SimpleAction("Action3", should_succeed=True, delay=0.1)
    ])
    par_mixed.set_blackboard(blackboard)
    
    result = await par_mixed.tick()
    print(f"   Parallel with mixed results: {result}\n")

    # 4. Custom Composite Nodes
    print("4. Custom Composite Nodes")
    
    # Random Selector
    random_sel = RandomSelector("TestRandomSelector", [
        SimpleAction("Action1", should_succeed=True),
        SimpleAction("Action2", should_succeed=True),
        SimpleAction("Action3", should_succeed=True)
    ])
    random_sel.set_blackboard(blackboard)
    
    print("   Random Selector (executes children in random order):")
    for i in range(3):
        result = await random_sel.tick()
        print(f"   Execution {i+1}: {result}")
    print()
    
    # Priority Selector
    priority_sel = PrioritySelector("TestPrioritySelector", [
        SimpleAction("Action1", should_succeed=False),
        SimpleAction("Action2", should_succeed=True),
        SimpleAction("Action3", should_succeed=True)
    ])
    priority_sel.set_blackboard(blackboard)
    
    result = await priority_sel.tick()
    print(f"   Priority Selector result: {result}\n")
    
    # Timeout Sequence
    timeout_seq = TimeoutSequence("TestTimeoutSequence", timeout=0.5, children=[
        SimpleAction("Action1", should_succeed=True, delay=0.2),
        SimpleAction("Action2", should_succeed=True, delay=0.2),
        SimpleAction("Action3", should_succeed=True, delay=0.2)
    ])
    timeout_seq.set_blackboard(blackboard)
    
    result = await timeout_seq.tick()
    print(f"   Timeout Sequence result: {result}\n")

    # 5. Nested Composite Nodes
    print("5. Nested Composite Nodes")
    print("   Combining different composite node types")
    
    nested = Sequence("NestedTest", [
        Selector("InnerSelector", [
            SimpleAction("Action1", should_succeed=False),
            SimpleAction("Action2", should_succeed=True)
        ]),
        Parallel("InnerParallel", [
            SimpleAction("Action3", should_succeed=True),
            SimpleAction("Action4", should_succeed=True)
        ])
    ])
    nested.set_blackboard(blackboard)
    
    result = await nested.tick()
    print(f"   Nested composite result: {result}")

    print("\n=== Example completed ===")


if __name__ == "__main__":
    asyncio.run(main()) 