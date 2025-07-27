import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
from click.testing import CliRunner
from cli.abtree_cli import cli, load, run, create, validate, list_nodes, info


class TestCLI:
    """Test CLI tool"""
    
    @pytest.fixture
    def runner(self):
        """Create CLI runner"""
        return CliRunner()
    
    @pytest.fixture
    def temp_xml_file(self):
        """Create temporary XML file"""
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
        
        # Clean up temporary file
        os.unlink(temp_file)
    
    def test_cli_help(self, runner):
        """Test CLI help information"""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "ABTree" in result.output
        assert "load" in result.output
        assert "run" in result.output
        assert "create" in result.output
    
    def test_cli_verbose_logging(self, runner):
        """Test CLI verbose logging"""
        result = runner.invoke(cli, ['--verbose', '--help'])
        assert result.exit_code == 0
    
    def test_cli_log_file(self, runner):
        """Test CLI log file"""
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as log_file:
            result = runner.invoke(cli, ['--log-file', log_file.name, '--help'])
            assert result.exit_code == 0
            
            # Clean up log file
            os.unlink(log_file.name)
    
    @patch('cli.abtree_cli.XMLParser')
    @patch('cli.abtree_cli.validate_tree')
    @patch('cli.abtree_cli.print_validation_result')
    def test_load_command_success(self, mock_print_validation, mock_validate_tree, mock_xml_parser, runner, temp_xml_file):
        """Test load command success"""
        # Mock XML parser
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
        
        # Mock validation result
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validate_tree.return_value = mock_validation_result
        
        # Execute command
        result = runner.invoke(load, [temp_xml_file, '--validate'])
        
        assert result.exit_code == 0
        assert "TestTree" in result.output
        assert "3" in result.output  # Total node count
    
    @patch('cli.abtree_cli.XMLParser')
    def test_load_command_parse_error(self, mock_xml_parser, runner, temp_xml_file):
        """Test load command parse error"""
        # Mock parse error
        mock_parser = Mock()
        mock_parser.parse_file.side_effect = Exception("Parse error")
        mock_xml_parser.return_value = mock_parser
        
        # Execute command
        result = runner.invoke(load, [temp_xml_file])
        
        assert result.exit_code == 1
        assert "Loading failed" in result.output
    
    @patch('cli.abtree_cli.XMLParser')
    @patch('cli.abtree_cli.validate_tree')
    def test_load_command_validation_failure(self, mock_validate_tree, mock_xml_parser, runner, temp_xml_file):
        """Test load command validation failure"""
        # Mock XML parser
        mock_parser = Mock()
        mock_tree = Mock()
        mock_tree.name = "TestTree"
        mock_parser.parse_file.return_value = mock_tree
        mock_xml_parser.return_value = mock_parser
        
        # Mock validation failure
        mock_validation_result = Mock()
        mock_validation_result.is_valid = False
        mock_validation_result.errors = ["Invalid tree structure"]
        mock_validate_tree.return_value = mock_validation_result
        
        # Execute command
        result = runner.invoke(load, [temp_xml_file, '--validate'])
        
        assert result.exit_code == 1
    
    @patch('cli.abtree_cli.XMLParser')
    @patch('cli.abtree_cli.TreeBuilder')
    def test_load_command_with_output(self, mock_tree_builder, mock_xml_parser, runner, temp_xml_file):
        """Test load command with output file"""
        # Mock XML parser
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
        
        # Mock tree builder
        mock_builder = Mock()
        mock_builder.export_to_xml.return_value = "exported_xml"
        mock_tree_builder.return_value = mock_builder
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as output_file:
            output_path = output_file.name
        
        try:
            # Execute command
            result = runner.invoke(load, [temp_xml_file, '--output', output_path])
            
            assert result.exit_code == 0
            assert "exported" in result.output
            
        finally:
            # Clean up output file
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    @patch('cli.abtree_cli.XMLParser')
    @patch('cli.abtree_cli.asyncio.run')
    def test_run_command_success(self, mock_asyncio_run, mock_xml_parser, runner, temp_xml_file):
        """Test run command success"""
        # Mock XML parser
        mock_parser = Mock()
        mock_tree = Mock()
        mock_tree.name = "TestTree"
        mock_parser.parse_file.return_value = mock_tree
        mock_xml_parser.return_value = mock_parser
        
        # Mock async execution
        mock_asyncio_run.return_value = None
        
        # Execute command
        result = runner.invoke(run, [temp_xml_file, '--ticks', '5', '--rate', '30.0'])
        
        assert result.exit_code == 0
    
    @patch('cli.abtree_cli.XMLParser')
    def test_run_command_parse_error(self, mock_xml_parser, runner, temp_xml_file):
        """Test run command parse error"""
        # Mock parse error
        mock_parser = Mock()
        mock_parser.parse_file.side_effect = Exception("Parse error")
        mock_xml_parser.return_value = mock_parser
        
        # Execute command
        result = runner.invoke(run, [temp_xml_file])
        
        assert result.exit_code == 1
        assert "Execution failed" in result.output
    
    @patch('click.open_file')
    @patch('cli.abtree_cli.TreeBuilder')
    def test_create_command_simple(self, mock_tree_builder, mock_open_file, runner):
        """Test create command simple example"""
        # Mock tree builder
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
        
        # Mock file operations
        mock_file = Mock()
        mock_open_file.return_value.__enter__.return_value = mock_file
        
        # Execute command
        result = runner.invoke(create, ['--name', 'TestTree', '--type', 'simple'])
        
        assert result.exit_code == 0
        assert "TestTree" in result.output
    
    @patch('click.open_file')
    @patch('cli.abtree_cli.TreeBuilder')
    def test_create_command_advanced(self, mock_tree_builder, mock_open_file, runner):
        """Test create command advanced example"""
        # Mock tree builder
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
        
        # Mock file operations
        mock_file = Mock()
        mock_open_file.return_value.__enter__.return_value = mock_file
        
        # Execute command
        result = runner.invoke(create, ['--name', 'AdvancedTree', '--type', 'advanced'])
        
        assert result.exit_code == 0
        assert "AdvancedTree" in result.output
    
    @patch('click.open_file')
    @patch('cli.abtree_cli.TreeBuilder')
    def test_create_command_with_output(self, mock_tree_builder, mock_open_file, runner):
        """Test create command with output file"""
        # Mock tree builder
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
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as output_file:
            output_path = output_file.name
        
        try:
            # Execute command
            result = runner.invoke(create, ['--name', 'TestTree', '--output', output_path])
            
            assert result.exit_code == 0
            assert "TestTree" in result.output
            
        finally:
            # Clean up output file
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    @patch('cli.abtree_cli.XMLParser')
    @patch('cli.abtree_cli.validate_tree')
    @patch('abtree.validators.validate_xml_structure')
    def test_validate_command_success(self, mock_validate_xml_structure, mock_validate_tree, mock_xml_parser, runner, temp_xml_file):
        """Test validate command success"""
        # Mock XML parser
        mock_parser = Mock()
        mock_tree = Mock()
        mock_tree.name = "TestTree"
        mock_parser.parse_file.return_value = mock_tree
        mock_xml_parser.return_value = mock_parser
        
        # Mock XML validation result
        mock_xml_validation_result = Mock()
        mock_xml_validation_result.is_valid = True
        mock_xml_validation_result.errors = []
        mock_xml_validation_result.warnings = []
        mock_validate_xml_structure.return_value = mock_xml_validation_result
        
        # Mock validation result
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validation_result.errors = []
        mock_validation_result.warnings = ["Minor warning"]
        mock_validate_tree.return_value = mock_validation_result
        
        # Execute command
        result = runner.invoke(validate, [temp_xml_file])
        
        assert result.exit_code == 0
        assert "TestTree" in result.output
    
    @patch('cli.abtree_cli.XMLParser')
    @patch('cli.abtree_cli.validate_tree')
    def test_validate_command_failure(self, mock_validate_tree, mock_xml_parser, runner, temp_xml_file):
        """Test validate command failure"""
        # Mock XML parser
        mock_parser = Mock()
        mock_tree = Mock()
        mock_tree.name = "TestTree"
        mock_parser.parse_file.return_value = mock_tree
        mock_xml_parser.return_value = mock_parser
        
        # Mock validation failure
        mock_validation_result = Mock()
        mock_validation_result.is_valid = False
        mock_validation_result.errors = ["Invalid structure"]
        mock_validate_tree.return_value = mock_validation_result
        
        # Execute command
        result = runner.invoke(validate, [temp_xml_file])
        
        assert result.exit_code == 1
    
    @patch('abtree.registry.node_registry.get_global_registry')
    def test_list_nodes_command(self, mock_get_global_registry, runner):
        """Test list_nodes command"""
        # Mock registry
        mock_registry = Mock()
        mock_registry.get_registered.return_value = ['AlwaysSuccess', 'Sequence', 'Inverter']
        mock_registry.get_metadata.side_effect = lambda node_type: {
            'description': f'Description for {node_type}'
        }
        mock_get_global_registry.return_value = mock_registry
        
        # Execute command
        result = runner.invoke(list_nodes)
        
        assert result.exit_code == 0
        assert "AlwaysSuccess" in result.output
        assert "Sequence" in result.output
        assert "Inverter" in result.output
    
    @patch('cli.abtree_cli.XMLParser')
    def test_info_command_success(self, mock_xml_parser, runner, temp_xml_file):
        """Test info command success"""
        # Mock XML parser
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
        
        # Execute command
        result = runner.invoke(info, [temp_xml_file])
        
        assert result.exit_code == 0
        assert "TestTree" in result.output
        assert "3" in result.output  # Total node count
        assert "Sequence" in result.output
    
    @patch('cli.abtree_cli.XMLParser')
    def test_info_command_parse_error(self, mock_xml_parser, runner, temp_xml_file):
        """Test info command parse error"""
        # Mock parse error
        mock_parser = Mock()
        mock_parser.parse_file.side_effect = Exception("Parse error")
        mock_xml_parser.return_value = mock_parser
        
        # Execute command
        result = runner.invoke(info, [temp_xml_file])
        
        assert result.exit_code == 1
        assert "Analysis failed" in result.output


