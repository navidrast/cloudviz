"""
Layout management for CloudViz visualizations.
Provides different layout algorithms for organizing diagram elements.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from cloudviz.core.models import CloudResource, ResourceRelationship
from cloudviz.core.utils import LoggerMixin


@dataclass
class LayoutConfig:
    """Configuration for layout algorithms."""
    name: str
    display_name: str
    description: str
    parameters: Dict[str, Any]


class BaseLayout(ABC, LoggerMixin):
    """Base class for layout algorithms."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize layout."""
        self.config = config or {}
    
    @property
    @abstractmethod
    def layout_config(self) -> LayoutConfig:
        """Get layout configuration."""
        pass
    
    @abstractmethod
    def arrange_resources(
        self,
        resources: List[CloudResource],
        relationships: List[ResourceRelationship]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Arrange resources according to layout algorithm.
        
        Args:
            resources: List of resources to arrange
            relationships: List of relationships between resources
            
        Returns:
            Dictionary mapping resource IDs to layout properties
        """
        pass
    
    def get_mermaid_direction(self) -> str:
        """Get Mermaid diagram direction for this layout."""
        return "TD"  # Top Down by default
    
    def get_graphviz_attributes(self) -> Dict[str, str]:
        """Get Graphviz attributes for this layout."""
        return {
            'rankdir': 'TB',
            'nodesep': '0.5',
            'ranksep': '0.5'
        }


class HierarchicalLayout(BaseLayout):
    """Hierarchical layout organizing resources by containment and dependencies."""
    
    @property
    def layout_config(self) -> LayoutConfig:
        """Get hierarchical layout configuration."""
        return LayoutConfig(
            name="hierarchical",
            display_name="Hierarchical",
            description="Organize resources in a top-down hierarchy based on containment relationships",
            parameters={
                'direction': self.config.get('direction', 'TD'),
                'group_by_type': self.config.get('group_by_type', False),
                'group_by_resource_group': self.config.get('group_by_resource_group', True),
                'separate_networks': self.config.get('separate_networks', True)
            }
        )
    
    def arrange_resources(
        self,
        resources: List[CloudResource],
        relationships: List[ResourceRelationship]
    ) -> Dict[str, Dict[str, Any]]:
        """Arrange resources hierarchically."""
        arrangement = {}
        
        # Build hierarchy based on containment relationships
        hierarchy = self._build_hierarchy(resources, relationships)
        
        # Assign levels based on hierarchy
        levels = self._assign_levels(hierarchy)
        
        # Group resources by resource group if enabled
        if self.layout_config.parameters['group_by_resource_group']:
            groups = self._group_by_resource_group(resources)
        else:
            groups = {'default': resources}
        
        # Arrange each group
        for group_name, group_resources in groups.items():
            group_arrangement = self._arrange_group_hierarchically(
                group_resources, levels, hierarchy
            )
            arrangement.update(group_arrangement)
        
        return arrangement
    
    def _build_hierarchy(
        self,
        resources: List[CloudResource],
        relationships: List[ResourceRelationship]
    ) -> Dict[str, List[str]]:
        """Build containment hierarchy."""
        hierarchy = {resource.id: [] for resource in resources}
        
        # Add containment relationships
        for rel in relationships:
            if rel.relationship_type.value == 'CONTAINS':
                hierarchy[rel.source_id].append(rel.target_id)
        
        return hierarchy
    
    def _assign_levels(self, hierarchy: Dict[str, List[str]]) -> Dict[str, int]:
        """Assign hierarchy levels to resources."""
        levels = {}
        visited = set()
        
        # Find root nodes (nodes with no parents)
        all_children = set()
        for children in hierarchy.values():
            all_children.update(children)
        
        roots = [node for node in hierarchy.keys() if node not in all_children]
        
        # Assign levels using BFS
        current_level = 0
        current_nodes = roots
        
        while current_nodes:
            next_nodes = []
            for node in current_nodes:
                if node not in visited:
                    levels[node] = current_level
                    visited.add(node)
                    next_nodes.extend(hierarchy.get(node, []))
            
            current_nodes = next_nodes
            current_level += 1
        
        # Assign level 0 to any unvisited nodes
        for node in hierarchy.keys():
            if node not in levels:
                levels[node] = 0
        
        return levels
    
    def _group_by_resource_group(
        self,
        resources: List[CloudResource]
    ) -> Dict[str, List[CloudResource]]:
        """Group resources by resource group."""
        groups = {}
        
        for resource in resources:
            group_name = resource.resource_group or 'default'
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(resource)
        
        return groups
    
    def _arrange_group_hierarchically(
        self,
        resources: List[CloudResource],
        levels: Dict[str, int],
        hierarchy: Dict[str, List[str]]
    ) -> Dict[str, Dict[str, Any]]:
        """Arrange a group of resources hierarchically."""
        arrangement = {}
        
        # Sort resources by level and type
        sorted_resources = sorted(
            resources,
            key=lambda r: (levels.get(r.id, 0), r.get_category(), r.name)
        )
        
        # Assign positions
        level_positions = {}
        for resource in sorted_resources:
            level = levels.get(resource.id, 0)
            
            if level not in level_positions:
                level_positions[level] = 0
            
            arrangement[resource.id] = {
                'level': level,
                'position': level_positions[level],
                'group': resource.resource_group or 'default',
                'category': resource.get_category()
            }
            
            level_positions[level] += 1
        
        return arrangement
    
    def get_mermaid_direction(self) -> str:
        """Get Mermaid direction for hierarchical layout."""
        direction = self.layout_config.parameters['direction']
        return direction
    
    def get_graphviz_attributes(self) -> Dict[str, str]:
        """Get Graphviz attributes for hierarchical layout."""
        direction = self.layout_config.parameters['direction']
        
        # Map direction to Graphviz rankdir
        direction_map = {
            'TD': 'TB',  # Top Down
            'DT': 'BT',  # Down Top
            'LR': 'LR',  # Left Right
            'RL': 'RL'   # Right Left
        }
        
        return {
            'rankdir': direction_map.get(direction, 'TB'),
            'nodesep': '0.5',
            'ranksep': '0.8',
            'splines': 'ortho'
        }


class CircularLayout(BaseLayout):
    """Circular layout arranging resources in concentric circles."""
    
    @property
    def layout_config(self) -> LayoutConfig:
        """Get circular layout configuration."""
        return LayoutConfig(
            name="circular",
            display_name="Circular",
            description="Arrange resources in concentric circles based on relationships",
            parameters={
                'center_resource': self.config.get('center_resource', None),
                'radius_increment': self.config.get('radius_increment', 1.0),
                'group_similar': self.config.get('group_similar', True)
            }
        )
    
    def arrange_resources(
        self,
        resources: List[CloudResource],
        relationships: List[ResourceRelationship]
    ) -> Dict[str, Dict[str, Any]]:
        """Arrange resources in circular layout."""
        arrangement = {}
        
        # Find center resource or choose most connected
        center_resource = self._find_center_resource(resources, relationships)
        
        # Build connection graph
        connections = self._build_connection_graph(resources, relationships)
        
        # Assign resources to circles based on distance from center
        circles = self._assign_to_circles(center_resource, connections)
        
        # Position resources within circles
        for circle_index, circle_resources in circles.items():
            circle_arrangement = self._arrange_circle(
                circle_resources, circle_index, len(circle_resources)
            )
            arrangement.update(circle_arrangement)
        
        return arrangement
    
    def _find_center_resource(
        self,
        resources: List[CloudResource],
        relationships: List[ResourceRelationship]
    ) -> str:
        """Find the most suitable center resource."""
        center = self.layout_config.parameters['center_resource']
        if center:
            return center
        
        # Count connections for each resource
        connection_counts = {}
        for resource in resources:
            connection_counts[resource.id] = 0
        
        for rel in relationships:
            if rel.source_id in connection_counts:
                connection_counts[rel.source_id] += 1
            if rel.target_id in connection_counts:
                connection_counts[rel.target_id] += 1
        
        # Return most connected resource
        if connection_counts:
            return max(connection_counts.items(), key=lambda x: x[1])[0]
        
        # Fallback to first resource
        return resources[0].id if resources else ""
    
    def _build_connection_graph(
        self,
        resources: List[CloudResource],
        relationships: List[ResourceRelationship]
    ) -> Dict[str, List[str]]:
        """Build bidirectional connection graph."""
        graph = {resource.id: [] for resource in resources}
        
        for rel in relationships:
            if rel.source_id in graph and rel.target_id in graph:
                graph[rel.source_id].append(rel.target_id)
                graph[rel.target_id].append(rel.source_id)
        
        return graph
    
    def _assign_to_circles(
        self,
        center: str,
        connections: Dict[str, List[str]]
    ) -> Dict[int, List[str]]:
        """Assign resources to concentric circles using BFS."""
        circles = {0: [center]}
        visited = {center}
        current_circle = 0
        
        while True:
            next_circle_resources = []
            
            for resource in circles[current_circle]:
                for connected in connections.get(resource, []):
                    if connected not in visited:
                        next_circle_resources.append(connected)
                        visited.add(connected)
            
            if not next_circle_resources:
                break
            
            current_circle += 1
            circles[current_circle] = next_circle_resources
        
        return circles
    
    def _arrange_circle(
        self,
        resources: List[str],
        circle_index: int,
        total_in_circle: int
    ) -> Dict[str, Dict[str, Any]]:
        """Arrange resources within a circle."""
        arrangement = {}
        
        radius = circle_index * self.layout_config.parameters['radius_increment']
        
        for i, resource_id in enumerate(resources):
            angle = (2 * 3.14159 * i) / total_in_circle if total_in_circle > 0 else 0
            
            arrangement[resource_id] = {
                'circle': circle_index,
                'position': i,
                'radius': radius,
                'angle': angle,
                'x': radius * (1 if circle_index == 0 else __import__('math').cos(angle)),
                'y': radius * (0 if circle_index == 0 else __import__('math').sin(angle))
            }
        
        return arrangement
    
    def get_graphviz_attributes(self) -> Dict[str, str]:
        """Get Graphviz attributes for circular layout."""
        return {
            'layout': 'circo',
            'overlap': 'false',
            'splines': 'curved'
        }


class ForceLayout(BaseLayout):
    """Force-directed layout using simulated physics."""
    
    @property
    def layout_config(self) -> LayoutConfig:
        """Get force layout configuration."""
        return LayoutConfig(
            name="force",
            display_name="Force-Directed",
            description="Use physics simulation to arrange resources naturally",
            parameters={
                'iterations': self.config.get('iterations', 100),
                'attraction_strength': self.config.get('attraction_strength', 1.0),
                'repulsion_strength': self.config.get('repulsion_strength', 1.0),
                'edge_length': self.config.get('edge_length', 1.0)
            }
        )
    
    def arrange_resources(
        self,
        resources: List[CloudResource],
        relationships: List[ResourceRelationship]
    ) -> Dict[str, Dict[str, Any]]:
        """Arrange resources using force-directed algorithm."""
        arrangement = {}
        
        # Simple force-directed positioning
        # In a real implementation, this would use iterative physics simulation
        
        # For now, arrange in a grid with some randomization
        import math
        
        grid_size = math.ceil(math.sqrt(len(resources)))
        
        for i, resource in enumerate(resources):
            row = i // grid_size
            col = i % grid_size
            
            # Add some pseudo-random offset based on connections
            connection_count = sum(
                1 for rel in relationships
                if rel.source_id == resource.id or rel.target_id == resource.id
            )
            
            offset_x = (connection_count % 3 - 1) * 0.2
            offset_y = ((connection_count // 3) % 3 - 1) * 0.2
            
            arrangement[resource.id] = {
                'x': col + offset_x,
                'y': row + offset_y,
                'grid_position': i,
                'connections': connection_count
            }
        
        return arrangement
    
    def get_graphviz_attributes(self) -> Dict[str, str]:
        """Get Graphviz attributes for force layout."""
        return {
            'layout': 'fdp',
            'overlap': 'false',
            'splines': 'curved',
            'K': str(self.layout_config.parameters['edge_length'])
        }


class GridLayout(BaseLayout):
    """Grid layout arranging resources in a regular grid."""
    
    @property
    def layout_config(self) -> LayoutConfig:
        """Get grid layout configuration."""
        return LayoutConfig(
            name="grid",
            display_name="Grid",
            description="Arrange resources in a regular grid pattern",
            parameters={
                'columns': self.config.get('columns', None),
                'group_by_type': self.config.get('group_by_type', True),
                'spacing': self.config.get('spacing', 1.0)
            }
        )
    
    def arrange_resources(
        self,
        resources: List[CloudResource],
        relationships: List[ResourceRelationship]
    ) -> Dict[str, Dict[str, Any]]:
        """Arrange resources in grid layout."""
        arrangement = {}
        
        # Group by type if enabled
        if self.layout_config.parameters['group_by_type']:
            grouped_resources = self._group_by_type(resources)
        else:
            grouped_resources = {'all': resources}
        
        current_row = 0
        
        for group_name, group_resources in grouped_resources.items():
            group_arrangement = self._arrange_group_in_grid(
                group_resources, current_row
            )
            arrangement.update(group_arrangement)
            
            # Calculate rows used by this group
            columns = self._calculate_columns(len(group_resources))
            import math
            rows_used = math.ceil(len(group_resources) / columns)
            current_row += rows_used + 1  # Add spacing between groups
        
        return arrangement
    
    def _group_by_type(
        self,
        resources: List[CloudResource]
    ) -> Dict[str, List[CloudResource]]:
        """Group resources by type."""
        groups = {}
        
        for resource in resources:
            res_type = resource.get_category()
            if res_type not in groups:
                groups[res_type] = []
            groups[res_type].append(resource)
        
        return groups
    
    def _calculate_columns(self, resource_count: int) -> int:
        """Calculate optimal number of columns."""
        columns = self.layout_config.parameters['columns']
        if columns:
            return columns
        
        # Calculate square-ish grid
        import math
        return math.ceil(math.sqrt(resource_count))
    
    def _arrange_group_in_grid(
        self,
        resources: List[CloudResource],
        start_row: int
    ) -> Dict[str, Dict[str, Any]]:
        """Arrange a group of resources in grid."""
        arrangement = {}
        columns = self._calculate_columns(len(resources))
        
        for i, resource in enumerate(resources):
            row = start_row + (i // columns)
            col = i % columns
            
            arrangement[resource.id] = {
                'row': row,
                'column': col,
                'grid_position': i,
                'group': resource.get_category()
            }
        
        return arrangement
    
    def get_graphviz_attributes(self) -> Dict[str, str]:
        """Get Graphviz attributes for grid layout."""
        spacing = self.layout_config.parameters['spacing']
        
        return {
            'layout': 'neato',
            'overlap': 'false',
            'nodesep': str(spacing),
            'ranksep': str(spacing)
        }


class RadialLayout(BaseLayout):
    """Radial layout with resources arranged in radial patterns."""
    
    @property
    def layout_config(self) -> LayoutConfig:
        """Get radial layout configuration."""
        return LayoutConfig(
            name="radial",
            display_name="Radial",
            description="Arrange resources in radial patterns from a central point",
            parameters={
                'center_resource': self.config.get('center_resource', None),
                'angle_increment': self.config.get('angle_increment', 30),
                'radius_base': self.config.get('radius_base', 2.0)
            }
        )
    
    def arrange_resources(
        self,
        resources: List[CloudResource],
        relationships: List[ResourceRelationship]
    ) -> Dict[str, Dict[str, Any]]:
        """Arrange resources in radial layout."""
        arrangement = {}
        
        # Find center resource
        center = self._find_center_resource(resources, relationships)
        
        # Group other resources by type
        other_resources = [r for r in resources if r.id != center]
        grouped = self._group_by_type(other_resources)
        
        # Place center
        arrangement[center] = {
            'x': 0,
            'y': 0,
            'radius': 0,
            'angle': 0,
            'is_center': True
        }
        
        # Arrange groups in radial pattern
        angle_per_group = 360.0 / len(grouped) if grouped else 0
        current_angle = 0
        
        for group_name, group_resources in grouped.items():
            group_arrangement = self._arrange_group_radially(
                group_resources, current_angle, angle_per_group
            )
            arrangement.update(group_arrangement)
            current_angle += angle_per_group
        
        return arrangement
    
    def _find_center_resource(
        self,
        resources: List[CloudResource],
        relationships: List[ResourceRelationship]
    ) -> str:
        """Find center resource (similar to circular layout)."""
        center = self.layout_config.parameters['center_resource']
        if center:
            return center
        
        # Use first resource as fallback
        return resources[0].id if resources else ""
    
    def _group_by_type(
        self,
        resources: List[CloudResource]
    ) -> Dict[str, List[CloudResource]]:
        """Group resources by type."""
        groups = {}
        
        for resource in resources:
            res_type = resource.get_category()
            if res_type not in groups:
                groups[res_type] = []
            groups[res_type].append(resource)
        
        return groups
    
    def _arrange_group_radially(
        self,
        resources: List[CloudResource],
        start_angle: float,
        angle_span: float
    ) -> Dict[str, Dict[str, Any]]:
        """Arrange a group of resources radially."""
        import math
        arrangement = {}
        
        radius = self.layout_config.parameters['radius_base']
        angle_increment = min(
            angle_span / len(resources) if resources else 0,
            self.layout_config.parameters['angle_increment']
        )
        
        for i, resource in enumerate(resources):
            angle = start_angle + (i * angle_increment)
            angle_rad = math.radians(angle)
            
            arrangement[resource.id] = {
                'x': radius * math.cos(angle_rad),
                'y': radius * math.sin(angle_rad),
                'radius': radius,
                'angle': angle,
                'group': resource.get_category(),
                'position': i
            }
        
        return arrangement
    
    def get_graphviz_attributes(self) -> Dict[str, str]:
        """Get Graphviz attributes for radial layout."""
        return {
            'layout': 'twopi',
            'overlap': 'false',
            'splines': 'curved'
        }


class LayoutManager(LoggerMixin):
    """Manager for layout algorithms."""
    
    def __init__(self):
        """Initialize layout manager."""
        self._layouts = {}
        self._register_default_layouts()
    
    def _register_default_layouts(self):
        """Register default layout algorithms."""
        self.register_layout(HierarchicalLayout())
        self.register_layout(CircularLayout())
        self.register_layout(ForceLayout())
        self.register_layout(GridLayout())
        self.register_layout(RadialLayout())
    
    def register_layout(self, layout: BaseLayout):
        """Register a layout algorithm."""
        self._layouts[layout.layout_config.name] = layout
        self.log_debug("Registered layout", layout=layout.layout_config.name)
    
    def get_layout(self, layout_name: str) -> Optional[BaseLayout]:
        """Get a layout by name."""
        return self._layouts.get(layout_name)
    
    def get_available_layouts(self) -> List[str]:
        """Get list of available layout names."""
        return list(self._layouts.keys())
    
    def get_layout_info(self, layout_name: str) -> Optional[Dict[str, Any]]:
        """Get layout information."""
        layout = self.get_layout(layout_name)
        if layout:
            config = layout.layout_config
            return {
                'name': config.name,
                'display_name': config.display_name,
                'description': config.description,
                'parameters': config.parameters
            }
        return None
    
    def get_all_layouts_info(self) -> List[Dict[str, Any]]:
        """Get information for all layouts."""
        return [self.get_layout_info(name) for name in self.get_available_layouts()]
