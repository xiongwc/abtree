#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 16: Automation Testing System - Automation Testing Application

Demonstrates how to use ABTree to build automation testing systems, including test case management,
test execution workflow, error detection and reporting, test data management, and continuous integration.

Learning Points:
- Test case management
- Test execution workflow
- Error detection and reporting
- Test data management
- Continuous integration
- How to configure automation testing system through XML strings
"""

import asyncio
import json
import random
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path
from abtree import BehaviorTree, Sequence, Selector, Action, Condition, register_node
from abtree.core import Status
from abtree.parser.xml_parser import XMLParser


# Register custom node types
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
        print(f"Test Manager {self.name}: Added test suite {suite.name}")
    
    def get_test_case(self, case_id: str) -> Optional[TestCase]:
        """Get test case"""
        for suite in self.test_suites.values():
            for case in suite.test_cases:
                if case.id == case_id:
                    return case
        return None
    
    def update_test_result(self, case_id: str, status: str, execution_time: float = 0.0, error_message: str = ""):
        """Update test result"""
        case = self.get_test_case(case_id)
        if case:
            case.status = status
            case.execution_time = execution_time
            case.error_message = error_message
            case.end_time = time.time()
            
            # Update suite statistics
            if case.status == "passed":
                case.suite.passed_count += 1
            elif case.status == "failed":
                case.suite.failed_count += 1
            elif case.status == "skipped":
                case.suite.skipped_count += 1
            
            print(f"Test Manager {self.name}: Updated test result {case_id} -> {status}")
    
    def save_test_report(self):
        """Save test report"""
        report_file = f"{self.report_path}/test_report_{int(time.time())}.json"
        
        report_data = {
            "timestamp": time.time(),
            "summary": self.get_summary(),
            "test_suites": {suite_id: asdict(suite) for suite_id, suite in self.test_suites.items()},
            "test_results": self.test_results,
            "environment": self.environment
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"Test Manager {self.name}: Test report saved to {report_file}")
        return report_file
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test summary"""
        total_cases = 0
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        total_time = 0.0
        
        for suite in self.test_suites.values():
            total_cases += suite.total_count
            total_passed += suite.passed_count
            total_failed += suite.failed_count
            total_skipped += suite.skipped_count
            total_time += suite.execution_time
        
        return {
            "total_cases": total_cases,
            "passed": total_passed,
            "failed": total_failed,
            "skipped": total_skipped,
            "success_rate": total_passed / total_cases if total_cases > 0 else 0.0,
            "total_time": total_time
        }


class TestCaseExecutionAction(Action):
    """Test case execution action"""
    
    def __init__(self, name, test_manager, case_id):
        super().__init__(name)
        self.test_manager = test_manager
        self.case_id = case_id
    
    async def execute(self, blackboard):
        case = self.test_manager.get_test_case(self.case_id)
        if not case:
            print(f"Test case {self.case_id} not found")
            return Status.FAILURE
        
        print(f"Executing test case: {case.name}")
        case.status = "running"
        case.start_time = time.time()
        
        # Simulate test execution
        await asyncio.sleep(0.01)  # Fast simulation
        
        # Simulate test result
        success_rate = 0.8
        if random.random() < success_rate:
            case.status = "passed"
            print(f"Test case {case.name} passed")
        else:
            case.status = "failed"
            case.error_message = "Simulated test failure"
            print(f"Test case {case.name} failed")
        
        case.execution_time = time.time() - case.start_time
        case.end_time = time.time()
        
        # Update test manager
        self.test_manager.update_test_result(
            self.case_id, 
            case.status, 
            case.execution_time, 
            case.error_message
        )
        
        return Status.SUCCESS if case.status == "passed" else Status.FAILURE