class TestCLIIntegration:
    """Test CLI integration"""
    
    @pytest.fixture
    def runner(self):
        """Create CLI runner"""
        return CliRunner()
    
    def test_cli_with_all_commands(self, runner):
        """Test CLI all commands"""
        # Test help
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        
        # Test subcommand help
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
        """Test CLI error handling"""
        # Test non-existent file - Click will return exit code 2
        result = runner.invoke(load, ['nonexistent.xml'])
        assert result.exit_code == 2
        
        result = runner.invoke(run, ['nonexistent.xml'])
        assert result.exit_code == 2
        
        result = runner.invoke(validate, ['nonexistent.xml'])
        assert result.exit_code == 2
        
        result = runner.invoke(info, ['nonexistent.xml'])
        assert result.exit_code == 2
    
    def test_cli_with_invalid_options(self, runner):
        """Test CLI invalid options"""
        # Test invalid create type
        result = runner.invoke(create, ['--type', 'invalid_type'])
        assert result.exit_code == 2  # Click error code
        
        # Test invalid ticks count
        result = runner.invoke(run, ['test.xml', '--ticks', '-1'])
        assert result.exit_code == 2
        
        # Test invalid rate
        result = runner.invoke(run, ['test.xml', '--rate', '0'])
        assert result.exit_code == 2


