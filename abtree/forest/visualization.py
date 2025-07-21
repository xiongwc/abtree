"""
Behavior Forest Visualization Module

This module provides visualization capabilities for behavior forests,
including forest structure visualization, node relationship graphs,
and real-time monitoring dashboards.
"""

import asyncio
import json
import logging
from dataclasses import asdict
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

try:
    import matplotlib.pyplot as plt
    import networkx as nx
    from matplotlib.animation import FuncAnimation
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    plt = None
    nx = None

from .core import BehaviorForest, ForestNode, ForestNodeType


class ForestVisualizer:
    """
    Visualizer for behavior forests.
    
    Provides methods to visualize forest structure, node relationships,
    and real-time monitoring of forest execution.
    """
    
    def __init__(self, forest: BehaviorForest):
        self.forest = forest
        self.logger = logging.getLogger(f"ForestVisualizer.{forest.name}")
        self._node_positions = {}
        self._animation = None
        
    def create_forest_graph(self) -> 'nx.DiGraph':
        """Create a NetworkX graph representation of the forest."""
        if not VISUALIZATION_AVAILABLE:
            raise ImportError("matplotlib and networkx are required for visualization")
            
        G = nx.DiGraph()
        
        # Add nodes
        for node_name, node in self.forest.nodes.items():
            G.add_node(node_name, 
                      type=node.node_type.value,
                      capabilities=list(node.capabilities),
                      status=node.status.value)
        
        # Add edges based on middleware connections
        for middleware in self.forest.middleware:
            if hasattr(middleware, 'get_connections'):
                connections = middleware.get_connections()
                for source, target in connections:
                    G.add_edge(source, target, middleware=type(middleware).__name__)
        
        return G
    
    def visualize_forest_structure(self, 
                                 figsize: tuple = (12, 8),
                                 save_path: Optional[str] = None) -> None:
        """Visualize the forest structure as a graph."""
        if not VISUALIZATION_AVAILABLE:
            self.logger.warning("Visualization libraries not available")
            return
            
        G = self.create_forest_graph()
        
        plt.figure(figsize=figsize)
        
        # Create layout
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Draw nodes with different colors based on type
        node_colors = []
        for node in G.nodes():
            node_type = G.nodes[node]['type']
            if node_type == 'master':
                node_colors.append('red')
            elif node_type == 'coordinator':
                node_colors.append('blue')
            elif node_type == 'worker':
                node_colors.append('green')
            else:
                node_colors.append('gray')
        
        # Draw the graph
        nx.draw(G, pos, 
                node_color=node_colors,
                node_size=2000,
                font_size=8,
                font_weight='bold',
                arrows=True,
                edge_color='gray',
                width=2)
        
        # Add labels
        labels = {node: f"{node}\n{G.nodes[node]['type']}" 
                 for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=6)
        
        plt.title(f"Behavior Forest: {self.forest.name}")
        plt.axis('off')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close()
    
    def create_real_time_monitor(self, update_interval: float = 1.0):
        """Create a real-time monitoring dashboard."""
        if not VISUALIZATION_AVAILABLE:
            self.logger.warning("Visualization libraries not available")
            return
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        def update(frame):
            ax1.clear()
            ax2.clear()
            
            # Update forest status
            self._plot_forest_status(ax1)
            self._plot_node_performance(ax2)
            
            plt.tight_layout()
        
        self._animation = FuncAnimation(fig, update, 
                                      interval=update_interval * 1000,
                                      blit=False)
        plt.show()
    
    def _plot_forest_status(self, ax):
        """Plot forest status information."""
        status_counts = {}
        for node in self.forest.nodes.values():
            status = node.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            ax.pie(status_counts.values(), 
                   labels=status_counts.keys(),
                   autopct='%1.1f%%')
            ax.set_title('Node Status Distribution')
    
    def _plot_node_performance(self, ax):
        """Plot node performance metrics."""
        node_names = list(self.forest.nodes.keys())
        execution_times = [0.1] * len(node_names)  # Placeholder
        
        ax.bar(node_names, execution_times)
        ax.set_title('Node Execution Times')
        ax.set_ylabel('Time (ms)')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def export_forest_data(self, format: str = 'json') -> str:
        """Export forest data for external visualization."""
        data = {
            'forest_name': self.forest.name,
            'timestamp': datetime.now().isoformat(),
            'nodes': {},
            'middleware': [type(mw).__name__ for mw in self.forest.middleware],
            'running': self.forest.running
        }
        
        for node_name, node in self.forest.nodes.items():
            data['nodes'][node_name] = {
                'type': node.node_type.value,
                'capabilities': list(node.capabilities),
                'status': node.status.value,
                'metadata': node.metadata
            }
        
        if format == 'json':
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def generate_forest_report(self) -> Dict[str, Any]:
        """Generate a comprehensive forest report."""
        report = {
            'forest_info': {
                'name': self.forest.name,
                'node_count': len(self.forest.nodes),
                'middleware_count': len(self.forest.middleware),
                'running': self.forest.running
            },
            'node_analysis': {},
            'middleware_analysis': {},
            'performance_metrics': {}
        }
        
        # Node analysis
        type_counts = {}
        status_counts = {}
        capability_counts = {}
        
        for node_name, node in self.forest.nodes.items():
            # Type distribution
            node_type = node.node_type.value
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
            
            # Status distribution
            status = node.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Capability analysis
            for capability in node.capabilities:
                capability_counts[capability] = capability_counts.get(capability, 0) + 1
        
        report['node_analysis'] = {
            'type_distribution': type_counts,
            'status_distribution': status_counts,
            'capability_distribution': capability_counts
        }
        
        # Middleware analysis
        for i, middleware in enumerate(self.forest.middleware):
            middleware_name = f"Middleware_{i}"
            report['middleware_analysis'][middleware_name] = {
                'type': type(middleware).__name__,
                'active': hasattr(middleware, 'is_active') and middleware.is_active()
            }
        
        return report


