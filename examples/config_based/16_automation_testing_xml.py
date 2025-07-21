#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 16: Automation Testing - XML Configuration Version

This is the XML configuration version of the Automation Testing example.
It demonstrates how to configure automation testing systems using XML.

Key Learning Points:
    - How to define automation testing using XML
    - How to configure test case management
    - How to implement test execution workflow with XML
    - Understanding test reporting in XML
"""

import asyncio
import json
import random
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path
from abtree import (
    BehaviorTree, Sequence, Selector, Action, Condition, Status,
    register_node,
)
from abtree.engine.blackboard import Blackboard


@dataclass
class TestCase:
    """Test case class"""
    id: str
    name: str
    description: str
    category: str
    priority: int  # 1-5, 5 is highest
    timeout: float
    dependencies: List[str]
    setup_data: Dict[str, Any]
    expected_result: Dict[str, Any]
    status: str = "pending"  # pending, running, passed, failed, skipped
    execution_time: float = 0.0
    error_message: str = ""
    start_time: float = 0.0
    end_time: float = 0.0


@dataclass
class TestSuite:
    """Test suite class"""
    id: str
    name: str
    description: str
    test_cases: List[TestCase]
    total_count: int = 0
    passed_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    execution_time: float = 0.0


class TestManager:
    """Test manager"""
    
    def __init__(self, name):
        self.name = name
        self.test_suites = {}
        self.current_suite = None
        self.test_results = []
        self.test_data = {}
        self.environment = {}
        self.report_path = "test_reports"
        
        # Create report directory
        Path(self.report_path).mkdir(exist_ok=True)
    
    def add_test_suite(self, suite: TestSuite):
        """Add test suite"""
        self.test_suites[suite.id] = suite
        print(f"Test manager {self.name}: Added test suite {suite.name}")
    
    def get_test_case(self, case_id: str) -> Optional[TestCase]:
        """Get test case"""
        for suite in self.test_suites.values():
            for case in suite.test_cases:
                if case.id == case_id:
                    return case
        return None
    
    def update_test_result(self, case_id: str, status: str, execution_time: float = 0.0, error_message: str = ""):
        """Update test result"""
        test_case = self.get_test_case(case_id)
        if test_case:
            test_case.status = status
            test_case.execution_time = execution_time
            test_case.error_message = error_message
            test_case.end_time = time.time()
            
            print(f"Test result updated: {case_id} -> {status}")
    
    def save_test_report(self):
        """Save test report"""
        report_data = {
            'timestamp': time.time(),
            'test_suites': [asdict(suite) for suite in self.test_suites.values()],
            'summary': self.get_summary()
        }
        
        report_file = f"{self.report_path}/test_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"Test report saved: {report_file}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test summary"""
        total_cases = 0
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        
        for suite in self.test_suites.values():
            for case in suite.test_cases:
                total_cases += 1
                if case.status == "passed":
                    total_passed += 1
                elif case.status == "failed":
                    total_failed += 1
                elif case.status == "skipped":
                    total_skipped += 1
        
        return {
            'total_cases': total_cases,
            'passed': total_passed,
            'failed': total_failed,
            'skipped': total_skipped,
            'success_rate': total_passed / total_cases if total_cases > 0 else 0
        }


class TestCaseExecutionAction(Action):
    """Execute a specific test case"""
    
    def __init__(self, name, case_id, **kwargs):
        super().__init__(name=name, **kwargs)
        self.case_id = case_id
    
    async def execute(self, blackboard):
        test_manager = blackboard.get("test_manager")
        if not test_manager:
            print(f"Test case execution {self.name}: Test manager not found")
            return Status.FAILURE
        
        test_case = test_manager.get_test_case(self.case_id)
        if not test_case:
            print(f"Test case execution {self.name}: Test case {self.case_id} not found")
            return Status.FAILURE
        
        print(f"Executing test case: {test_case.name}")
        start_time = time.time()
        
        try:
            # Simulate test execution
            await asyncio.sleep(0.01)
            
            # Simulate test result (80% success rate)
            if random.random() < 0.8:
                status = "passed"
                print(f"Test case {test_case.name} passed")
            else:
                status = "failed"
                print(f"Test case {test_case.name} failed")
            
            execution_time = time.time() - start_time
            test_manager.update_test_result(self.case_id, status, execution_time)
            
            return Status.SUCCESS
        except Exception as e:
            execution_time = time.time() - start_time
            test_manager.update_test_result(self.case_id, "failed", execution_time, str(e))
            return Status.FAILURE


