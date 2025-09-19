"""
Image rendering engine for CloudViz.
Converts diagrams to image formats (PNG, SVG) using external tools.
"""

import json
import os
import subprocess
import tempfile
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from cloudviz.core.base import VisualizationEngine
from cloudviz.core.models import ResourceInventory
from cloudviz.core.utils import get_logger, LoggerMixin


class ImageEngine(VisualizationEngine, LoggerMixin):
    """
    Image rendering engine for generating PNG/SVG from diagram sources.
    Supports rendering from Mermaid and Graphviz DOT sources.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Image engine."""
        super().__init__(config)
        self.supported_formats = ['png', 'svg', 'pdf', 'jpg', 'jpeg']
        self.supported_themes = ['professional', 'dark', 'light', 'minimal', 'colorful']
        self.supported_layouts = ['hierarchical', 'circular', 'force', 'grid', 'radial']
        
        # Tool paths and options
        self.graphviz_path = self.config.get('graphviz_path', 'dot')
        self.mermaid_cli_path = self.config.get('mermaid_cli_path', 'mmdc')
        self.puppeteer_config = self.config.get('puppeteer_config', {})
        
        # Image options
        self.dpi = self.config.get('dpi', 300)
        self.width = self.config.get('width', None)
        self.height = self.config.get('height', None)
        self.background_color = self.config.get('background_color', 'white')
        self.quality = self.config.get('quality', 95)  # For JPEG
        
        # Rendering engines
        self.mermaid_engine = None
        self.graphviz_engine = None
    
    async def render(
        self,
        inventory: ResourceInventory,
        output_format: str = 'png',
        theme: Optional[str] = None,
        layout: Optional[str] = None,
        **kwargs
    ) -> bytes:
        """
        Render resource inventory as image.
        
        Args:
            inventory: Resource inventory to visualize
            output_format: Output format (png, svg, pdf, jpg, jpeg)
            theme: Visual theme
            layout: Layout algorithm
            **kwargs: Additional rendering parameters
            
        Returns:
            bytes: Image data
        """
        self.log_info("Rendering image diagram",
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
        
        # Choose rendering path based on preferred source format
        source_format = kwargs.get('source_format', 'auto')
        
        try:
            if source_format == 'mermaid' or (source_format == 'auto' and self._should_use_mermaid(layout)):
                return await self._render_from_mermaid(inventory, output_format, theme, layout, **kwargs)
            else:
                return await self._render_from_graphviz(inventory, output_format, theme, layout, **kwargs)
                
        except Exception as e:
            self.log_error("Failed to render image diagram", exc_info=True, error=str(e))
            raise
    
    async def _render_from_mermaid(
        self,
        inventory: ResourceInventory,
        output_format: str,
        theme: str,
        layout: str,
        **kwargs
    ) -> bytes:
        """Render image from Mermaid source."""
        # Check if Mermaid CLI is available
        if not await self._check_mermaid_cli():
            raise RuntimeError("Mermaid CLI (mmdc) not found. Please install @mermaid-js/mermaid-cli")
        
        # Generate Mermaid source
        if not self.mermaid_engine:
            from cloudviz.visualization.engines.mermaid import MermaidEngine
            self.mermaid_engine = MermaidEngine(self.config)
        
        mermaid_source = await self.mermaid_engine.render(
            inventory, 'mermaid', theme, layout, **kwargs
        )
        
        # Create temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_file = temp_path / "diagram.mmd"
            output_file = temp_path / f"diagram.{output_format}"
            
            # Write Mermaid source
            input_file.write_bytes(mermaid_source)
            
            # Build mmdc command
            cmd = [
                self.mermaid_cli_path,
                '-i', str(input_file),
                '-o', str(output_file),
                '-f', output_format
            ]
            
            # Add theme
            if theme:
                mermaid_theme = self._map_theme_to_mermaid(theme)
                cmd.extend(['-t', mermaid_theme])
            
            # Add dimensions
            if self.width:
                cmd.extend(['-w', str(self.width)])
            if self.height:
                cmd.extend(['-H', str(self.height)])
            
            # Add background
            if self.background_color and self.background_color != 'transparent':
                cmd.extend(['-b', self.background_color])
            
            # Add puppeteer config
            if self.puppeteer_config:
                config_file = temp_path / "puppeteer-config.json"
                config_file.write_text(json.dumps(self.puppeteer_config))
                cmd.extend(['-p', str(config_file)])
            
            # Execute command
            self.log_debug("Executing Mermaid CLI command", command=' '.join(cmd))
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    check=True
                )
                
                if result.stderr:
                    self.log_warning("Mermaid CLI warnings", stderr=result.stderr)
                
                # Read output file
                if output_file.exists():
                    image_data = output_file.read_bytes()
                    self.log_info("Mermaid image rendered successfully", size=len(image_data))
                    return image_data
                else:
                    raise RuntimeError("Mermaid CLI did not generate output file")
                    
            except subprocess.TimeoutExpired:
                raise RuntimeError("Mermaid CLI execution timed out")
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Mermaid CLI failed: {e.stderr}")
    
    async def _render_from_graphviz(
        self,
        inventory: ResourceInventory,
        output_format: str,
        theme: str,
        layout: str,
        **kwargs
    ) -> bytes:
        """Render image from Graphviz DOT source."""
        # Check if Graphviz is available
        if not await self._check_graphviz():
            raise RuntimeError("Graphviz not found. Please install Graphviz")
        
        # Generate DOT source
        if not self.graphviz_engine:
            from cloudviz.visualization.engines.graphviz import GraphvizEngine
            self.graphviz_engine = GraphvizEngine(self.config)
        
        dot_source = await self.graphviz_engine.render(
            inventory, 'dot', theme, layout, **kwargs
        )
        
        # Create temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_file = temp_path / "diagram.dot"
            output_file = temp_path / f"diagram.{output_format}"
            
            # Write DOT source
            input_file.write_bytes(dot_source)
            
            # Choose Graphviz tool based on layout
            tool = self._get_graphviz_tool(layout)
            
            # Build command
            cmd = [
                tool,
                f'-T{output_format}',
                '-o', str(output_file),
                str(input_file)
            ]
            
            # Add DPI for raster formats
            if output_format.lower() in ['png', 'jpg', 'jpeg']:
                cmd.insert(1, f'-Gdpi={self.dpi}')
            
            # Add size constraints
            if self.width or self.height:
                size_parts = []
                if self.width:
                    size_parts.append(str(self.width / self.dpi))
                if self.height:
                    size_parts.append(str(self.height / self.dpi))
                size_str = ','.join(size_parts)
                cmd.insert(1, f'-Gsize={size_str}')
            
            # Add background color
            if self.background_color and self.background_color != 'transparent':
                cmd.insert(1, f'-Gbgcolor={self.background_color}')
            
            # Execute command
            self.log_debug("Executing Graphviz command", command=' '.join(cmd))
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    check=True
                )
                
                if result.stderr:
                    self.log_warning("Graphviz warnings", stderr=result.stderr)
                
                # Read output file
                if output_file.exists():
                    image_data = output_file.read_bytes()
                    self.log_info("Graphviz image rendered successfully", size=len(image_data))
                    return image_data
                else:
                    raise RuntimeError("Graphviz did not generate output file")
                    
            except subprocess.TimeoutExpired:
                raise RuntimeError("Graphviz execution timed out")
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Graphviz failed: {e.stderr}")
    
    async def _check_mermaid_cli(self) -> bool:
        """Check if Mermaid CLI is available."""
        try:
            result = subprocess.run(
                [self.mermaid_cli_path, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    async def _check_graphviz(self) -> bool:
        """Check if Graphviz is available."""
        try:
            result = subprocess.run(
                [self.graphviz_path, '-V'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _should_use_mermaid(self, layout: str) -> bool:
        """Determine if Mermaid should be preferred for the layout."""
        # Mermaid is better for hierarchical and flowchart layouts
        return layout in ['hierarchical', 'flowchart', 'mindmap', 'timeline']
    
    def _map_theme_to_mermaid(self, theme: str) -> str:
        """Map CloudViz theme to Mermaid theme."""
        theme_map = {
            'professional': 'default',
            'dark': 'dark',
            'light': 'base',
            'minimal': 'neutral',
            'colorful': 'forest'
        }
        return theme_map.get(theme, 'default')
    
    def _get_graphviz_tool(self, layout: str) -> str:
        """Get appropriate Graphviz tool for layout."""
        tool_map = {
            'hierarchical': 'dot',
            'circular': 'circo',
            'force': 'fdp',
            'grid': 'neato',
            'radial': 'twopi'
        }
        return tool_map.get(layout, 'dot')
    
    async def render_from_source(
        self,
        source: Union[str, bytes],
        source_format: str,
        output_format: str = 'png',
        **kwargs
    ) -> bytes:
        """
        Render image from diagram source.
        
        Args:
            source: Diagram source (Mermaid or DOT)
            source_format: Source format ('mermaid' or 'dot')
            output_format: Output image format
            **kwargs: Additional rendering parameters
            
        Returns:
            bytes: Image data
        """
        self.log_info("Rendering image from source",
                     source_format=source_format,
                     output_format=output_format)
        
        if isinstance(source, str):
            source = source.encode('utf-8')
        
        if source_format.lower() in ['mermaid', 'mmd']:
            return await self._render_source_with_mermaid(source, output_format, **kwargs)
        elif source_format.lower() in ['dot', 'gv', 'graphviz']:
            return await self._render_source_with_graphviz(source, output_format, **kwargs)
        else:
            raise ValueError(f"Unsupported source format: {source_format}")
    
    async def _render_source_with_mermaid(
        self,
        source: bytes,
        output_format: str,
        **kwargs
    ) -> bytes:
        """Render image from Mermaid source."""
        if not await self._check_mermaid_cli():
            raise RuntimeError("Mermaid CLI (mmdc) not found")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_file = temp_path / "diagram.mmd"
            output_file = temp_path / f"diagram.{output_format}"
            
            input_file.write_bytes(source)
            
            cmd = [
                self.mermaid_cli_path,
                '-i', str(input_file),
                '-o', str(output_file),
                '-f', output_format
            ]
            
            # Add optional parameters
            theme = kwargs.get('theme')
            if theme:
                mermaid_theme = self._map_theme_to_mermaid(theme)
                cmd.extend(['-t', mermaid_theme])
            
            width = kwargs.get('width', self.width)
            if width:
                cmd.extend(['-w', str(width)])
            
            height = kwargs.get('height', self.height)
            if height:
                cmd.extend(['-H', str(height)])
            
            background = kwargs.get('background_color', self.background_color)
            if background and background != 'transparent':
                cmd.extend(['-b', background])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=True)
            
            if output_file.exists():
                return output_file.read_bytes()
            else:
                raise RuntimeError("Mermaid CLI did not generate output file")
    
    async def _render_source_with_graphviz(
        self,
        source: bytes,
        output_format: str,
        **kwargs
    ) -> bytes:
        """Render image from Graphviz DOT source."""
        if not await self._check_graphviz():
            raise RuntimeError("Graphviz not found")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_file = temp_path / "diagram.dot"
            output_file = temp_path / f"diagram.{output_format}"
            
            input_file.write_bytes(source)
            
            layout = kwargs.get('layout', 'dot')
            tool = self._get_graphviz_tool(layout)
            
            cmd = [
                tool,
                f'-T{output_format}',
                '-o', str(output_file),
                str(input_file)
            ]
            
            # Add DPI for raster formats
            if output_format.lower() in ['png', 'jpg', 'jpeg']:
                dpi = kwargs.get('dpi', self.dpi)
                cmd.insert(1, f'-Gdpi={dpi}')
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=True)
            
            if output_file.exists():
                return output_file.read_bytes()
            else:
                raise RuntimeError("Graphviz did not generate output file")
    
    def get_supported_formats(self) -> List[str]:
        """Get supported output formats."""
        return self.supported_formats
    
    def get_available_themes(self) -> List[str]:
        """Get available themes."""
        return self.supported_themes
    
    def get_available_layouts(self) -> List[str]:
        """Get available layouts."""
        return self.supported_layouts