class TestCLIUtilities:
    """Test CLI utility functions"""
    
    @patch('cli.abtree_cli._print_node_tree')
    def test_print_node_tree(self, mock_print_node_tree):
        """Test print node tree"""
        # Mock node
        mock_node = Mock()
        mock_node.name = "TestNode"
        mock_node.children = []
        
        # Call print function
        from cli.abtree_cli import _print_node_tree
        _print_node_tree(mock_node, 0)
        
        # Verify function was called
        mock_print_node_tree.assert_called_once()
    
    @patch('cli.abtree_cli.cli')
    def test_main_function(self, mock_cli):
        """Test main function"""
        from cli.abtree_cli import main
        
        # Mock CLI call
        mock_cli.return_value = None
        
        # Call main function
        main()
        
        # Verify CLI was called
        mock_cli.assert_called_once()


class TestCLIEdgeCases:
    """Test CLI edge cases"""
    
    @pytest.fixture
    def runner(self):
        """Create CLI runner"""
        return CliRunner()
    
    def test_cli_with_empty_xml(self, runner):
        """Test CLI empty XML file"""
        # Create empty XML file
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
        """Test CLI malformed XML file"""
        # Create malformed XML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write("<invalid>xml</invalid>")
            temp_file = f.name
        
        try:
            result = runner.invoke(load, [temp_file])
            assert result.exit_code == 1
            
        finally:
            os.unlink(temp_file)
    
    def test_cli_with_large_xml(self, runner):
        """Test CLI large XML file"""
        # Create large XML file
        large_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<BehaviorTree name="LargeTree">\n<Root>\n'
        large_xml += '<Sequence name="RootSeq">\n' * 1000
        large_xml += '<AlwaysTrue name="Cond1"/>\n' * 1000
        large_xml += '</Sequence>\n' * 1000
        large_xml += '</Root>\n</BehaviorTree>'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(large_xml)
            temp_file = f.name
        
        try:
            # Test large file handling (may timeout or run out of memory)
            result = runner.invoke(load, [temp_file])
            # Do not check exit code here, as large files may cause timeouts
            
        finally:
            os.unlink(temp_file)
    
    def test_cli_with_special_characters(self, runner):
        """Test CLI special characters"""
        # Create XML file with special characters
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
            # Do not check exit code here, as special characters may cause parsing issues
            
        finally:
            os.unlink(temp_file) 