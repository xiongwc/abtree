"""
ABTree CLI Tool

Provides command-line tools for loading, executing, and debugging behavior trees.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click

# Add project root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from abtree import BehaviorTree
from abtree.parser.tree_builder import TreeBuilder
from abtree.parser.xml_parser import XMLParser
from abtree.utils.logger import log_error, log_info, setup_logger
from abtree.utils.validators import print_validation_result, validate_tree


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--log-file", help="Log file path")
def cli(verbose: bool, log_file: Optional[str]):
    """ABTree - Asynchronous Behavior Tree Framework Command Line Tool"""
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logger("abtree", log_level=log_level, log_file=log_file)
    log_info("ABTree CLI started")


@cli.command()
@click.argument("xml_file", type=click.Path(exists=True))
@click.option("--output", "-o", help="Output file path")
@click.option("--validate", is_flag=True, help="Validate behavior tree")
def load(xml_file: str, output: Optional[str], validate: bool):
    """Load behavior tree from XML file"""
    try:
        log_info(f"Loading XML file: {xml_file}")

        # Parse XML
        parser = XMLParser()
        tree = parser.parse_file(xml_file)

        log_info(f"Successfully loaded behavior tree: {tree.name}")

        # Validate behavior tree
        if validate:
            result = validate_tree(tree)
            print_validation_result(result, f"Behavior tree '{tree.name}' validation result")

            if not result.is_valid:
                sys.exit(1)

        # Display behavior tree information
        stats = tree.get_tree_stats()
        print(f"\nBehavior Tree Information:")
        print(f"  Name: {stats['name']}")
        print(f"  Description: {stats['description']}")
        print(f"  Total Nodes: {stats['total_nodes']}")
        print(f"  Node Types: {stats['node_types']}")
        print(f"  Status Distribution: {stats['status_distribution']}")

        # Export to file
        if output:
            builder = TreeBuilder()
            xml_content = builder.export_to_xml(tree, output)
            log_info(f"Behavior tree exported to: {output}")

    except Exception as e:
        log_error(f"Loading failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument("xml_file", type=click.Path(exists=True))
@click.option("--ticks", "-t", default=1, help="Number of executions")
@click.option("--rate", "-r", default=60.0, help="Execution frequency (FPS)")
@click.option("--auto", is_flag=True, help="Auto execution mode")
def run(xml_file: str, ticks: int, rate: float, auto: bool):
    """Execute behavior tree"""

    async def run_tree():
        try:
            log_info(f"Loading and executing behavior tree: {xml_file}")

            # Parse XML
            parser = XMLParser()
            tree = parser.parse_file(xml_file)

            log_info(f"Behavior tree '{tree.name}' loaded successfully")

            # Set blackboard data examples
            tree.set_blackboard_data("enemy_visible", True)
            tree.set_blackboard_data("health", 100)
            tree.set_blackboard_data("condition1", True)

            if auto:
                # Auto execution mode
                log_info(f"Starting auto execution mode, frequency: {rate} FPS")
                await tree.start(rate)

                try:
                    # Run for a period of time
                    await asyncio.sleep(5)
                finally:
                    await tree.stop()
                    log_info("Auto execution mode stopped")
            else:
                # Manual execution mode
                log_info(f"Executing {ticks} ticks")

                for i in range(ticks):
                    status = await tree.tick()
                    print(f"Tick {i+1}: {status.name}")

                    # Brief delay
                    await asyncio.sleep(1.0 / rate)

                log_info("Execution completed")

        except Exception as e:
            log_error(f"Execution failed: {e}")
            sys.exit(1)

    asyncio.run(run_tree())


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
    try:
        log_info(f"Creating {type} example behavior tree: {name}")

        builder = TreeBuilder()

        if type == "simple":
            tree = builder.create_simple_tree(name)
        else:
            tree = builder.create_advanced_tree(name)

        log_info(f"Example behavior tree '{tree.name}' created successfully")

        # Display behavior tree information
        stats = tree.get_tree_stats()
        print(f"\nBehavior Tree Information:")
        print(f"  Name: {stats['name']}")
        print(f"  Description: {stats['description']}")
        print(f"  Total Nodes: {stats['total_nodes']}")
        print(f"  Node Types: {stats['node_types']}")

        # Export to file
        if output:
            xml_content = builder.export_to_xml(tree, output)
            log_info(f"Behavior tree exported to: {output}")
        else:
            # Display XML content
            xml_content = builder.export_to_xml(tree)
            print(f"\nXML Content:")
            print(xml_content)

    except Exception as e:
        log_error(f"Creation failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument("xml_file", type=click.Path(exists=True))
def validate(xml_file: str):
    """Validate XML file and behavior tree"""
    try:
        log_info(f"Validating XML file: {xml_file}")

        # Read XML content
        with open(xml_file, "r", encoding="utf-8") as f:
            xml_content = f.read()

        # Validate XML structure
        from abtree.utils.validators import validate_xml_structure

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

        log_info("Validation completed, all checks passed")

    except Exception as e:
        log_error(f"Validation failed: {e}")
        sys.exit(1)


@cli.command()
def list_nodes():
    """List all available node types"""
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
        log_error(f"Failed to list node types: {e}")
        sys.exit(1)


@cli.command()
@click.argument("xml_file", type=click.Path(exists=True))
def info(xml_file: str):
    """Display detailed behavior tree information"""
    try:
        log_info(f"Analyzing behavior tree: {xml_file}")

        # Parse XML
        parser = XMLParser()
        tree = parser.parse_file(xml_file)

        # Get statistics
        from abtree.utils.validators import get_tree_statistics

        stats = get_tree_statistics(tree)

        print(f"\n=== Behavior Tree Detailed Information ===")
        print(f"Name: {stats['name']}")
        print(f"Description: {stats['description']}")
        print(f"Total Nodes: {stats['total_nodes']}")
        print(f"Tree Depth: {stats['tree_depth']}")
        print(f"Max Depth: {stats['max_depth']}")

        print(f"\nNode Type Distribution:")
        for node_type, count in stats["node_types"].items():
            print(f"  {node_type}: {count}")

        print(f"\nStatus Distribution:")
        for status, count in stats["status_distribution"].items():
            print(f"  {status}: {count}")

        print(f"\nSystem Components:")
        print(f"  Blackboard System: {'✓' if stats['has_blackboard'] else '✗'}")
        print(f"  Event System: {'✓' if stats['has_event_system'] else '✗'}")
        print(f"  Tick Manager: {'✓' if stats['has_tick_manager'] else '✗'}")

        # Display node tree structure
        print(f"\nNode Tree Structure:")
        _print_node_tree(tree.root, 0)

    except Exception as e:
        log_error(f"Analysis failed: {e}")
        sys.exit(1)


def _print_node_tree(node, depth: int):
    """Print node tree structure"""
    indent = "  " * depth
    print(f"{indent}{node.__class__.__name__}: {node.name} ({node.status.name})")

    for child in node.children:
        _print_node_tree(child, depth + 1)


def main():
    """Main function"""
    cli()


if __name__ == "__main__":
    main()
