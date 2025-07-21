#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 15: Automation Testing System - Automation Testing Application

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


# 注册自定义节点类型
def register_custom_nodes():
    """注册自定义节点类型"""
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
        print(f"测试管理器 {self.name}: 添加测试套件 {suite.name}")
    
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
            
            print(f"测试管理器 {self.name}: 更新测试结果 {case_id} -> {status}")
    
    def save_test_report(self):
        """Save test report"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = f"{self.report_path}/test_report_{timestamp}.json"
        
        report_data = {
            "timestamp": timestamp,
            "test_manager": self.name,
            "suites": [asdict(suite) for suite in self.test_suites.values()],
            "environment": self.environment,
            "summary": self.get_summary()
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"测试管理器 {self.name}: 测试报告已保存到 {report_file}")
        return report_file
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test summary"""
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        total_time = 0.0
        
        for suite in self.test_suites.values():
            total_tests += suite.total_count
            total_passed += suite.passed_count
            total_failed += suite.failed_count
            total_skipped += suite.skipped_count
            total_time += suite.execution_time
        
        return {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "skipped": total_skipped,
            "success_rate": total_passed / total_tests if total_tests > 0 else 0,
            "total_time": total_time
        }


class TestCaseExecutionAction(Action):
    """Test case execution action"""
    
    def __init__(self, name, test_manager, case_id):
        super().__init__(name)
        self.test_manager = test_manager
        self.case_id = case_id
    
    async def execute(self, blackboard):
        print(f"Test case execution action {self.name}: Start executing test case {self.case_id}")
        
        case = self.test_manager.get_test_case(self.case_id)
        if not case:
            print(f"Test case execution action {self.name}: Test case {self.case_id} does not exist")
            return Status.FAILURE
        
        # Update status to running
        case.status = "running"
        case.start_time = time.time()
        
        # Simulate test execution
        try:
            # Check dependencies
            for dep in case.dependencies:
                dep_case = self.test_manager.get_test_case(dep)
                if dep_case and dep_case.status != "passed":
                    case.status = "skipped"
                    case.error_message = f"Dependency test case {dep} failed"
                    self.test_manager.update_test_result(self.case_id, "skipped", 0, case.error_message)
                    return Status.FAILURE
            
            # Execute test
            await asyncio.sleep(random.uniform(0.5, 2.0))  # Simulate test time
            
            # Simulate test result
            success_rate = 0.8  # 80% success rate
            if random.random() < success_rate:
                case.status = "passed"
                execution_time = time.time() - case.start_time
                self.test_manager.update_test_result(self.case_id, "passed", execution_time)
                print(f"Test case execution action {self.name}: Test passed")
                return Status.SUCCESS
            else:
                case.status = "failed"
                execution_time = time.time() - case.start_time
                error_message = f"Test failed: Expected result mismatch"
                self.test_manager.update_test_result(self.case_id, "failed", execution_time, error_message)
                print(f"Test case execution action {self.name}: Test failed")
                return Status.FAILURE
                
        except Exception as e:
            case.status = "failed"
            execution_time = time.time() - case.start_time
            error_message = f"Test exception: {str(e)}"
            self.test_manager.update_test_result(self.case_id, "failed", execution_time, error_message)
            print(f"Test case execution action {self.name}: Test exception")
            return Status.FAILURE


class TestSuiteExecutionAction(Action):
    """Test suite execution action"""
    
    def __init__(self, name, test_manager, suite_id):
        super().__init__(name)
        self.test_manager = test_manager
        self.suite_id = suite_id
    
    async def execute(self, blackboard):
        print(f"Test suite execution action {self.name}: Start executing test suite {self.suite_id}")
        
        suite = self.test_manager.test_suites.get(self.suite_id)
        if not suite:
            print(f"Test suite execution action {self.name}: Test suite {self.suite_id} does not exist")
            return Status.FAILURE
        
        self.test_manager.current_suite = suite
        suite_start_time = time.time()
        
        # Sort test cases by priority
        sorted_cases = sorted(suite.test_cases, key=lambda x: x.priority, reverse=True)
        
        # Execute all test cases
        for case in sorted_cases:
            if case.status == "pending":
                execution_action = TestCaseExecutionAction(f"执行{case.id}", self.test_manager, case.id)
                result = await execution_action.execute(blackboard)
                
                if result == Status.FAILURE:
                    print(f"Test suite execution action {self.name}: Test case {case.id} execution failed")
        
        suite.execution_time = time.time() - suite_start_time
        print(f"Test suite execution action {self.name}: Suite execution completed, time taken {suite.execution_time:.2f}s")
        
        return Status.SUCCESS