class ForestDashboard:
    """
    Real-time dashboard for monitoring behavior forests.
    
    Provides a web-based or console-based dashboard for monitoring
    forest execution, node status, and performance metrics.
    """
    
    def __init__(self, forests: List[BehaviorForest]):
        self.forests = forests
        self.logger = logging.getLogger("ForestDashboard")
        self.metrics = {}
        
    async def start_monitoring(self, update_interval: float = 1.0):
        """Start real-time monitoring of all forests."""
        self.logger.info("Starting forest monitoring dashboard")
        
        while True:
            await self._update_metrics()
            await self._display_dashboard()
            await asyncio.sleep(update_interval)
    
    async def _update_metrics(self):
        """Update forest metrics."""
        for forest in self.forests:
            self.metrics[forest.name] = {
                'node_count': len(forest.nodes),
                'running': forest.running,
                'node_status': {
                    name: node.status.value 
                    for name, node in forest.nodes.items()
                },
                'middleware_status': {
                    f"Middleware_{i}": hasattr(mw, 'is_active') and mw.is_active()
                    for i, mw in enumerate(forest.middleware)
                }
            }
    
    async def _display_dashboard(self):
        """Display the monitoring dashboard."""
        print("\n" + "="*60)
        print("BEHAVIOR FOREST MONITORING DASHBOARD")
        print("="*60)
        
        for forest_name, metrics in self.metrics.items():
            print(f"\n🌳 Forest: {forest_name}")
            print(f"   Status: {'🟢 Running' if metrics['running'] else '🔴 Stopped'}")
            print(f"   Nodes: {metrics['node_count']}")
            
            print("   Node Status:")
            for node_name, status in metrics['node_status'].items():
                status_icon = "🟢" if status == "SUCCESS" else "🔴" if status == "FAILURE" else "🟡"
                print(f"     {status_icon} {node_name}: {status}")
            
            print("   Middleware:")
            for mw_name, active in metrics['middleware_status'].items():
                status_icon = "🟢" if active else "🔴"
                print(f"     {status_icon} {mw_name}")
        
        print("\n" + "="*60)


def create_forest_visualizer(forest: BehaviorForest) -> ForestVisualizer:
    """Create a visualizer for a behavior forest."""
    return ForestVisualizer(forest)


def create_forest_dashboard(forests: List[BehaviorForest]) -> ForestDashboard:
    """Create a dashboard for monitoring multiple forests."""
    return ForestDashboard(forests) 