class TestSuiteExecutionAction(Action):
    """Test suite execution action"""
    
    def __init__(self, name, test_manager, suite_id):
        super().__init__(name)
        self.test_manager = test_manager
        self.suite_id = suite_id
    
    async def execute(self, blackboard):
        suite = self.test_manager.test_suites.get(self.suite_id)
        if not suite:
            print(f"Test suite {self.suite_id} not found")
            return Status.FAILURE
        
        print(f"Executing test suite: {suite.name}")
        suite.start_time = time.time()
        
        # Execute all test cases in the suite
        for case in suite.test_cases:
            execution_action = TestCaseExecutionAction(f"Execute {case.id}", self.test_manager, case.id)
            await execution_action.execute(blackboard)
        
        suite.execution_time = time.time() - suite.start_time
        print(f"Test suite {suite.name} completed")
        
        return Status.SUCCESS


class TestDataPreparationAction(Action):
    """Test data preparation action"""
    
    def __init__(self, name, test_manager):
        super().__init__(name)
        self.test_manager = test_manager
    
    async def execute(self, blackboard):
        print("Preparing test data...")
        await asyncio.sleep(0.01)
        
        # Prepare test data
        test_data = {
            "users": [
                {"id": 1, "name": "Test User 1", "email": "test1@example.com"},
                {"id": 2, "name": "Test User 2", "email": "test2@example.com"},
                {"id": 3, "name": "Test User 3", "email": "test3@example.com"}
            ],
            "products": [
                {"id": 1, "name": "Product A", "price": 100.0},
                {"id": 2, "name": "Product B", "price": 200.0},
                {"id": 3, "name": "Product C", "price": 300.0}
            ]
        }
        
        self.test_manager.test_data = test_data
        print("Test data preparation completed")
        
        return Status.SUCCESS


class EnvironmentSetupAction(Action):
    """Environment setup action"""
    
    async def execute(self, blackboard):
        print("Setting up test environment...")
        await asyncio.sleep(0.01)
        
        # Simulate environment setup
        environment = {
            "database": "test_db",
            "api_endpoint": "https://api.test.com",
            "timeout": 30,
            "retry_count": 3
        }
        
        blackboard.set("environment", environment)
        print("Test environment setup completed")
        
        return Status.SUCCESS


class TestResultAnalysisAction(Action):
    """Test result analysis action"""
    
    def __init__(self, name, test_manager):
        super().__init__(name)
        self.test_manager = test_manager
    
    async def execute(self, blackboard):
        print("Analyzing test results...")
        await asyncio.sleep(0.01)
        
        summary = self.test_manager.get_summary()
        
        # Analyze results
        if summary["success_rate"] >= 0.8:
            print("Test analysis: Good success rate")
            blackboard.set("test_quality", "good")
        elif summary["success_rate"] >= 0.6:
            print("Test analysis: Acceptable success rate")
            blackboard.set("test_quality", "acceptable")
        else:
            print("Test analysis: Poor success rate")
            blackboard.set("test_quality", "poor")
        
        return Status.SUCCESS