class TestDataPreparationAction(Action):
    """Test data preparation action"""
    
    def __init__(self, name, test_manager):
        super().__init__(name)
        self.test_manager = test_manager
    
    async def execute(self, blackboard):
        print(f"Test data preparation action {self.name}: Start preparing test data")
        
        # Prepare test data
        test_data = {
            "users": [
                {"id": 1, "name": "测试用户1", "email": "test1@example.com"},
                {"id": 2, "name": "测试用户2", "email": "test2@example.com"},
                {"id": 3, "name": "测试用户3", "email": "test3@example.com"}
            ],
            "products": [
                {"id": 1, "name": "产品A", "price": 100.0},
                {"id": 2, "name": "产品B", "price": 200.0},
                {"id": 3, "name": "产品C", "price": 300.0}
            ],
            "orders": [
                {"id": 1, "user_id": 1, "product_id": 1, "quantity": 2},
                {"id": 2, "user_id": 2, "product_id": 2, "quantity": 1},
                {"id": 3, "user_id": 3, "product_id": 3, "quantity": 3}
            ]
        }
        
        self.test_manager.test_data = test_data
        blackboard.set("test_data_ready", True)
        blackboard.set("test_data", test_data)
        
        await asyncio.sleep(0.5)
        print(f"Test data preparation action {self.name}: Test data preparation completed")
        return Status.SUCCESS


class EnvironmentSetupAction(Action):
    """Environment setup action"""
    
    def __init__(self, name, test_manager):
        super().__init__(name)
        self.test_manager = test_manager
    
    async def execute(self, blackboard):
        print(f"Environment setup action {self.name}: Start setting up test environment")
        
        # Set up test environment
        environment = {
            "database_url": "sqlite:///test.db",
            "api_base_url": "http://localhost:8000",
            "timeout": 30,
            "retry_count": 3,
            "log_level": "DEBUG"
        }
        
        self.test_manager.environment = environment
        blackboard.set("environment_ready", True)
        blackboard.set("environment", environment)
        
        await asyncio.sleep(0.3)
        print(f"Environment setup action {self.name}: Test environment setup completed")
        return Status.SUCCESS


class TestResultAnalysisAction(Action):
    """Test result analysis action"""
    
    def __init__(self, name, test_manager):
        super().__init__(name)
        self.test_manager = test_manager
    
    async def execute(self, blackboard):
        print(f"Test result analysis action {self.name}: Start analyzing test results")
        
        summary = self.test_manager.get_summary()
        
        # Analyze results
        analysis = {
            "total_tests": summary["total_tests"],
            "success_rate": summary["success_rate"],
            "failed_tests": summary["failed"],
            "execution_time": summary["total_time"],
            "recommendations": []
        }
        
        # Generate recommendations
        if summary["success_rate"] < 0.8:
            analysis["recommendations"].append("Low test success rate, recommend checking test case design")
        
        if summary["failed"] > 0:
            analysis["recommendations"].append("Failed test cases exist, need to fix")
        
        if summary["total_time"] > 300:  # 5 minutes
            analysis["recommendations"].append("Test execution time too long, recommend optimization")
        
        blackboard.set("test_analysis", analysis)
        
        await asyncio.sleep(0.2)
        print(f"Test result analysis action {self.name}: Analysis completed, success rate {summary['success_rate']:.1%}")
        return Status.SUCCESS