class TestSuiteExecutionAction(Action):
    """Execute a test suite"""
    
    def __init__(self, name, suite_id, **kwargs):
        super().__init__(name=name, **kwargs)
        self.suite_id = suite_id
    
    async def execute(self, blackboard):
        test_manager = blackboard.get("test_manager")
        if not test_manager:
            print(f"Test suite execution {self.name}: Test manager not found")
            return Status.FAILURE
        
        test_suite = test_manager.test_suites.get(self.suite_id)
        if not test_suite:
            print(f"Test suite execution {self.name}: Test suite {self.suite_id} not found")
            return Status.FAILURE
        
        print(f"Executing test suite: {test_suite.name}")
        
        # Execute all test cases in the suite
        for test_case in test_suite.test_cases:
            # Create and execute test case action
            case_action = TestCaseExecutionAction(f"Execute {test_case.id}", test_case.id)
            await case_action.execute(blackboard)
        
        return Status.SUCCESS


class TestDataPreparationAction(Action):
    """Prepare test data"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
    
    async def execute(self, blackboard):
        test_manager = blackboard.get("test_manager")
        if not test_manager:
            print(f"Test data preparation {self.name}: Test manager not found")
            return Status.FAILURE
        
        print(f"Preparing test data: {self.name}")
        await asyncio.sleep(0.01)
        
        # Simulate data preparation
        test_manager.test_data = {
            "users": [{"id": 1, "username": "testuser", "password": "testpass"}],
            "products": [{"id": 1, "name": "Laptop", "price": 999.99}],
            "orders": []
        }
        
        blackboard.set("test_data_ready", True)
        print("Test data preparation completed")
        return Status.SUCCESS


class EnvironmentSetupAction(Action):
    """Setup test environment"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
    
    async def execute(self, blackboard):
        test_manager = blackboard.get("test_manager")
        if not test_manager:
            print(f"Environment setup {self.name}: Test manager not found")
            return Status.FAILURE
        
        print(f"Setting up test environment: {self.name}")
        await asyncio.sleep(0.01)
        
        # Simulate environment setup
        test_manager.environment = {
            "database": "test_db",
            "api_endpoint": "http://localhost:8000",
            "browser": "chrome",
            "timeout": 30
        }
        
        blackboard.set("environment_ready", True)
        print("Test environment setup completed")
        return Status.SUCCESS


