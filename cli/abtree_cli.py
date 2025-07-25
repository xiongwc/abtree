"""
ABTree CLI Tool

Provides command-line tools for loading, executing, and debugging behavior trees.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import click

# Add project root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from abtree import BehaviorTree
from abtree.parser.tree_builder import TreeBuilder
from abtree.parser.xml_parser import XMLParser
from abtree.utils.logger import get_abtree_logger
from abtree.validators import print_validation_result, validate_tree


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--log-file", help="Log file path")
def cli(verbose: bool, log_file: Optional[str]):
    """ABTree - Asynchronous Behavior Tree Framework Command Line Tool"""
    # Setup logging
    logger = get_abtree_logger()
    if verbose:
        logger.setLevel(logging.DEBUG)
    logger.info("ABTree CLI started")


@cli.command()
@click.argument("xml_file", type=click.Path(exists=True))
@click.option("--output", "-o", help="Output file path")
@click.option("--validate", is_flag=True, help="Validate behavior tree")
def load(xml_file: str, output: Optional[str], validate: bool):
    """Load behavior tree from XML file"""
    logger = get_abtree_logger()
    try:
        logger.info(f"Loading XML file: {xml_file}")

        # Parse XML
        parser = XMLParser()
        tree = parser.parse_file(xml_file)

        logger.info(f"Successfully loaded behavior tree: {tree.name}")

        # Validate behavior tree
        if validate:
            result = validate_tree(tree)
            print_validation_result(result, f"Behavior tree '{tree.name}' validation result")

            if not result.is_valid:
                sys.exit(1)

        # Display behavior tree information
        stats = tree.get_tree_stats()
        print(f"\nBehavior Tree Information:")
        print(f"  Name: {stats.get('name', 'Unknown')}")
        print(f"  Description: {stats.get('description', 'No description')}")
        print(f"  Total Nodes: {stats.get('total_nodes', 0)}")
        print(f"  Node Types: {stats.get('node_types', {})}")
        print(f"  Status Distribution: {stats.get('status_distribution', {})}")

        # Export to file
        if output:
            builder = TreeBuilder()
            xml_content = builder.export_to_xml(tree, output)
            logger.info(f"Behavior tree exported to: {output}")
            print(f"Behavior tree exported to: {output}")

    except Exception as e:
        error_msg = f"Loading failed: {e}"
        logger.error(error_msg)
        print(error_msg)
        sys.exit(1)


@cli.command()
@click.argument("xml_file", type=click.Path(exists=True))
@click.option("--ticks", "-t", default=1, help="Number of executions")
@click.option("--rate", "-r", default=60.0, help="Execution frequency (FPS)")
@click.option("--auto", is_flag=True, help="Auto execution mode")
def run(xml_file: str, ticks: int, rate: float, auto: bool):
    """Execute behavior tree"""

    async def run_tree():
        logger = get_abtree_logger()
        try:
            logger.info(f"Loading and executing behavior tree: {xml_file}")

            # Parse XML
            parser = XMLParser()
            tree = parser.parse_file(xml_file)

            logger.info(f"Behavior tree '{tree.name}' loaded successfully")

            # Set blackboard data examples
            tree.set_blackboard_data("enemy_visible", True)
            tree.set_blackboard_data("health", 100)
            tree.set_blackboard_data("condition1", True)

            if auto:
                # Auto execution mode
                logger.info(f"Starting auto execution mode, frequency: {rate} FPS")
                await tree.start(rate)

                try:
                    # Run for a period of time
                    await asyncio.sleep(5)
                finally:
                    await tree.stop()
                    logger.info("Auto execution mode stopped")
            else:
                # Manual execution mode
                logger.info(f"Executing {ticks} ticks")

                for i in range(ticks):
                    status = await tree.tick()
                    print(f"Tick {i+1}: {status.name}")

                    # Brief delay
                    await asyncio.sleep(1.0 / rate)

                logger.info("Execution completed")

        except Exception as e:
            error_msg = f"Execution failed: {e}"
            logger.error(error_msg)
            print(error_msg)
            sys.exit(1)

    try:
        asyncio.run(run_tree())
    except Exception as e:
        error_msg = f"Execution failed: {e}"
        print(error_msg)
        sys.exit(1)


@cli.command()
@click.option("--name", "-n", default="ExampleTree", help="Behavior tree name")
@click.option(
    "--type",
    "-t",
    type=click.Choice(["simple", "advanced"]),
    default="simple",
    help="Example type",
)
@click.option("--output", "-o", help="Output file path")
def create(name: str, type: str, output: Optional[str]):
    """Create example behavior tree"""
    logger = get_abtree_logger()
    try:
        logger.info(f"Creating {type} example behavior tree: {name}")

        builder = TreeBuilder()

        if type == "simple":
            tree = builder.create_simple_tree(name)
        else:
            tree = builder.create_advanced_tree(name)

        # Robustly log tree name
        tree_name = getattr(tree, 'name', str(tree))
        logger.info(f"Example behavior tree '{tree_name}' created successfully")

        # Display behavior tree information
        stats = tree.get_tree_stats() if hasattr(tree, 'get_tree_stats') else {}
        print(f"\nBehavior Tree Information:")
        print(f"  Name: {stats.get('name', getattr(tree, 'name', str(tree)))}")
        print(f"  Description: {stats.get('description', getattr(tree, 'description', 'No description'))}")
        print(f"  Total Nodes: {stats.get('total_nodes', 0)}")
        print(f"  Node Types: {stats.get('node_types', {})}")
        
        # Print the tree name for test verification
        print(f"Created tree: {tree_name}")

        # Export to file
        if output:
            xml_content = builder.export_to_xml(tree, output)
            logger.info(f"Behavior tree exported to: {output}")
            print(f"Behavior tree exported to: {output}")
        else:
            # Display XML content
            xml_content = builder.export_to_xml(tree)
            print(f"\nXML Content:")
            print(xml_content)

    except Exception as e:
        error_msg = f"Creation failed: {e}"
        logger.error(error_msg)
        print(error_msg)
        sys.exit(1)


@cli.command()
@click.argument("xml_file", type=click.Path(exists=True))
def validate(xml_file: str):
    """Validate XML file and behavior tree"""
    logger = get_abtree_logger()
    try:
        logger.info(f"Validating XML file: {xml_file}")

        # Read XML content
        with open(xml_file, "r", encoding="utf-8") as f:
            xml_content = f.read()

        # Validate XML structure
        from abtree.validators import validate_xml_structure

        xml_result = validate_xml_structure(xml_content)
        print_validation_result(xml_result, "XML structure validation")

        if not xml_result.is_valid:
            sys.exit(1)

        # Parse and validate behavior tree
        parser = XMLParser()
        tree = parser.parse_file(xml_file)

        tree_result = validate_tree(tree)
        print_validation_result(tree_result, f"Behavior tree '{tree.name}' validation")

        if not tree_result.is_valid:
            sys.exit(1)

        logger.info("Validation completed, all checks passed")

    except Exception as e:
        error_msg = f"Validation failed: {e}"
        logger.error(error_msg)
        print(error_msg)
        sys.exit(1)


@cli.command()
def list_nodes():
    """List all available node types"""
    logger = get_abtree_logger()
    try:
        from abtree.registry.node_registry import get_global_registry

        registry = get_global_registry()
        registered_nodes = registry.get_registered()

        if not registered_nodes:
            print("No registered node types")
            return

        print(f"\nAvailable node types ({len(registered_nodes)}):")
        for node_type in sorted(registered_nodes):
            metadata = registry.get_metadata(node_type)
            description = (
                metadata.get("description", "No description") if metadata else "No description"
            )
            print(f"  {node_type}: {description}")

    except Exception as e:
        error_msg = f"Failed to list node types: {e}"
        logger.error(error_msg)
        print(error_msg)
        sys.exit(1)


@cli.command()
@click.argument("xml_file", type=click.Path(exists=True))
def info(xml_file: str):
    """Display detailed behavior tree information"""
    logger = get_abtree_logger()
    try:
        logger.info(f"Analyzing behavior tree: {xml_file}")

        # Parse XML
        parser = XMLParser()
        tree = parser.parse_file(xml_file)

        # Get statistics
        stats = tree.get_tree_stats()

        print(f"\n=== Behavior Tree Detailed Information ===")
        print(f"Name: {stats.get('name', 'Unknown')}")
        print(f"Description: {stats.get('description', 'No description')}")
        print(f"Total Nodes: {stats.get('total_nodes', 0)}")
        
        # Calculate tree depth if not available
        tree_depth = stats.get('tree_depth', 0)
        if tree_depth == 0 and hasattr(tree, 'root') and tree.root:
            try:
                def calculate_depth(node, depth=0):
                    if not hasattr(node, 'children') or not node.children:
                        return depth
                    return max(calculate_depth(child, depth + 1) for child in node.children)
                tree_depth = calculate_depth(tree.root)
            except (AttributeError, TypeError):
                # Handle Mock objects or other non-iterable objects
                tree_depth = 0
        print(f"Tree Depth: {tree_depth}")

        print(f"\nNode Type Distribution:")
        node_types = stats.get("node_types", {})
        if isinstance(node_types, dict):
            for node_type, count in node_types.items():
                print(f"  {node_type}: {count}")
        elif isinstance(node_types, list):
            for node_type in node_types:
                print(f"  {node_type}: 1")
        else:
            print("  No node type information available")

        print(f"\nStatus Distribution:")
        status_distribution = stats.get("status_distribution", {})
        if isinstance(status_distribution, dict):
            for status, count in status_distribution.items():
                print(f"  {status}: {count}")
        else:
            print("  No status distribution information available")

        print(f"\nSystem Components:")
        print(f"  Blackboard System: {'✓' if stats.get('has_blackboard', False) else '✗'}")
        print(f"  Event System: {'✓' if stats.get('has_event_system', False) else '✗'}")
        print(f"  Tick Manager: {'✓' if stats.get('has_tick_manager', False) else '✗'}")

        # Display node tree structure
        print(f"\nNode Tree Structure:")
        _print_node_tree(tree.root, 0)

    except Exception as e:
        error_msg = f"Analysis failed: {e}"
        logger.error(error_msg)
        print(error_msg)
        sys.exit(1)


def _print_node_tree(node, depth: int):
    """Print node tree structure"""
    indent = "  " * depth
    try:
        node_name = getattr(node, 'name', 'Unknown')
        node_status = getattr(node, 'status', None)
        status_name = getattr(node_status, 'name', 'UNKNOWN') if node_status else 'UNKNOWN'
        node_class = getattr(node, '__class__', type(node))
        class_name = getattr(node_class, '__name__', 'Unknown')
        
        print(f"{indent}{class_name}: {node_name} ({status_name})")

        # Try to iterate over children
        children = getattr(node, 'children', [])
        if hasattr(children, '__iter__') and not isinstance(children, str):
            for child in children:
                _print_node_tree(child, depth + 1)
    except Exception:
        # Handle any errors gracefully
        print(f"{indent}Unknown Node")


def main():
    """Main function"""
    cli()


if __name__ == "__main__":
    main()