class TestReportGenerationAction(Action):
    """Test report generation action"""
    
    def __init__(self, name, test_manager):
        super().__init__(name)
        self.test_manager = test_manager
    
    async def execute(self, blackboard):
        print(f"Test report generation action {self.name}: Start generating test report")
        
        # Generate test report
        report_file = self.test_manager.save_test_report()
        
        # Generate HTML report
        html_report = self.generate_html_report()
        html_file = report_file.replace('.json', '.html')
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        blackboard.set("report_file", report_file)
        blackboard.set("html_report_file", html_file)
        
        await asyncio.sleep(0.3)
        print(f"Test report generation action {self.name}: Report generation completed")
        return Status.SUCCESS
    
    def generate_html_report(self) -> str:
        """Generate HTML report"""
        summary = self.test_manager.get_summary()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ margin: 20px 0; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e8f4f8; border-radius: 3px; }}
                .success {{ color: green; }}
                .failure {{ color: red; }}
                .warning {{ color: orange; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Automation Test Report</h1>
                <p>Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <h2>Test Summary</h2>
                <div class="metric">
                    <strong>Total Tests:</strong> {summary['total_tests']}
                </div>
                <div class="metric">
                    <strong>Passed:</strong> <span class="success">{summary['passed']}</span>
                </div>
                <div class="metric">
                    <strong>Failed:</strong> <span class="failure">{summary['failed']}</span>
                </div>
                <div class="metric">
                    <strong>Skipped:</strong> <span class="warning">{summary['skipped']}</span>
                </div>
                <div class="metric">
                    <strong>Success Rate:</strong> {summary['success_rate']:.1%}
                </div>
                <div class="metric">
                    <strong>Execution Time:</strong> {summary['total_time']:.2f}s
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


class TestDataReadyCondition(Condition):
    """Test data ready condition"""
    
    async def evaluate(self, blackboard):
        test_data_ready = blackboard.get("test_data_ready", False)
        print(f"Test data ready condition: {test_data_ready}")
        return test_data_ready


class EnvironmentReadyCondition(Condition):
    """Environment ready condition"""
    
    async def evaluate(self, blackboard):
        environment_ready = blackboard.get("environment_ready", False)
        print(f"Environment ready condition: {environment_ready}")
        return environment_ready


class TestExecutionCompleteCondition(Condition):
    """Test execution complete condition"""
    
    def __init__(self, name, test_manager):
        super().__init__(name)
        self.test_manager = test_manager
    
    async def evaluate(self, blackboard):
        # Check if all test cases are completed
        all_completed = True
        for suite in self.test_manager.test_suites.values():
            for case in suite.test_cases:
                if case.status == "pending":
                    all_completed = False
                    break
        
        print(f"Test execution complete condition: {all_completed}")
        return all_completed


async def main():
    """Main function - Demonstrate automation testing system"""
    
    # 注册自定义节点类型
    register_custom_nodes()
    
    print("=== ABTree Automation Testing System Example ===\n")
    
    # 1. Create test manager
    test_manager = TestManager("自动化测试管理器")
    
    # 2. Create test cases
    test_cases = [
        TestCase("TC001", "用户登录测试", "测试用户登录功能", "authentication", 5, 30.0, [], {}, {"status": "success"}),
        TestCase("TC002", "用户注册测试", "测试用户注册功能", "authentication", 4, 30.0, [], {}, {"status": "success"}),
        TestCase("TC003", "产品列表测试", "测试产品列表功能", "product", 3, 20.0, [], {}, {"status": "success"}),
        TestCase("TC004", "订单创建测试", "测试订单创建功能", "order", 5, 45.0, ["TC001", "TC003"], {}, {"status": "success"}),
        TestCase("TC005", "支付流程测试", "测试支付流程", "payment", 5, 60.0, ["TC004"], {}, {"status": "success"}),
        TestCase("TC006", "数据验证测试", "测试数据验证功能", "validation", 3, 15.0, [], {}, {"status": "success"}),
        TestCase("TC007", "性能测试", "测试系统性能", "performance", 4, 120.0, [], {}, {"status": "success"}),
        TestCase("TC008", "安全测试", "测试系统安全性", "security", 5, 90.0, [], {}, {"status": "success"})
    ]
    
    # 3. Create test suite
    test_suite = TestSuite(
        "SUITE001",
        "完整功能测试套件",
        "测试系统的所有主要功能",
        test_cases
    )
    test_suite.total_count = len(test_cases)
    
    test_manager.add_test_suite(test_suite)
    
    # 4. Create behavior tree
    root = Selector("自动化测试系统")
    
    # 5. Create test workflow
    # Environment preparation
    setup_sequence = Sequence("环境准备")
    setup_sequence.add_child(EnvironmentSetupAction("环境设置", test_manager))
    setup_sequence.add_child(EnvironmentReadyCondition("环境就绪检查"))
    
    # Data preparation
    data_sequence = Sequence("数据准备")
    data_sequence.add_child(TestDataPreparationAction("测试数据准备", test_manager))
    data_sequence.add_child(TestDataReadyCondition("数据就绪检查"))
    
    # Test execution
    execution_sequence = Sequence("测试执行")
    execution_sequence.add_child(TestSuiteExecutionAction("测试套件执行", test_manager, "SUITE001"))
    execution_sequence.add_child(TestExecutionCompleteCondition("执行完成检查", test_manager))
    
    # Result analysis
    analysis_sequence = Sequence("结果分析")
    analysis_sequence.add_child(TestResultAnalysisAction("测试结果分析", test_manager))
    
    # Report generation
    report_sequence = Sequence("报告生成")
    report_sequence.add_child(TestReportGenerationAction("测试报告生成", test_manager))
    
    # 6. Assemble behavior tree
    root.add_child(setup_sequence)
    root.add_child(data_sequence)
    root.add_child(execution_sequence)
    root.add_child(analysis_sequence)
    root.add_child(report_sequence)
    
    # 7. Create behavior tree instance
    tree = BehaviorTree()
    tree.load_from_root(root)
    blackboard = tree.blackboard
    
    # 8. Initialize data
    blackboard.set("test_data_ready", False)
    blackboard.set("environment_ready", False)
    
    print("Start executing automation testing system...")
    print("=" * 50)
    
    # 9. Execute tests
    result = await tree.tick()
    print(f"Automation test execution result: {result}")
    
    # 10. Display final results
    summary = test_manager.get_summary()
    print("\n=== Test Execution Complete ===")
    print(f"Total tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Success rate: {summary['success_rate']:.1%}")
    print(f"Total execution time: {summary['total_time']:.2f}s")
    
    # Display analysis results
    analysis = blackboard.get("test_analysis", {})
    if analysis:
        print(f"\n=== Test Analysis ===")
        print(f"Recommendations: {analysis.get('recommendations', [])}")
    
    # Display report files
    report_file = blackboard.get("report_file", "")
    html_file = blackboard.get("html_report_file", "")
    if report_file:
        print(f"\nTest reports generated:")
        print(f"JSON report: {report_file}")
        print(f"HTML report: {html_file}")
    
    # 11. 演示XML配置方式
    print("\n=== XML配置方式演示 ===")
    
    # 为XML配置创建简化的节点类
    class SimpleEnvironmentSetupAction(Action):
        """简化的环境设置动作"""
        
        async def execute(self, blackboard):
            print(f"Simple environment setup action {self.name}: Start setting up test environment")
            
            # Set up test environment
            environment = {
                "database_url": "sqlite:///test.db",
                "api_base_url": "http://localhost:8000",
                "timeout": 30,
                "retry_count": 3,
                "log_level": "DEBUG"
            }
            
            blackboard.set("environment_ready", True)
            blackboard.set("environment", environment)
            
            await asyncio.sleep(0.3)
            print(f"Simple environment setup action {self.name}: Test environment setup completed")
            return Status.SUCCESS

    class SimpleTestDataPreparationAction(Action):
        """简化的测试数据准备动作"""
        
        async def execute(self, blackboard):
            print(f"Simple test data preparation action {self.name}: Start preparing test data")
            
            # Prepare test data
            test_data = {
                "users": [
                    {"id": 1, "name": "测试用户1", "email": "test1@example.com"},
                    {"id": 2, "name": "测试用户2", "email": "test2@example.com"},
                    {"id": 3, "name": "测试用户3", "email": "test3@example.com"}
                ],
                "products": [
                    {"id": 1, "name": "产品A", "price": 100.0},
                    {"id": 2, "name": "产品B", "price": 200.0},
                    {"id": 3, "name": "产品C", "price": 300.0}
                ],
                "orders": [
                    {"id": 1, "user_id": 1, "product_id": 1, "quantity": 2},
                    {"id": 2, "user_id": 2, "product_id": 2, "quantity": 1},
                    {"id": 3, "user_id": 3, "product_id": 3, "quantity": 3}
                ]
            }
            
            blackboard.set("test_data_ready", True)
            blackboard.set("test_data", test_data)
            
            await asyncio.sleep(0.5)
            print(f"Simple test data preparation action {self.name}: Test data preparation completed")
            return Status.SUCCESS

    class SimpleTestSuiteExecutionAction(Action):
        """简化的测试套件执行动作"""
        
        async def execute(self, blackboard):
            print(f"Simple test suite execution action {self.name}: Start executing test suite")
            
            # Simulate test execution
            test_results = {
                "total_tests": 8,
                "passed": 7,
                "failed": 1,
                "skipped": 0,
                "success_rate": 0.875,
                "total_time": 45.2
            }
            
            blackboard.set("test_results", test_results)
            blackboard.set("test_execution_complete", True)
            
            await asyncio.sleep(0.4)
            print(f"Simple test suite execution action {self.name}: Test suite execution completed")
            return Status.SUCCESS

    class SimpleTestResultAnalysisAction(Action):
        """简化的测试结果分析动作"""
        
        async def execute(self, blackboard):
            print(f"Simple test result analysis action {self.name}: Start analyzing test results")
            
            test_results = blackboard.get("test_results", {})
            
            # Analyze results
            analysis = {
                "total_tests": test_results.get("total_tests", 0),
                "success_rate": test_results.get("success_rate", 0.0),
                "failed_tests": test_results.get("failed", 0),
                "execution_time": test_results.get("total_time", 0.0),
                "recommendations": []
            }
            
            # Generate recommendations
            if analysis["success_rate"] < 0.8:
                analysis["recommendations"].append("Low test success rate, recommend checking test case design")
            
            if analysis["failed_tests"] > 0:
                analysis["recommendations"].append("Failed test cases exist, need to fix")
            
            if analysis["execution_time"] > 300:  # 5 minutes
                analysis["recommendations"].append("Test execution time too long, recommend optimization")
            
            blackboard.set("test_analysis", analysis)
            
            await asyncio.sleep(0.2)
            print(f"Simple test result analysis action {self.name}: Analysis completed, success rate {analysis['success_rate']:.1%}")
            return Status.SUCCESS

    class SimpleTestReportGenerationAction(Action):
        """简化的测试报告生成动作"""
        
        async def execute(self, blackboard):
            print(f"Simple test report generation action {self.name}: Start generating test report")
            
            test_results = blackboard.get("test_results", {})
            analysis = blackboard.get("test_analysis", {})
            
            # Generate simple report
            report = {
                "timestamp": time.time(),
                "test_results": test_results,
                "analysis": analysis,
                "status": "completed"
            }
            
            blackboard.set("report", report)
            
            await asyncio.sleep(0.3)
            print(f"Simple test report generation action {self.name}: Report generation completed")
            return Status.SUCCESS

    class SimpleTestExecutionCompleteCondition(Condition):
        """简化的测试执行完成条件"""
        
        async def evaluate(self, blackboard):
            # Check if test execution is complete
            test_execution_complete = blackboard.get("test_execution_complete", False)
            return test_execution_complete

    # 注册简化的节点类型
    register_node("SimpleEnvironmentSetupAction", SimpleEnvironmentSetupAction)
    register_node("SimpleTestDataPreparationAction", SimpleTestDataPreparationAction)
    register_node("SimpleTestSuiteExecutionAction", SimpleTestSuiteExecutionAction)
    register_node("SimpleTestResultAnalysisAction", SimpleTestResultAnalysisAction)
    register_node("SimpleTestReportGenerationAction", SimpleTestReportGenerationAction)
    register_node("SimpleTestExecutionCompleteCondition", SimpleTestExecutionCompleteCondition)

    # XML字符串配置
    xml_config = '''
    <BehaviorTree name="AutomationTestingXML" description="XML配置的自动化测试系统示例">
        <Sequence name="根序列">
            <Selector name="自动化测试系统">
                <Sequence name="环境准备">
                    <SimpleEnvironmentSetupAction name="环境设置" />
                    <EnvironmentReadyCondition name="环境就绪检查" />
                </Sequence>
                <Sequence name="数据准备">
                    <SimpleTestDataPreparationAction name="测试数据准备" />
                    <TestDataReadyCondition name="数据就绪检查" />
                </Sequence>
                <Sequence name="测试执行">
                    <SimpleTestSuiteExecutionAction name="测试套件执行" />
                    <SimpleTestExecutionCompleteCondition name="执行完成检查" />
                </Sequence>
                <Sequence name="结果分析">
                    <SimpleTestResultAnalysisAction name="测试结果分析" />
                </Sequence>
                <Sequence name="报告生成">
                    <SimpleTestReportGenerationAction name="测试报告生成" />
                </Sequence>
            </Selector>
        </Sequence>
    </BehaviorTree>
    '''
    
    # 解析XML配置
    parser = XMLParser()
    
    # 确保自定义节点类型已注册
    register_custom_nodes()
    
    xml_tree = parser.parse_string(xml_config)
    xml_blackboard = xml_tree.blackboard
    
    # 初始化XML配置的数据
    xml_blackboard.set("test_data_ready", False)
    xml_blackboard.set("environment_ready", False)
    
    print("通过XML字符串配置的行为树:")
    print(xml_config.strip())
    print("\n开始执行XML配置的行为树...")
    xml_result = await xml_tree.tick()
    print(f"XML配置执行完成! 结果: {xml_result}")


if __name__ == "__main__":
    asyncio.run(main()) 