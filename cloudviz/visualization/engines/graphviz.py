"""
Graphviz DOT engine for CloudViz.
Generates Graphviz DOT files for cloud infrastructure visualization.
"""

import json
from typing import Dict, List, Optional, Any, Set
from cloudviz.core.base import VisualizationEngine
from cloudviz.core.models import ResourceInventory, CloudResource, ResourceRelationship, RelationshipType
from cloudviz.core.utils import get_logger, LoggerMixin


class GraphvizEngine(VisualizationEngine, LoggerMixin):
    """
    Graphviz DOT diagram generation engine.
    Creates DOT files for rendering with Graphviz tools.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Graphviz engine."""
        super().__init__(config)
        self.supported_formats = ['dot', 'gv']
        self.supported_themes = ['professional', 'dark', 'light', 'minimal', 'colorful']
        self.supported_layouts = ['hierarchical', 'circular', 'force', 'grid', 'radial']
        
        # Graphviz configuration
        self.rankdir = self.config.get('rankdir', 'TB')  # TB, BT, LR, RL
        self.splines = self.config.get('splines', 'ortho')  # ortho, spline, line, polyline
        self.overlap = self.config.get('overlap', 'false')
        self.nodesep = self.config.get('nodesep', '0.5')
        self.ranksep = self.config.get('ranksep', '0.5')
        self.fontname = self.config.get('fontname', 'Arial')
        self.fontsize = self.config.get('fontsize', '10')
        
        # Content options
        self.include_resource_types = self.config.get('include_resource_types', True)
        self.include_regions = self.config.get('include_regions', True)
        self.group_by_resource_group = self.config.get('group_by_resource_group', True)
        self.show_relationships = self.config.get('show_relationships', True)
        self.max_label_length = self.config.get('max_label_length', 30)
    
    async def render(
        self,
        inventory: ResourceInventory,
        output_format: str = 'dot',
        theme: Optional[str] = None,
        layout: Optional[str] = None,
        **kwargs
    ) -> bytes:
        """
        Render resource inventory as Graphviz DOT.
        
        Args:
            inventory: Resource inventory to visualize
            output_format: Output format (dot, gv)
            theme: Visual theme
            layout: Layout algorithm
            **kwargs: Additional rendering parameters
            
        Returns:
            bytes: DOT diagram as UTF-8 encoded bytes
        """
        self.log_info("Rendering Graphviz DOT diagram",
                     resource_count=len(inventory.resources),
                     format=output_format,
                     theme=theme,
                     layout=layout)
        
        # Validate options
        if not await self.validate_options(output_format, theme, layout):
            raise ValueError(f"Invalid rendering options: format={output_format}, theme={theme}, layout={layout}")
        
        # Set defaults
        theme = theme or 'professional'
        layout = layout or 'hierarchical'
        
        # Override config with kwargs
        rankdir = kwargs.get('rankdir', self.rankdir)
        splines = kwargs.get('splines', self.splines)
        
        try:
            # Generate DOT content
            dot_content = self._generate_dot_content(inventory, theme, layout, rankdir, splines, **kwargs)
            
            self.log_info("Graphviz DOT diagram generated successfully",
                         content_length=len(dot_content))
            
            return dot_content.encode('utf-8')
            
        except Exception as e:
            self.log_error("Failed to render Graphviz DOT diagram", exc_info=True, error=str(e))
            raise
    
    def _generate_dot_content(
        self,
        inventory: ResourceInventory,
        theme: str,
        layout: str,
        rankdir: str,
        splines: str,
        **kwargs
    ) -> str:
        """Generate complete DOT file content."""
        lines = []
        
        # Start DOT graph
        graph_name = kwargs.get('graph_name', 'CloudInfrastructure')
        lines.append(f'digraph "{graph_name}" {{')
        
        # Graph attributes
        lines.extend(self._get_graph_attributes(rankdir, splines, layout, theme))
        
        # Node defaults
        lines.extend(self._get_default_node_attributes(theme))
        
        # Edge defaults
        lines.extend(self._get_default_edge_attributes(theme))
        
        # Add resources
        if self.group_by_resource_group:
            lines.extend(self._add_resource_groups(inventory.resources, theme))
        else:
            lines.extend(self._add_resources(inventory.resources, theme))
        
        # Add relationships
        if self.show_relationships and inventory.relationships:
            lines.append('')
            lines.append('    // Relationships')
            lines.extend(self._add_relationships(inventory.relationships, theme))
        
        # Add layout-specific constraints
        lines.extend(self._add_layout_constraints(layout, inventory.resources))
        
        # Close graph
        lines.append('}')
        
        # Add metadata as comments
        content = '\n'.join(lines)
        content = self._add_metadata_comments(content, inventory)
        
        return content
    
    def _get_graph_attributes(self, rankdir: str, splines: str, layout: str, theme: str) -> List[str]:
        """Get graph-level attributes."""
        attrs = []
        attrs.append('    // Graph attributes')
        attrs.append(f'    rankdir="{rankdir}";')
        attrs.append(f'    splines="{splines}";')
        attrs.append(f'    overlap="{self.overlap}";')
        attrs.append(f'    nodesep="{self.nodesep}";')
        attrs.append(f'    ranksep="{self.ranksep}";')
        attrs.append(f'    fontname="{self.fontname}";')
        attrs.append(f'    fontsize="{self.fontsize}";')
        
        # Layout-specific attributes
        if layout == 'circular':
            attrs.append('    layout="circo";')
        elif layout == 'force':
            attrs.append('    layout="fdp";')
        elif layout == 'radial':
            attrs.append('    layout="twopi";')
        else:
            attrs.append('    layout="dot";')
        
        # Theme-specific graph attributes
        theme_attrs = self._get_theme_graph_attributes(theme)
        attrs.extend(theme_attrs)
        
        attrs.append('')
        return attrs
    
    def _get_default_node_attributes(self, theme: str) -> List[str]:
        """Get default node attributes."""
        attrs = []
        attrs.append('    // Default node attributes')
        attrs.append('    node [')
        attrs.append(f'        fontname="{self.fontname}",')
        attrs.append(f'        fontsize="{self.fontsize}",')
        attrs.append('        shape="box",')
        attrs.append('        style="rounded,filled",')
        
        # Theme-specific defaults
        theme_attrs = self._get_theme_node_attributes(theme)
        attrs.extend([f'        {attr}' for attr in theme_attrs])
        
        attrs.append('    ];')
        attrs.append('')
        return attrs
    
    def _get_default_edge_attributes(self, theme: str) -> List[str]:
        """Get default edge attributes."""
        attrs = []
        attrs.append('    // Default edge attributes')
        attrs.append('    edge [')
        attrs.append(f'        fontname="{self.fontname}",')
        attrs.append(f'        fontsize="{int(self.fontsize) - 1}",')
        
        # Theme-specific defaults
        theme_attrs = self._get_theme_edge_attributes(theme)
        attrs.extend([f'        {attr}' for attr in theme_attrs])
        
        attrs.append('    ];')
        attrs.append('')
        return attrs
    
    def _add_resource_groups(self, resources: List[CloudResource], theme: str) -> List[str]:
        """Add resources grouped by resource group."""
        lines = []
        lines.append('    // Resource Groups')
        
        # Group resources
        groups = self._group_resources_by_resource_group(resources)
        
        cluster_id = 0
        for rg_name, rg_resources in groups.items():
            if rg_name and rg_resources:
                cluster_id += 1
                
                # Create cluster (subgraph)
                lines.append(f'    subgraph "cluster_{cluster_id}" {{')
                lines.append(f'        label="{rg_name}";')
                lines.append('        style="rounded,filled";')
                lines.append('        fillcolor="#f0f0f0";')
                lines.append('        color="#cccccc";')
                lines.append('')
                
                # Add resources in this group
                for resource in rg_resources:
                    node_def = self._create_resource_node(resource, theme, indent='        ')
                    lines.append(node_def)
                
                lines.append('    }')
                lines.append('')
        
        # Add ungrouped resources
        ungrouped = groups.get('', []) + groups.get('No Resource Group', [])
        if ungrouped:
            lines.append('    // Ungrouped Resources')
            for resource in ungrouped:
                node_def = self._create_resource_node(resource, theme, indent='    ')
                lines.append(node_def)
            lines.append('')
        
        return lines
    
    def _add_resources(self, resources: List[CloudResource], theme: str) -> List[str]:
        """Add resources without grouping."""
        lines = []
        lines.append('    // Resources')
        
        for resource in resources:
            node_def = self._create_resource_node(resource, theme, indent='    ')
            lines.append(node_def)
        
        lines.append('')
        return lines
    
    def _create_resource_node(self, resource: CloudResource, theme: str, indent: str = '    ') -> str:
        """Create DOT node definition for a resource."""
        node_id = self._sanitize_id(resource.id)
        label = self._create_resource_label(resource)
        
        # Get node attributes based on resource type
        attrs = self._get_resource_node_attributes(resource, theme)
        attr_str = ', '.join(attrs)
        
        return f'{indent}"{node_id}" [{attr_str}];'
    
    def _create_resource_label(self, resource: CloudResource) -> str:
        """Create display label for a resource."""
        parts = []
        
        # Resource name
        name = self._escape_label(self._truncate_label(resource.name))
        parts.append(name)
        
        # Add resource type if enabled
        if self.include_resource_types:
            res_type = self._escape_label(resource.get_category())
            parts.append(f'({res_type})')
        
        # Add region if enabled
        if self.include_regions and resource.region:
            region = self._escape_label(resource.region)
            parts.append(f'[{region}]')
        
        return '\\n'.join(parts)
    
    def _get_resource_node_attributes(self, resource: CloudResource, theme: str) -> List[str]:
        """Get node attributes for a specific resource."""
        attrs = []
        
        # Label
        label = self._create_resource_label(resource)
        attrs.append(f'label="{label}"')
        
        # Shape based on resource type
        shape = self._get_resource_shape(resource)
        if shape:
            attrs.append(f'shape="{shape}"')
        
        # Color based on resource type and theme
        colors = self._get_resource_colors(resource, theme)
        if colors.get('fillcolor'):
            attrs.append(f'fillcolor="{colors["fillcolor"]}"')
        if colors.get('color'):
            attrs.append(f'color="{colors["color"]}"')
        if colors.get('fontcolor'):
            attrs.append(f'fontcolor="{colors["fontcolor"]}"')
        
        return attrs
    
    def _get_resource_shape(self, resource: CloudResource) -> str:
        """Get DOT shape for resource type."""
        category = resource.get_category()
        
        shape_map = {
            'Compute': 'box',
            'Storage': 'ellipse',
            'Networking': 'diamond',
            'Database': 'cylinder',
            'Security': 'octagon',
            'Management': 'folder',
            'Other': 'box'
        }
        
        return shape_map.get(category, 'box')
    
    def _get_resource_colors(self, resource: CloudResource, theme: str) -> Dict[str, str]:
        """Get colors for resource based on type and theme."""
        category = resource.get_category()
        
        color_schemes = {
            'professional': {
                'Compute': {'fillcolor': '#0078d4', 'color': '#005a9e', 'fontcolor': 'white'},
                'Storage': {'fillcolor': '#00bcf2', 'color': '#0082a6', 'fontcolor': 'white'},
                'Networking': {'fillcolor': '#7fba00', 'color': '#5c8a00', 'fontcolor': 'white'},
                'Database': {'fillcolor': '#ff6c00', 'color': '#cc5500', 'fontcolor': 'white'},
                'Security': {'fillcolor': '#5c2d91', 'color': '#4a2574', 'fontcolor': 'white'},
                'Management': {'fillcolor': '#68217a', 'color': '#531968', 'fontcolor': 'white'},
                'Other': {'fillcolor': '#737373', 'color': '#525252', 'fontcolor': 'white'}
            },
            'dark': {
                'Compute': {'fillcolor': '#2d3748', 'color': '#4a5568', 'fontcolor': '#e2e8f0'},
                'Storage': {'fillcolor': '#2c5282', 'color': '#3182ce', 'fontcolor': '#e2e8f0'},
                'Networking': {'fillcolor': '#276749', 'color': '#38a169', 'fontcolor': '#e2e8f0'},
                'Database': {'fillcolor': '#9c4221', 'color': '#dd6b20', 'fontcolor': '#e2e8f0'},
                'Security': {'fillcolor': '#553c9a', 'color': '#805ad5', 'fontcolor': '#e2e8f0'},
                'Management': {'fillcolor': '#702459', 'color': '#d53f8c', 'fontcolor': '#e2e8f0'},
                'Other': {'fillcolor': '#4a5568', 'color': '#6b7280', 'fontcolor': '#e2e8f0'}
            },
            'light': {
                'Compute': {'fillcolor': '#ebf8ff', 'color': '#3182ce', 'fontcolor': '#2c5282'},
                'Storage': {'fillcolor': '#e6fffa', 'color': '#38b2ac', 'fontcolor': '#285e61'},
                'Networking': {'fillcolor': '#f0fff4', 'color': '#38a169', 'fontcolor': '#276749'},
                'Database': {'fillcolor': '#fffaf0', 'color': '#dd6b20', 'fontcolor': '#9c4221'},
                'Security': {'fillcolor': '#faf5ff', 'color': '#805ad5', 'fontcolor': '#553c9a'},
                'Management': {'fillcolor': '#fdf2f8', 'color': '#d53f8c', 'fontcolor': '#702459'},
                'Other': {'fillcolor': '#f9fafb', 'color': '#6b7280', 'fontcolor': '#374151'}
            },
            'minimal': {
                'Compute': {'fillcolor': '#f9f9f9', 'color': '#d1d5db', 'fontcolor': '#374151'},
                'Storage': {'fillcolor': '#f9f9f9', 'color': '#d1d5db', 'fontcolor': '#374151'},
                'Networking': {'fillcolor': '#f9f9f9', 'color': '#d1d5db', 'fontcolor': '#374151'},
                'Database': {'fillcolor': '#f9f9f9', 'color': '#d1d5db', 'fontcolor': '#374151'},
                'Security': {'fillcolor': '#f9f9f9', 'color': '#d1d5db', 'fontcolor': '#374151'},
                'Management': {'fillcolor': '#f9f9f9', 'color': '#d1d5db', 'fontcolor': '#374151'},
                'Other': {'fillcolor': '#f9f9f9', 'color': '#d1d5db', 'fontcolor': '#374151'}
            },
            'colorful': {
                'Compute': {'fillcolor': '#ff6b6b', 'color': '#ee5a52', 'fontcolor': 'white'},
                'Storage': {'fillcolor': '#4ecdc4', 'color': '#45b7b8', 'fontcolor': 'white'},
                'Networking': {'fillcolor': '#45b7d1', 'color': '#3498db', 'fontcolor': 'white'},
                'Database': {'fillcolor': '#f9ca24', 'color': '#f0932b', 'fontcolor': 'black'},
                'Security': {'fillcolor': '#6c5ce7', 'color': '#a29bfe', 'fontcolor': 'white'},
                'Management': {'fillcolor': '#fd79a8', 'color': '#e84393', 'fontcolor': 'white'},
                'Other': {'fillcolor': '#78e08f', 'color': '#6ab04c', 'fontcolor': 'white'}
            }
        }
        
        scheme = color_schemes.get(theme, color_schemes['professional'])
        return scheme.get(category, scheme['Other'])
    
    def _add_relationships(self, relationships: List[ResourceRelationship], theme: str) -> List[str]:
        """Add relationship edges."""
        lines = []
        
        for relationship in relationships:
            edge_def = self._create_relationship_edge(relationship, theme)
            if edge_def:
                lines.append(f'    {edge_def}')
        
        return lines
    
    def _create_relationship_edge(self, relationship: ResourceRelationship, theme: str) -> Optional[str]:
        """Create DOT edge definition for a relationship."""
        source_id = self._sanitize_id(relationship.source_id)
        target_id = self._sanitize_id(relationship.target_id)
        
        # Edge attributes
        attrs = []
        
        # Label
        label = relationship.get_edge_label()
        if label:
            escaped_label = self._escape_label(label)
            attrs.append(f'label="{escaped_label}"')
        
        # Style based on relationship type
        style = self._get_relationship_style(relationship.relationship_type)
        if style:
            attrs.append(f'style="{style}"')
        
        # Color based on relationship type and theme
        color = self._get_relationship_color(relationship.relationship_type, theme)
        if color:
            attrs.append(f'color="{color}"')
        
        attr_str = ', '.join(attrs) if attrs else ''
        
        if attr_str:
            return f'"{source_id}" -> "{target_id}" [{attr_str}];'
        else:
            return f'"{source_id}" -> "{target_id}";'
    
    def _get_relationship_style(self, relationship_type: RelationshipType) -> str:
        """Get edge style for relationship type."""
        style_map = {
            RelationshipType.CONTAINS: 'solid',
            RelationshipType.CONNECTS_TO: 'dashed',
            RelationshipType.DEPENDS_ON: 'bold',
            RelationshipType.MANAGED_BY: 'solid',
            RelationshipType.SECURED_BY: 'dotted',
            RelationshipType.ROUTES_TO: 'dashed',
            RelationshipType.REPLICATES_TO: 'bold',
            RelationshipType.BACKS_UP_TO: 'bold'
        }
        return style_map.get(relationship_type, 'solid')
    
    def _get_relationship_color(self, relationship_type: RelationshipType, theme: str) -> str:
        """Get edge color for relationship type."""
        if theme == 'minimal':
            return '#6b7280'
        elif theme == 'dark':
            return '#9ca3af'
        
        color_map = {
            RelationshipType.CONTAINS: '#0078d4',
            RelationshipType.CONNECTS_TO: '#7fba00',
            RelationshipType.DEPENDS_ON: '#ff6c00',
            RelationshipType.MANAGED_BY: '#5c2d91',
            RelationshipType.SECURED_BY: '#dc2626',
            RelationshipType.ROUTES_TO: '#059669',
            RelationshipType.REPLICATES_TO: '#dc2626',
            RelationshipType.BACKS_UP_TO: '#0891b2'
        }
        return color_map.get(relationship_type, '#6b7280')
    
    def _add_layout_constraints(self, layout: str, resources: List[CloudResource]) -> List[str]:
        """Add layout-specific constraints."""
        lines = []
        
        if layout == 'hierarchical':
            # Group resources by type on same rank
            by_type = {}
            for resource in resources:
                res_type = resource.get_category()
                if res_type not in by_type:
                    by_type[res_type] = []
                by_type[res_type].append(resource)
            
            if len(by_type) > 1:
                lines.append('')
                lines.append('    // Layout constraints')
                for res_type, type_resources in by_type.items():
                    if len(type_resources) > 1:
                        node_ids = [f'"{self._sanitize_id(r.id)}"' for r in type_resources]
                        lines.append(f'    {{ rank=same; {"; ".join(node_ids)}; }}')
        
        return lines
    
    def _get_theme_graph_attributes(self, theme: str) -> List[str]:
        """Get theme-specific graph attributes."""
        attrs = []
        
        if theme == 'dark':
            attrs.append('    bgcolor="#1a202c";')
            attrs.append('    fontcolor="#e2e8f0";')
        elif theme == 'light':
            attrs.append('    bgcolor="#ffffff";')
            attrs.append('    fontcolor="#374151";')
        elif theme == 'minimal':
            attrs.append('    bgcolor="#ffffff";')
            attrs.append('    fontcolor="#6b7280";')
        
        return attrs
    
    def _get_theme_node_attributes(self, theme: str) -> List[str]:
        """Get theme-specific default node attributes."""
        if theme == 'minimal':
            return ['fillcolor="#f9fafb"', 'color="#d1d5db"', 'fontcolor="#374151"']
        elif theme == 'dark':
            return ['fillcolor="#374151"', 'color="#6b7280"', 'fontcolor="#e2e8f0"']
        else:
            return ['fillcolor="#ffffff"', 'color="#374151"', 'fontcolor="#374151"']
    
    def _get_theme_edge_attributes(self, theme: str) -> List[str]:
        """Get theme-specific default edge attributes."""
        if theme == 'minimal':
            return ['color="#9ca3af"', 'fontcolor="#6b7280"']
        elif theme == 'dark':
            return ['color="#9ca3af"', 'fontcolor="#e2e8f0"']
        else:
            return ['color="#6b7280"', 'fontcolor="#374151"']
    
    def _group_resources_by_resource_group(self, resources: List[CloudResource]) -> Dict[str, List[CloudResource]]:
        """Group resources by resource group."""
        groups = {}
        
        for resource in resources:
            rg_name = resource.resource_group or ""
            if rg_name not in groups:
                groups[rg_name] = []
            groups[rg_name].append(resource)
        
        return groups
    
    def _sanitize_id(self, resource_id: str) -> str:
        """Sanitize resource ID for DOT format."""
        # Replace problematic characters
        sanitized = resource_id.replace('/', '_').replace('-', '_').replace('.', '_')
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c == '_')
        return sanitized
    
    def _escape_label(self, text: str) -> str:
        """Escape text for DOT labels."""
        return text.replace('"', '\\"').replace('\\', '\\\\')
    
    def _truncate_label(self, text: str) -> str:
        """Truncate text to maximum label length."""
        if len(text) <= self.max_label_length:
            return text
        return text[:self.max_label_length - 3] + "..."
    
    def _add_metadata_comments(self, content: str, inventory: ResourceInventory) -> str:
        """Add metadata as comments to the DOT file."""
        comments = []
        comments.append("/* CloudViz Generated DOT Diagram */")
        comments.append(f"/* Generated at: {inventory.extraction_time.isoformat()} */")
        comments.append(f"/* Resource count: {len(inventory.resources)} */")
        comments.append(f"/* Relationship count: {len(inventory.relationships)} */")
        
        if inventory.provider:
            comments.append(f"/* Provider: {inventory.provider.value} */")
        
        if inventory.extraction_scope:
            comments.append(f"/* Scope: {inventory.extraction_scope.value} */")
            if inventory.scope_identifier:
                comments.append(f"/* Scope ID: {inventory.scope_identifier} */")
        
        comments.append("")
        
        return "\n".join(comments) + "\n" + content
    
    def get_supported_formats(self) -> List[str]:
        """Get supported output formats."""
        return self.supported_formats
    
    def get_available_themes(self) -> List[str]:
        """Get available themes."""
        return self.supported_themes
    
    def get_available_layouts(self) -> List[str]:
        """Get available layouts."""
        return self.supported_layouts
