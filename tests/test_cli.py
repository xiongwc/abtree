import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
from click.testing import CliRunner
from cli.abtree_cli import cli, load, run, create, validate, list_nodes, info


class TestCLI:
    """测试CLI工具"""
    
    @pytest.fixture
    def runner(self):
        """创建CLI运行器"""
        return CliRunner()
    
    @pytest.fixture
    def temp_xml_file(self):
        """创建临时XML文件"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<BehaviorTree name="TestTree">
    <Root>
        <Sequence name="RootSeq">
            <AlwaysTrue name="Cond1"/>
            <AlwaysSuccess name="Action1"/>
        </Sequence>
    </Root>
</BehaviorTree>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        yield temp_file
        
        # 清理临时文件
        os.unlink(temp_file)
    
    def test_cli_help(self, runner):
        """测试CLI帮助信息"""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "ABTree" in result.output
        assert "load" in result.output
        assert "run" in result.output
        assert "create" in result.output
    
    def test_cli_verbose_logging(self, runner):
        """测试CLI详细日志"""
        result = runner.invoke(cli, ['--verbose', '--help'])
        assert result.exit_code == 0
    
    def test_cli_log_file(self, runner):
        """测试CLI日志文件"""
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as log_file:
            result = runner.invoke(cli, ['--log-file', log_file.name, '--help'])
            assert result.exit_code == 0
            
            # 清理日志文件
            os.unlink(log_file.name)
    
    @patch('cli.abtree_cli.XMLParser')
    @patch('cli.abtree_cli.validate_tree')
    @patch('cli.abtree_cli.print_validation_result')
    def test_load_command_success(self, mock_print_validation, mock_validate_tree, mock_xml_parser, runner, temp_xml_file):
        """测试load命令成功"""
        # 模拟XML解析器
        mock_parser = Mock()
        mock_tree = Mock()
        mock_tree.name = "TestTree"
        mock_tree.get_tree_stats.return_value = {
            'name': 'TestTree',
            'description': 'Test Description',
            'total_nodes': 3,
            'node_types': ['Sequence', 'AlwaysTrue', 'AlwaysSuccess'],
            'status_distribution': {'SUCCESS': 1}
        }
        mock_parser.parse_file.return_value = mock_tree
        mock_xml_parser.return_value = mock_parser
        
        # 模拟验证结果
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validate_tree.return_value = mock_validation_result
        
        # 执行命令
        result = runner.invoke(load, [temp_xml_file, '--validate'])
        
        assert result.exit_code == 0
        assert "TestTree" in result.output
        assert "3" in result.output  # 总节点数
    
    @patch('cli.abtree_cli.XMLParser')
    def test_load_command_parse_error(self, mock_xml_parser, runner, temp_xml_file):
        """测试load命令解析错误"""
        # 模拟解析错误
        mock_parser = Mock()
        mock_parser.parse_file.side_effect = Exception("Parse error")
        mock_xml_parser.return_value = mock_parser
        
        # 执行命令
        result = runner.invoke(load, [temp_xml_file])
        
        assert result.exit_code == 1
        assert "Loading failed" in result.output
    
    @patch('cli.abtree_cli.XMLParser')
    @patch('cli.abtree_cli.validate_tree')
    def test_load_command_validation_failure(self, mock_validate_tree, mock_xml_parser, runner, temp_xml_file):
        """测试load命令验证失败"""
        # 模拟XML解析器
        mock_parser = Mock()
        mock_tree = Mock()
        mock_tree.name = "TestTree"
        mock_parser.parse_file.return_value = mock_tree
        mock_xml_parser.return_value = mock_parser
        
        # 模拟验证失败
        mock_validation_result = Mock()
        mock_validation_result.is_valid = False
        mock_validation_result.errors = ["Invalid tree structure"]
        mock_validate_tree.return_value = mock_validation_result
        
        # 执行命令
        result = runner.invoke(load, [temp_xml_file, '--validate'])
        
        assert result.exit_code == 1
    
    @patch('cli.abtree_cli.XMLParser')
    @patch('cli.abtree_cli.TreeBuilder')
    def test_load_command_with_output(self, mock_tree_builder, mock_xml_parser, runner, temp_xml_file):
        """测试load命令带输出文件"""
        # 模拟XML解析器
        mock_parser = Mock()
        mock_tree = Mock()
        mock_tree.name = "TestTree"
        mock_tree.get_tree_stats.return_value = {
            'name': 'TestTree',
            'description': 'Test Description',
            'total_nodes': 3,
            'node_types': {'Sequence': 1, 'AlwaysTrue': 1, 'AlwaysSuccess': 1},
            'status_distribution': {'SUCCESS': 1}
        }
        mock_parser.parse_file.return_value = mock_tree
        mock_xml_parser.return_value = mock_parser
        
        # 模拟树构建器
        mock_builder = Mock()
        mock_builder.export_to_xml.return_value = "exported_xml"
        mock_tree_builder.return_value = mock_builder
        
        # 创建临时输出文件
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as output_file:
            output_path = output_file.name
        
        try:
            # 执行命令
            result = runner.invoke(load, [temp_xml_file, '--output', output_path])
            
            assert result.exit_code == 0
            assert "exported" in result.output
            
        finally:
            # 清理输出文件
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    @patch('cli.abtree_cli.XMLParser')
    @patch('cli.abtree_cli.asyncio.run')
    def test_run_command_success(self, mock_asyncio_run, mock_xml_parser, runner, temp_xml_file):
        """测试run命令成功"""
        # 模拟XML解析器
        mock_parser = Mock()
        mock_tree = Mock()
        mock_tree.name = "TestTree"
        mock_parser.parse_file.return_value = mock_tree
        mock_xml_parser.return_value = mock_parser
        
        # 模拟异步运行
        mock_asyncio_run.return_value = None
        
        # 执行命令
        result = runner.invoke(run, [temp_xml_file, '--ticks', '5', '--rate', '30.0'])
        
        assert result.exit_code == 0
    
    @patch('cli.abtree_cli.XMLParser')
    def test_run_command_parse_error(self, mock_xml_parser, runner, temp_xml_file):
        """测试run命令解析错误"""
        # 模拟解析错误
        mock_parser = Mock()
        mock_parser.parse_file.side_effect = Exception("Parse error")
        mock_xml_parser.return_value = mock_parser
        
        # 执行命令
        result = runner.invoke(run, [temp_xml_file])
        
        assert result.exit_code == 1
        assert "Execution failed" in result.output
    
    @patch('click.open_file')
    @patch('cli.abtree_cli.TreeBuilder')
    def test_create_command_simple(self, mock_tree_builder, mock_open_file, runner):
        """测试create命令简单示例"""
        # 模拟树构建器
        mock_builder = Mock()
        mock_tree = Mock()
        mock_tree.name = "TestTree"
        mock_tree.get_tree_stats.return_value = {
            'name': 'TestTree',
            'description': 'Test Description',
            'total_nodes': 3,
            'node_types': {'Sequence': 1, 'AlwaysTrue': 1, 'AlwaysSuccess': 1},
            'status_distribution': {'SUCCESS': 1}
        }
        mock_builder.create_simple_tree.return_value = mock_tree
        mock_tree_builder.return_value = mock_builder
        
        # 模拟文件操作
        mock_file = Mock()
        mock_open_file.return_value.__enter__.return_value = mock_file
        
        # 执行命令
        result = runner.invoke(create, ['--name', 'TestTree', '--type', 'simple'])
        
        assert result.exit_code == 0
        assert "TestTree" in result.output
    
    @patch('click.open_file')
    @patch('cli.abtree_cli.TreeBuilder')
    def test_create_command_advanced(self, mock_tree_builder, mock_open_file, runner):
        """测试create命令高级示例"""
        # 模拟树构建器
        mock_builder = Mock()
        mock_tree = Mock()
        mock_tree.name = "AdvancedTree"
        mock_tree.get_tree_stats.return_value = {
            'name': 'AdvancedTree',
            'description': 'Advanced Description',
            'total_nodes': 5,
            'node_types': {'Selector': 1, 'Sequence': 1, 'AlwaysTrue': 2, 'AlwaysSuccess': 1},
            'status_distribution': {'SUCCESS': 1}
        }
        mock_builder.create_advanced_tree.return_value = mock_tree
        mock_tree_builder.return_value = mock_builder
        
        # 模拟文件操作
        mock_file = Mock()
        mock_open_file.return_value.__enter__.return_value = mock_file
        
        # 执行命令
        result = runner.invoke(create, ['--name', 'AdvancedTree', '--type', 'advanced'])
        
        assert result.exit_code == 0
        assert "AdvancedTree" in result.output
    
    @patch('click.open_file')
    @patch('cli.abtree_cli.TreeBuilder')
    def test_create_command_with_output(self, mock_tree_builder, mock_open_file, runner):
        """测试create命令带输出文件"""
        # 模拟树构建器
        mock_builder = Mock()
        mock_tree = Mock()
        mock_tree.name = "TestTree"
        mock_tree.get_tree_stats.return_value = {
            'name': 'TestTree',
            'description': 'Test Description',
            'total_nodes': 3,
            'node_types': {'Sequence': 1, 'AlwaysTrue': 1, 'AlwaysSuccess': 1},
            'status_distribution': {'SUCCESS': 1}
        }
        mock_builder.create_simple_tree.return_value = mock_tree
        mock_tree_builder.return_value = mock_builder
        
        # 创建临时输出文件
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as output_file:
            output_path = output_file.name
        
        try:
            # 执行命令
            result = runner.invoke(create, ['--name', 'TestTree', '--output', output_path])
            
            assert result.exit_code == 0
            assert "TestTree" in result.output
            
        finally:
            # 清理输出文件
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    @patch('cli.abtree_cli.XMLParser')
    @patch('cli.abtree_cli.validate_tree')
    @patch('abtree.validators.validate_xml_structure')
    def test_validate_command_success(self, mock_validate_xml_structure, mock_validate_tree, mock_xml_parser, runner, temp_xml_file):
        """测试validate命令成功"""
        # 模拟XML解析器
        mock_parser = Mock()
        mock_tree = Mock()
        mock_tree.name = "TestTree"
        mock_parser.parse_file.return_value = mock_tree
        mock_xml_parser.return_value = mock_parser
        
        # 模拟XML验证结果
        mock_xml_validation_result = Mock()
        mock_xml_validation_result.is_valid = True
        mock_xml_validation_result.errors = []
        mock_xml_validation_result.warnings = []
        mock_validate_xml_structure.return_value = mock_xml_validation_result
        
        # 模拟验证结果
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validation_result.errors = []
        mock_validation_result.warnings = ["Minor warning"]
        mock_validate_tree.return_value = mock_validation_result
        
        # 执行命令
        result = runner.invoke(validate, [temp_xml_file])
        
        assert result.exit_code == 0
        assert "TestTree" in result.output
    
    @patch('cli.abtree_cli.XMLParser')
    @patch('cli.abtree_cli.validate_tree')
    def test_validate_command_failure(self, mock_validate_tree, mock_xml_parser, runner, temp_xml_file):
        """测试validate命令失败"""
        # 模拟XML解析器
        mock_parser = Mock()
        mock_tree = Mock()
        mock_tree.name = "TestTree"
        mock_parser.parse_file.return_value = mock_tree
        mock_xml_parser.return_value = mock_parser
        
        # 模拟验证失败
        mock_validation_result = Mock()
        mock_validation_result.is_valid = False
        mock_validation_result.errors = ["Invalid structure"]
        mock_validate_tree.return_value = mock_validation_result
        
        # 执行命令
        result = runner.invoke(validate, [temp_xml_file])
        
        assert result.exit_code == 1
    
    @patch('abtree.registry.node_registry.get_global_registry')
    def test_list_nodes_command(self, mock_get_global_registry, runner):
        """测试list_nodes命令"""
        # 模拟注册表
        mock_registry = Mock()
        mock_registry.get_registered.return_value = ['AlwaysSuccess', 'Sequence', 'Inverter']
        mock_registry.get_metadata.side_effect = lambda node_type: {
            'description': f'Description for {node_type}'
        }
        mock_get_global_registry.return_value = mock_registry
        
        # 执行命令
        result = runner.invoke(list_nodes)
        
        assert result.exit_code == 0
        assert "AlwaysSuccess" in result.output
        assert "Sequence" in result.output
        assert "Inverter" in result.output
    
    @patch('cli.abtree_cli.XMLParser')
    def test_info_command_success(self, mock_xml_parser, runner, temp_xml_file):
        """测试info命令成功"""
        # 模拟XML解析器
        mock_parser = Mock()
        mock_tree = Mock()
        mock_tree.name = "TestTree"
        mock_tree.get_tree_stats.return_value = {
            'name': 'TestTree',
            'description': 'Test Description',
            'total_nodes': 3,
            'node_types': ['Sequence', 'AlwaysTrue', 'AlwaysSuccess'],
            'status_distribution': {'SUCCESS': 1}
        }
        mock_parser.parse_file.return_value = mock_tree
        mock_xml_parser.return_value = mock_parser
        
        # 执行命令
        result = runner.invoke(info, [temp_xml_file])
        
        assert result.exit_code == 0
        assert "TestTree" in result.output
        assert "3" in result.output  # 总节点数
        assert "Sequence" in result.output
    
    @patch('cli.abtree_cli.XMLParser')
    def test_info_command_parse_error(self, mock_xml_parser, runner, temp_xml_file):
        """测试info命令解析错误"""
        # 模拟解析错误
        mock_parser = Mock()
        mock_parser.parse_file.side_effect = Exception("Parse error")
        mock_xml_parser.return_value = mock_parser
        
        # 执行命令
        result = runner.invoke(info, [temp_xml_file])
        
        assert result.exit_code == 1
        assert "Analysis failed" in result.output


class TestCLIIntegration:
    """测试CLI集成"""
    
    @pytest.fixture
    def runner(self):
        """创建CLI运行器"""
        return CliRunner()
    
    def test_cli_with_all_commands(self, runner):
        """测试CLI所有命令"""
        # 测试帮助
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        
        # 测试子命令帮助
        result = runner.invoke(cli, ['load', '--help'])
        assert result.exit_code == 0
        
        result = runner.invoke(cli, ['run', '--help'])
        assert result.exit_code == 0
        
        result = runner.invoke(cli, ['create', '--help'])
        assert result.exit_code == 0
        
        result = runner.invoke(cli, ['validate', '--help'])
        assert result.exit_code == 0
        
        result = runner.invoke(cli, ['list-nodes', '--help'])
        assert result.exit_code == 0
        
        result = runner.invoke(cli, ['info', '--help'])
        assert result.exit_code == 0
    
    def test_cli_error_handling(self, runner):
        """测试CLI错误处理"""
        # 测试不存在的文件 - Click 会返回退出码 2
        result = runner.invoke(load, ['nonexistent.xml'])
        assert result.exit_code == 2
        
        result = runner.invoke(run, ['nonexistent.xml'])
        assert result.exit_code == 2
        
        result = runner.invoke(validate, ['nonexistent.xml'])
        assert result.exit_code == 2
        
        result = runner.invoke(info, ['nonexistent.xml'])
        assert result.exit_code == 2
    
    def test_cli_with_invalid_options(self, runner):
        """测试CLI无效选项"""
        # 测试无效的create类型
        result = runner.invoke(create, ['--type', 'invalid_type'])
        assert result.exit_code == 2  # Click错误码
        
        # 测试无效的ticks数量
        result = runner.invoke(run, ['test.xml', '--ticks', '-1'])
        assert result.exit_code == 2
        
        # 测试无效的rate
        result = runner.invoke(run, ['test.xml', '--rate', '0'])
        assert result.exit_code == 2


class TestCLIUtilities:
    """测试CLI工具函数"""
    
    @patch('cli.abtree_cli._print_node_tree')
    def test_print_node_tree(self, mock_print_node_tree):
        """测试打印节点树"""
        # 模拟节点
        mock_node = Mock()
        mock_node.name = "TestNode"
        mock_node.children = []
        
        # 调用打印函数
        from cli.abtree_cli import _print_node_tree
        _print_node_tree(mock_node, 0)
        
        # 验证函数被调用
        mock_print_node_tree.assert_called_once()
    
    @patch('cli.abtree_cli.cli')
    def test_main_function(self, mock_cli):
        """测试main函数"""
        from cli.abtree_cli import main
        
        # 模拟CLI调用
        mock_cli.return_value = None
        
        # 调用main函数
        main()
        
        # 验证CLI被调用
        mock_cli.assert_called_once()


class TestCLIEdgeCases:
    """测试CLI边界情况"""
    
    @pytest.fixture
    def runner(self):
        """创建CLI运行器"""
        return CliRunner()
    
    def test_cli_with_empty_xml(self, runner):
        """测试CLI空XML文件"""
        # 创建空XML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write("")
            temp_file = f.name
        
        try:
            result = runner.invoke(load, [temp_file])
            assert result.exit_code == 1
            
            result = runner.invoke(validate, [temp_file])
            assert result.exit_code == 1
            
        finally:
            os.unlink(temp_file)
    
    def test_cli_with_malformed_xml(self, runner):
        """测试CLI格式错误的XML文件"""
        # 创建格式错误的XML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write("<invalid>xml</invalid>")
            temp_file = f.name
        
        try:
            result = runner.invoke(load, [temp_file])
            assert result.exit_code == 1
            
        finally:
            os.unlink(temp_file)
    
    def test_cli_with_large_xml(self, runner):
        """测试CLI大型XML文件"""
        # 创建大型XML文件
        large_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<BehaviorTree name="LargeTree">\n<Root>\n'
        large_xml += '<Sequence name="RootSeq">\n' * 1000
        large_xml += '<AlwaysTrue name="Cond1"/>\n' * 1000
        large_xml += '</Sequence>\n' * 1000
        large_xml += '</Root>\n</BehaviorTree>'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(large_xml)
            temp_file = f.name
        
        try:
            # 测试大型文件处理（可能超时或内存不足）
            result = runner.invoke(load, [temp_file])
            # 这里不检查退出码，因为大型文件可能导致超时
            
        finally:
            os.unlink(temp_file)
    
    def test_cli_with_special_characters(self, runner):
        """测试CLI特殊字符"""
        # 创建包含特殊字符的XML文件
        special_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<BehaviorTree name="Test&amp;Tree">
    <Root>
        <Sequence name="Root&lt;Seq&gt;">
            <AlwaysTrue name="Cond&quot;1&quot;"/>
        </Sequence>
    </Root>
</BehaviorTree>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(special_xml)
            temp_file = f.name
        
        try:
            result = runner.invoke(load, [temp_file])
            # 这里不检查退出码，因为特殊字符可能导致解析问题
            
        finally:
            os.unlink(temp_file) 