class TestResultAnalysisAction(Action):
    """Analyze test results"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
    
    async def execute(self, blackboard):
        test_manager = blackboard.get("test_manager")
        if not test_manager:
            print(f"Test result analysis {self.name}: Test manager not found")
            return Status.FAILURE
        
        print(f"Analyzing test results: {self.name}")
        await asyncio.sleep(0.01)
        
        summary = test_manager.get_summary()
        print(f"Test result summary: {summary}")
        
        return Status.SUCCESS


class TestReportGenerationAction(Action):
    """Generate test report"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
    
    async def execute(self, blackboard):
        test_manager = blackboard.get("test_manager")
        if not test_manager:
            print(f"Test report generation {self.name}: Test manager not found")
            return Status.FAILURE
        
        print(f"Generating test report: {self.name}")
        await asyncio.sleep(0.01)
        
        # Save test report
        test_manager.save_test_report()
        
        # Generate HTML report
        html_report = self.generate_html_report(test_manager)
        report_file = f"{test_manager.report_path}/test_report_{int(time.time())}.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"HTML report generated: {report_file}")
        return Status.SUCCESS
    
    def generate_html_report(self, test_manager) -> str:
        """Generate HTML test report"""
        summary = test_manager.get_summary()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
                .suite {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
                .case {{ margin: 5px 0; padding: 5px; background: #f9f9f9; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                .skipped {{ color: orange; }}
            </style>
        </head>
        <body>
            <h1>Automated Test Report</h1>
            <div class="summary">
                <h2>Test Summary</h2>
                <p>Total Cases: {summary['total_cases']}</p>
                <p>Passed: <span class="passed">{summary['passed']}</span></p>
                <p>Failed: <span class="failed">{summary['failed']}</span></p>
                <p>Skipped: <span class="skipped">{summary['skipped']}</span></p>
                <p>Execution Time: {summary['total_time']:.2f} seconds</p>
            </div>
        </body>
        </html>
        """
        return html


class TestDataReadyCondition(Condition):
    """Check if test data is ready"""
    
    async def evaluate(self, blackboard):
        return blackboard.get("test_data_ready", False)


class EnvironmentReadyCondition(Condition):
    """Check if test environment is ready"""
    
    async def evaluate(self, blackboard):
        return blackboard.get("environment_ready", False)


class TestExecutionCompleteCondition(Condition):
    """Check if test execution is complete"""
    
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
    
    async def evaluate(self, blackboard):
        test_manager = blackboard.get("test_manager")
        if not test_manager:
            print(f"Test execution completion check {self.name}: Test manager not found")
            return False
        
        # Check if all test cases are completed
        total_cases = 0
        completed_cases = 0
        
        for suite in test_manager.test_suites.values():
            for case in suite.test_cases:
                total_cases += 1
                if case.status in ["passed", "failed", "skipped"]:
                    completed_cases += 1
        
        return completed_cases >= total_cases if total_cases > 0 else True


def register_custom_nodes():
    """Register custom node types"""
    register_node("TestCaseExecutionAction", TestCaseExecutionAction)
    register_node("TestSuiteExecutionAction", TestSuiteExecutionAction)
    register_node("TestDataPreparationAction", TestDataPreparationAction)
    register_node("EnvironmentSetupAction", EnvironmentSetupAction)
    register_node("TestResultAnalysisAction", TestResultAnalysisAction)
    register_node("TestReportGenerationAction", TestReportGenerationAction)
    register_node("TestDataReadyCondition", TestDataReadyCondition)
    register_node("EnvironmentReadyCondition", EnvironmentReadyCondition)
    register_node("TestExecutionCompleteCondition", TestExecutionCompleteCondition)


async def main():
    """Main function - Demonstrate XML-based automation testing configuration"""
    
    print("=== ABTree Automation Testing XML Configuration Example ===\n")
    
    # Register custom node types
    register_custom_nodes()
    
    # Create test manager
    test_manager = TestManager("AutomationTestManager")
    
    # Create test cases
    test_cases = [
        TestCase(
            id="TC001",
            name="User Login Test",
            description="Test user login functionality",
            category="authentication",
            priority=5,
            timeout=30.0,
            dependencies=[],
            setup_data={"username": "testuser", "password": "testpass"},
            expected_result={"status": "success", "redirect": "/dashboard"}
        ),
        TestCase(
            id="TC002",
            name="Product Search Test",
            description="Test product search functionality",
            category="search",
            priority=4,
            timeout=20.0,
            dependencies=[],
            setup_data={"search_term": "laptop", "category": "electronics"},
            expected_result={"results_count": 10, "has_results": True}
        ),
        TestCase(
            id="TC003",
            name="Order Creation Test",
            description="Test order creation functionality",
            category="order",
            priority=5,
            timeout=45.0,
            dependencies=["TC001"],
            setup_data={"product_id": 1, "quantity": 2, "user_id": 1},
            expected_result={"order_id": "not_null", "status": "pending"}
        )
    ]
    
    # Create test suite
    test_suite = TestSuite(
        id="TS001",
        name="Functional Test Suite",
        description="Basic functional tests",
        test_cases=test_cases
    )
    
    # Add test suite
    test_manager.add_test_suite(test_suite)
    
    # Create blackboard
    blackboard = Blackboard()
    blackboard.set("test_manager", test_manager)
    blackboard.set("test_data_ready", False)
    blackboard.set("environment_ready", False)
    
    # Create behavior tree
    tree = BehaviorTree()
    
    # Define XML configuration string
    xml_config = '''
    <BehaviorTree name="AutomationTestingXML" description="Automation testing with XML configuration">
        <Sequence name="Test Execution Workflow">
            <!-- Environment setup -->
            <Sequence name="Environment Setup">
                <EnvironmentSetupAction name="Setup Environment" />
                <EnvironmentReadyCondition name="Check Environment Ready" />
            </Sequence>
            
            <!-- Test data preparation -->
            <Sequence name="Test Data Preparation">
                <TestDataPreparationAction name="Prepare Test Data" />
                <TestDataReadyCondition name="Check Test Data Ready" />
            </Sequence>
            
            <!-- Test suite execution -->
            <Sequence name="Test Suite Execution">
                <TestSuiteExecutionAction name="Execute Test Suite" suite_id="TS001" />
                <TestExecutionCompleteCondition name="Check Execution Complete" />
            </Sequence>
            
            <!-- Result analysis and reporting -->
            <Sequence name="Result Analysis and Reporting">
                <TestResultAnalysisAction name="Analyze Test Results" />
                <TestReportGenerationAction name="Generate Test Report" />
            </Sequence>
        </Sequence>
    </BehaviorTree>
    '''
    
    # Load XML configuration
    tree.load_from_string(xml_config)
    
    print("Automation testing behavior tree configured:")
    print("  - Environment setup: Prepare test environment")
    print("  - Test data preparation: Prepare test data")
    print("  - Test suite execution: Execute test cases")
    print("  - Result analysis and reporting: Generate test report")
    
    # Execute behavior tree
    print("\n=== Starting automation testing ===")
    
    result = await tree.tick()
    print(f"\nTest execution completed! Result: {result}")
    
    # Display final summary
    summary = test_manager.get_summary()
    print(f"\nTest Summary:")
    print(f"  Total test cases: {summary['total_cases']}")
    print(f"  Passed: {summary['passed']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Skipped: {summary['skipped']}")
    print(f"  Success rate: {summary['success_rate']:.1%}")


if __name__ == "__main__":
    asyncio.run(main()) 