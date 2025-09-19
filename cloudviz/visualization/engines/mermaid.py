"""
Mermaid diagram engine for CloudViz.
Generates Mermaid markdown diagrams for cloud infrastructure visualization.
"""

import json
from typing import Dict, List, Optional, Any, Set
from cloudviz.core.base import VisualizationEngine
from cloudviz.core.models import ResourceInventory, CloudResource, ResourceRelationship, RelationshipType
from cloudviz.core.utils import get_logger, LoggerMixin


class MermaidEngine(VisualizationEngine, LoggerMixin):
    """
    Mermaid diagram generation engine.
    Creates Mermaid markdown diagrams for cloud infrastructure visualization.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Mermaid engine."""
        super().__init__(config)
        self.supported_formats = ['mermaid', 'md']
        self.supported_themes = ['professional', 'dark', 'light', 'minimal', 'colorful']
        self.supported_layouts = ['hierarchical', 'flowchart', 'graph', 'mindmap', 'timeline']
        
        # Mermaid configuration
        self.node_id_counter = 0
        self.node_id_map = {}
        self.max_label_length = self.config.get('max_label_length', 20)
        self.include_resource_types = self.config.get('include_resource_types', True)
        self.include_regions = self.config.get('include_regions', True)
        self.group_by_resource_group = self.config.get('group_by_resource_group', True)
        self.show_relationships = self.config.get('show_relationships', True)
    
    async def render(
        self,
        inventory: ResourceInventory,
        output_format: str = 'mermaid',
        theme: Optional[str] = None,
        layout: Optional[str] = None,
        **kwargs
    ) -> bytes:
        """
        Render resource inventory as Mermaid diagram.
        
        Args:
            inventory: Resource inventory to visualize
            output_format: Output format (mermaid, md)
            theme: Visual theme
            layout: Layout algorithm
            **kwargs: Additional rendering parameters
            
        Returns:
            bytes: Mermaid diagram as UTF-8 encoded bytes
        """
        self.log_info("Rendering Mermaid diagram",
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
        
        # Reset state
        self.node_id_counter = 0
        self.node_id_map = {}
        
        try:
            # Generate diagram based on layout
            if layout == 'hierarchical':
                diagram = self._generate_hierarchical_diagram(inventory, theme, **kwargs)
            elif layout == 'flowchart':
                diagram = self._generate_flowchart_diagram(inventory, theme, **kwargs)
            elif layout == 'graph':
                diagram = self._generate_graph_diagram(inventory, theme, **kwargs)
            elif layout == 'mindmap':
                diagram = self._generate_mindmap_diagram(inventory, theme, **kwargs)
            elif layout == 'timeline':
                diagram = self._generate_timeline_diagram(inventory, theme, **kwargs)
            else:
                raise ValueError(f"Unsupported layout: {layout}")
            
            # Apply theme styling
            diagram = self._apply_theme_styling(diagram, theme)
            
            # Add metadata as comments
            diagram = self._add_metadata_comments(diagram, inventory)
            
            self.log_info("Mermaid diagram generated successfully",
                         diagram_length=len(diagram))
            
            return diagram.encode('utf-8')
            
        except Exception as e:
            self.log_error("Failed to render Mermaid diagram", exc_info=True, error=str(e))
            raise
    
    def _generate_hierarchical_diagram(
        self,
        inventory: ResourceInventory,
        theme: str,
        **kwargs
    ) -> str:
        """Generate hierarchical Mermaid diagram."""
        lines = []
        
        # Start with flowchart
        direction = kwargs.get('direction', 'TD')
        lines.append(f"flowchart {direction}")
        
        # Group resources by resource group
        if self.group_by_resource_group:
            resource_groups = self._group_resources_by_resource_group(inventory.resources)
            
            for rg_name, resources in resource_groups.items():
                if rg_name and resources:
                    # Create resource group subgraph
                    rg_id = self._get_node_id(f"rg_{rg_name}")
                    lines.append(f"    subgraph {rg_id}[\"{rg_name}\"]")
                    
                    # Add resources in this resource group
                    for resource in resources:
                        node_def = self._create_resource_node(resource, theme, indent="        ")
                        lines.append(node_def)
                    
                    lines.append("    end")
        else:
            # Add all resources without grouping
            for resource in inventory.resources:
                node_def = self._create_resource_node(resource, theme, indent="    ")
                lines.append(node_def)
        
        # Add relationships
        if self.show_relationships and inventory.relationships:
            lines.append("")
            lines.append("    %% Relationships")
            for relationship in inventory.relationships:
                rel_def = self._create_relationship_edge(relationship)
                if rel_def:
                    lines.append(f"    {rel_def}")
        
        return "\n".join(lines)
    
    def _generate_flowchart_diagram(
        self,
        inventory: ResourceInventory,
        theme: str,
        **kwargs
    ) -> str:
        """Generate flowchart Mermaid diagram."""
        lines = []
        
        # Start with flowchart
        direction = kwargs.get('direction', 'LR')
        lines.append(f"flowchart {direction}")
        
        # Add nodes
        for resource in inventory.resources:
            node_def = self._create_resource_node(resource, theme, indent="    ")
            lines.append(node_def)
        
        # Add relationships
        if self.show_relationships and inventory.relationships:
            lines.append("")
            lines.append("    %% Relationships")
            for relationship in inventory.relationships:
                rel_def = self._create_relationship_edge(relationship)
                if rel_def:
                    lines.append(f"    {rel_def}")
        
        return "\n".join(lines)
    
    def _generate_graph_diagram(
        self,
        inventory: ResourceInventory,
        theme: str,
        **kwargs
    ) -> str:
        """Generate graph Mermaid diagram."""
        lines = []
        
        # Start with graph
        lines.append("graph TD")
        
        # Add nodes
        for resource in inventory.resources:
            node_def = self._create_resource_node(resource, theme, indent="    ", style="graph")
            lines.append(node_def)
        
        # Add relationships
        if self.show_relationships and inventory.relationships:
            lines.append("")
            lines.append("    %% Relationships")
            for relationship in inventory.relationships:
                rel_def = self._create_relationship_edge(relationship, style="graph")
                if rel_def:
                    lines.append(f"    {rel_def}")
        
        return "\n".join(lines)
    
    def _generate_mindmap_diagram(
        self,
        inventory: ResourceInventory,
        theme: str,
        **kwargs
    ) -> str:
        """Generate mindmap Mermaid diagram."""
        lines = []
        
        # Start with mindmap
        lines.append("mindmap")
        lines.append("  root((Cloud Infrastructure))")
        
        # Group by resource groups
        resource_groups = self._group_resources_by_resource_group(inventory.resources)
        
        for rg_name, resources in resource_groups.items():
            if rg_name and resources:
                lines.append(f"    {rg_name}")
                
                # Group by resource type
                by_type = {}
                for resource in resources:
                    res_type = resource.get_category()
                    if res_type not in by_type:
                        by_type[res_type] = []
                    by_type[res_type].append(resource)
                
                for res_type, type_resources in by_type.items():
                    lines.append(f"      {res_type}")
                    for resource in type_resources[:5]:  # Limit to 5 per type
                        short_name = self._truncate_label(resource.name)
                        lines.append(f"        {short_name}")
        
        return "\n".join(lines)
    
    def _generate_timeline_diagram(
        self,
        inventory: ResourceInventory,
        theme: str,
        **kwargs
    ) -> str:
        """Generate timeline Mermaid diagram."""
        lines = []
        
        # Start with timeline
        lines.append("timeline")
        lines.append("    title Resource Creation Timeline")
        
        # Sort resources by creation date
        dated_resources = [r for r in inventory.resources if r.created_time]
        dated_resources.sort(key=lambda x: x.created_time)
        
        # Group by date
        by_date = {}
        for resource in dated_resources:
            date_key = resource.created_time.strftime("%Y-%m-%d")
            if date_key not in by_date:
                by_date[date_key] = []
            by_date[date_key].append(resource)
        
        for date, resources in by_date.items():
            lines.append(f"    {date}")
            for resource in resources[:3]:  # Limit to 3 per date
                short_name = self._truncate_label(resource.name)
                lines.append(f"        {short_name} : {resource.get_category()}")
        
        return "\n".join(lines)
    
    def _create_resource_node(
        self,
        resource: CloudResource,
        theme: str,
        indent: str = "    ",
        style: str = "flowchart"
    ) -> str:
        """Create Mermaid node definition for a resource."""
        node_id = self._get_node_id(resource.id)
        
        # Create display label
        label = self._create_resource_label(resource)
        
        # Choose node shape based on resource type
        shape = self._get_node_shape(resource, style)
        
        # Create node definition
        if style == "graph":
            return f"{indent}{node_id}[{label}]"
        else:
            return f"{indent}{node_id}{shape}"
    
    def _create_resource_label(self, resource: CloudResource) -> str:
        """Create display label for a resource."""
        parts = []
        
        # Resource name
        name = self._truncate_label(resource.name)
        parts.append(name)
        
        # Add resource type if enabled
        if self.include_resource_types:
            res_type = resource.get_category()
            parts.append(f"({res_type})")
        
        # Add region if enabled
        if self.include_regions and resource.region:
            parts.append(f"[{resource.region}]")
        
        return "<br/>".join(parts)
    
    def _get_node_shape(self, resource: CloudResource, style: str) -> str:
        """Get Mermaid node shape based on resource type."""
        label = self._create_resource_label(resource)
        
        # Map resource categories to shapes
        category = resource.get_category()
        
        if style == "flowchart":
            shape_map = {
                'Compute': f'["{label}"]',
                'Storage': f'[("{label}")]',
                'Networking': f'{{"{label}"}}',
                'Database': f'[("{label}")]',
                'Security': f'{{{{"{label}"}}}}',
                'Management': f'[("{label}")]',
                'Other': f'["{label}"]'
            }
        else:
            shape_map = {
                'Compute': f'[{label}]',
                'Storage': f'({label})',
                'Networking': f'{{{label}}}',
                'Database': f'({label})',
                'Security': f'{{{{{label}}}}}',
                'Management': f'({label})',
                'Other': f'[{label}]'
            }
        
        return shape_map.get(category, f'["{label}"]')
    
    def _create_relationship_edge(
        self,
        relationship: ResourceRelationship,
        style: str = "flowchart"
    ) -> Optional[str]:
        """Create Mermaid edge definition for a relationship."""
        source_id = self._get_existing_node_id(relationship.source_id)
        target_id = self._get_existing_node_id(relationship.target_id)
        
        if not source_id or not target_id:
            return None
        
        # Choose edge style based on relationship type
        edge_style = self._get_edge_style(relationship.relationship_type)
        
        # Create edge label
        label = relationship.get_edge_label()
        
        if label and len(label) < 20:
            return f"{source_id} {edge_style}|{label}| {target_id}"
        else:
            return f"{source_id} {edge_style} {target_id}"
    
    def _get_edge_style(self, relationship_type: RelationshipType) -> str:
        """Get Mermaid edge style for relationship type."""
        style_map = {
            RelationshipType.CONTAINS: "-->",
            RelationshipType.CONNECTS_TO: "-.->",
            RelationshipType.DEPENDS_ON: "==>",
            RelationshipType.MANAGED_BY: "-->",
            RelationshipType.SECURED_BY: "-.->",
            RelationshipType.ROUTES_TO: "-.->",
            RelationshipType.REPLICATES_TO: "==>",
            RelationshipType.BACKS_UP_TO: "==>"
        }
        return style_map.get(relationship_type, "-->")
    
    def _apply_theme_styling(self, diagram: str, theme: str) -> str:
        """Apply theme-specific styling to the diagram."""
        theme_styles = {
            'professional': self._get_professional_theme_styles(),
            'dark': self._get_dark_theme_styles(),
            'light': self._get_light_theme_styles(),
            'minimal': self._get_minimal_theme_styles(),
            'colorful': self._get_colorful_theme_styles()
        }
        
        styles = theme_styles.get(theme, theme_styles['professional'])
        
        # Add styling to diagram
        if styles:
            diagram += "\n\n" + styles
        
        return diagram
    
    def _get_professional_theme_styles(self) -> str:
        """Get professional theme styling."""
        return """    %% Professional theme styling
    classDef compute fill:#0078d4,stroke:#005a9e,stroke-width:2px,color:#fff
    classDef storage fill:#00bcf2,stroke:#0082a6,stroke-width:2px,color:#fff
    classDef network fill:#7fba00,stroke:#5c8a00,stroke-width:2px,color:#fff
    classDef database fill:#ff6c00,stroke:#cc5500,stroke-width:2px,color:#fff
    classDef security fill:#5c2d91,stroke:#4a2574,stroke-width:2px,color:#fff
    classDef management fill:#68217a,stroke:#531968,stroke-width:2px,color:#fff"""
    
    def _get_dark_theme_styles(self) -> str:
        """Get dark theme styling."""
        return """    %% Dark theme styling
    classDef compute fill:#2d3748,stroke:#4a5568,stroke-width:2px,color:#e2e8f0
    classDef storage fill:#2c5282,stroke:#3182ce,stroke-width:2px,color:#e2e8f0
    classDef network fill:#276749,stroke:#38a169,stroke-width:2px,color:#e2e8f0
    classDef database fill:#9c4221,stroke:#dd6b20,stroke-width:2px,color:#e2e8f0
    classDef security fill:#553c9a,stroke:#805ad5,stroke-width:2px,color:#e2e8f0
    classDef management fill:#702459,stroke:#d53f8c,stroke-width:2px,color:#e2e8f0"""
    
    def _get_light_theme_styles(self) -> str:
        """Get light theme styling."""
        return """    %% Light theme styling
    classDef compute fill:#ebf8ff,stroke:#3182ce,stroke-width:2px,color:#2c5282
    classDef storage fill:#e6fffa,stroke:#38b2ac,stroke-width:2px,color:#285e61
    classDef network fill:#f0fff4,stroke:#38a169,stroke-width:2px,color:#276749
    classDef database fill:#fffaf0,stroke:#dd6b20,stroke-width:2px,color:#9c4221
    classDef security fill:#faf5ff,stroke:#805ad5,stroke-width:2px,color:#553c9a
    classDef management fill:#fdf2f8,stroke:#d53f8c,stroke-width:2px,color:#702459"""
    
    def _get_minimal_theme_styles(self) -> str:
        """Get minimal theme styling."""
        return """    %% Minimal theme styling
    classDef default fill:#f9f9f9,stroke:#d1d5db,stroke-width:1px,color:#374151"""
    
    def _get_colorful_theme_styles(self) -> str:
        """Get colorful theme styling."""
        return """    %% Colorful theme styling
    classDef compute fill:#ff6b6b,stroke:#ee5a52,stroke-width:2px,color:#fff
    classDef storage fill:#4ecdc4,stroke:#45b7b8,stroke-width:2px,color:#fff
    classDef network fill:#45b7d1,stroke:#3498db,stroke-width:2px,color:#fff
    classDef database fill:#f9ca24,stroke:#f0932b,stroke-width:2px,color:#fff
    classDef security fill:#6c5ce7,stroke:#a29bfe,stroke-width:2px,color:#fff
    classDef management fill:#fd79a8,stroke:#e84393,stroke-width:2px,color:#fff"""
    
    def _add_metadata_comments(self, diagram: str, inventory: ResourceInventory) -> str:
        """Add metadata as comments to the diagram."""
        comments = []
        comments.append("%% CloudViz Generated Diagram")
        comments.append(f"%% Generated at: {inventory.extraction_time.isoformat()}")
        comments.append(f"%% Resource count: {len(inventory.resources)}")
        comments.append(f"%% Relationship count: {len(inventory.relationships)}")
        
        if inventory.provider:
            comments.append(f"%% Provider: {inventory.provider.value}")
        
        if inventory.extraction_scope:
            comments.append(f"%% Scope: {inventory.extraction_scope.value}")
            if inventory.scope_identifier:
                comments.append(f"%% Scope ID: {inventory.scope_identifier}")
        
        comments.append("")
        
        return "\n".join(comments) + diagram
    
    def _group_resources_by_resource_group(
        self,
        resources: List[CloudResource]
    ) -> Dict[str, List[CloudResource]]:
        """Group resources by resource group."""
        groups = {}
        
        for resource in resources:
            rg_name = resource.resource_group or "No Resource Group"
            if rg_name not in groups:
                groups[rg_name] = []
            groups[rg_name].append(resource)
        
        return groups
    
    def _get_node_id(self, resource_id: str) -> str:
        """Get or create a node ID for a resource."""
        if resource_id not in self.node_id_map:
            self.node_id_counter += 1
            self.node_id_map[resource_id] = f"node{self.node_id_counter}"
        
        return self.node_id_map[resource_id]
    
    def _get_existing_node_id(self, resource_id: str) -> Optional[str]:
        """Get existing node ID for a resource."""
        return self.node_id_map.get(resource_id)
    
    def _truncate_label(self, text: str) -> str:
        """Truncate text to maximum label length."""
        if len(text) <= self.max_label_length:
            return text
        return text[:self.max_label_length - 3] + "..."
    
    def get_supported_formats(self) -> List[str]:
        """Get supported output formats."""
        return self.supported_formats
    
    def get_available_themes(self) -> List[str]:
        """Get available themes."""
        return self.supported_themes
    
    def get_available_layouts(self) -> List[str]:
        """Get available layouts."""
        return self.supported_layouts