class TestReportGenerationAction(Action):
    """Test report generation action"""
    
    def __init__(self, name, test_manager):
        super().__init__(name)
        self.test_manager = test_manager
    
    async def execute(self, blackboard):
        print("Generating test report...")
        await asyncio.sleep(0.01)
        
        # Save test report
        report_file = self.test_manager.save_test_report()
        
        # Generate HTML report
        html_report = self.generate_html_report()
        html_file = f"{self.test_manager.report_path}/test_report_{int(time.time())}.html"
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"Test report generated: {html_file}")
        return Status.SUCCESS
    
    def generate_html_report(self) -> str:
        """Generate HTML test report"""
        summary = self.test_manager.get_summary()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: white; border-radius: 3px; }}
                .success {{ color: green; }}
                .failure {{ color: red; }}
                .warning {{ color: orange; }}
            </style>
        </head>
        <body>
            <h1>Test Report</h1>
            <div class="summary">
                <h2>Summary</h2>
                <div class="metric">Total Cases: {summary['total_cases']}</div>
                <div class="metric success">Passed: {summary['passed']}</div>
                <div class="metric failure">Failed: {summary['failed']}</div>
                <div class="metric warning">Skipped: {summary['skipped']}</div>
                <div class="metric">Success Rate: {summary['success_rate']:.1%}</div>
                <div class="metric">Total Time: {summary['total_time']:.2f}s</div>
            </div>
        </body>
        </html>
        """
        
        return html


class TestDataReadyCondition(Condition):
    """Test data ready condition"""
    
    async def evaluate(self, blackboard):
        test_data = blackboard.get("test_data", {})
        return len(test_data) > 0


class EnvironmentReadyCondition(Condition):
    """Environment ready condition"""
    
    async def evaluate(self, blackboard):
        environment = blackboard.get("environment", {})
        required_keys = ["database", "api_endpoint", "timeout"]
        return all(key in environment for key in required_keys)


class TestExecutionCompleteCondition(Condition):
    """Test execution complete condition"""
    
    def __init__(self, name, test_manager):
        super().__init__(name)
        self.test_manager = test_manager
    
    async def evaluate(self, blackboard):
        # Check if all test cases are completed
        for suite in self.test_manager.test_suites.values():
            for case in suite.test_cases:
                if case.status in ["pending", "running"]:
                    return False
        return True


async def main():
    """Main function - demonstrate automation testing system"""
    
    # Register custom node types
    register_custom_nodes()
    
    print("=== ABTree Automation Testing Example ===\n")
    
    # Create test manager
    test_manager = TestManager("Automation Test Manager")
    
    # Create test cases
    test_cases = [
        TestCase("TC001", "User Login Test", "Test user login functionality", "authentication", 5, 30.0, [], {}, {"status": "success"}),
        TestCase("TC002", "Product Search Test", "Test product search functionality", "search", 4, 20.0, [], {}, {"results_count": 10}),
        TestCase("TC003", "Order Creation Test", "Test order creation process", "order", 5, 45.0, ["TC001"], {}, {"order_id": "12345"}),
        TestCase("TC004", "Payment Processing Test", "Test payment processing", "payment", 5, 60.0, ["TC003"], {}, {"payment_status": "completed"}),
        TestCase("TC005", "User Registration Test", "Test user registration", "registration", 3, 25.0, [], {}, {"user_id": "new_user"})
    ]
    
    # Create test suite
    test_suite = TestSuite("TS001", "E-commerce Test Suite", "Complete e-commerce functionality tests", test_cases)
    test_suite.total_count = len(test_cases)
    
    # Add test suite to manager
    test_manager.add_test_suite(test_suite)
    
    # Create behavior tree
    root = Sequence("Automation Testing Workflow")
    
    # Test data preparation branch
    data_prep_branch = Sequence("Data Preparation")
    data_prep_branch.add_child(TestDataPreparationAction("Prepare Test Data", test_manager))
    
    # Environment setup branch
    env_setup_branch = Sequence("Environment Setup")
    env_setup_branch.add_child(EnvironmentSetupAction("Setup Environment"))
    
    # Test execution branch
    test_exec_branch = Sequence("Test Execution")
    test_exec_branch.add_child(TestSuiteExecutionAction("Execute Test Suite", test_manager, "TS001"))
    
    # Result analysis branch
    analysis_branch = Sequence("Result Analysis")
    analysis_branch.add_child(TestResultAnalysisAction("Analyze Results", test_manager))
    
    # Report generation branch
    report_branch = Sequence("Report Generation")
    report_branch.add_child(TestReportGenerationAction("Generate Report", test_manager))
    
    # Assemble behavior tree
    root.add_child(data_prep_branch)
    root.add_child(env_setup_branch)
    root.add_child(test_exec_branch)
    root.add_child(analysis_branch)
    root.add_child(report_branch)
    
    # Create behavior tree instance
    tree = BehaviorTree()
    tree.load_from_root(root)
    blackboard = tree.blackboard
    
    print("Starting automation testing workflow...")
    print("=" * 50)
    
    # Execute behavior tree
    result = await tree.tick()
    
    print(f"\nAutomation testing completed! Result: {result}")
    
    # Display final summary
    summary = test_manager.get_summary()
    print(f"\nFinal Test Summary:")
    print(f"Total Cases: {summary['total_cases']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']:.1%}")
    print(f"Total Time: {summary['total_time']:.2f}s")


if __name__ == "__main__":
    asyncio.run(main()) 