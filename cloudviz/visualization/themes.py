"""
Theme management for CloudViz visualizations.
Provides consistent styling across different visualization engines.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from cloudviz.core.utils import LoggerMixin


@dataclass
class ColorPalette:
    """Color palette for themes."""
    primary: str
    secondary: str
    accent: str
    background: str
    foreground: str
    success: str
    warning: str
    error: str
    info: str
    
    # Resource type colors
    compute: str = field(default="")
    storage: str = field(default="")
    networking: str = field(default="")
    database: str = field(default="")
    security: str = field(default="")
    management: str = field(default="")
    other: str = field(default="")
    
    def __post_init__(self):
        """Set default resource colors if not provided."""
        if not self.compute:
            self.compute = self.primary
        if not self.storage:
            self.storage = self.secondary
        if not self.networking:
            self.networking = self.accent
        if not self.database:
            self.database = self.warning
        if not self.security:
            self.security = self.error
        if not self.management:
            self.management = self.info
        if not self.other:
            self.other = self.foreground


@dataclass
class Typography:
    """Typography settings for themes."""
    font_family: str = "Arial, sans-serif"
    font_size: int = 10
    font_size_small: int = 8
    font_size_large: int = 12
    font_weight: str = "normal"
    font_weight_bold: str = "bold"
    line_height: float = 1.2


@dataclass
class Spacing:
    """Spacing settings for themes."""
    node_sep: float = 0.5
    rank_sep: float = 0.5
    margin: float = 0.2
    padding: float = 0.1


@dataclass
class ThemeConfig:
    """Complete theme configuration."""
    name: str
    display_name: str
    description: str
    colors: ColorPalette
    typography: Typography = field(default_factory=Typography)
    spacing: Spacing = field(default_factory=Spacing)
    custom_properties: Dict[str, Any] = field(default_factory=dict)


class BaseTheme(ABC, LoggerMixin):
    """Base class for visualization themes."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize theme."""
        self.config = config or {}
        self._theme_config = None
    
    @property
    @abstractmethod
    def theme_config(self) -> ThemeConfig:
        """Get theme configuration."""
        pass
    
    @abstractmethod
    def get_mermaid_styles(self) -> str:
        """Get Mermaid-specific styling."""
        pass
    
    @abstractmethod
    def get_graphviz_styles(self) -> Dict[str, str]:
        """Get Graphviz-specific styling."""
        pass
    
    def get_resource_color(self, resource_category: str) -> str:
        """Get color for a resource category."""
        colors = self.theme_config.colors
        
        category_map = {
            'Compute': colors.compute,
            'Storage': colors.storage,
            'Networking': colors.networking,
            'Database': colors.database,
            'Security': colors.security,
            'Management': colors.management,
            'Other': colors.other
        }
        
        return category_map.get(resource_category, colors.other)
    
    def get_relationship_color(self, relationship_type: str) -> str:
        """Get color for a relationship type."""
        colors = self.theme_config.colors
        
        # Map relationship types to semantic colors
        type_map = {
            'CONTAINS': colors.primary,
            'CONNECTS_TO': colors.accent,
            'DEPENDS_ON': colors.warning,
            'MANAGED_BY': colors.secondary,
            'SECURED_BY': colors.error,
            'ROUTES_TO': colors.success,
            'REPLICATES_TO': colors.info,
            'BACKS_UP_TO': colors.info
        }
        
        return type_map.get(relationship_type, colors.foreground)


class ProfessionalTheme(BaseTheme):
    """Professional Microsoft-style theme."""
    
    @property
    def theme_config(self) -> ThemeConfig:
        """Get professional theme configuration."""
        if self._theme_config is None:
            colors = ColorPalette(
                primary="#0078d4",
                secondary="#00bcf2", 
                accent="#7fba00",
                background="#ffffff",
                foreground="#323130",
                success="#107c10",
                warning="#ff8c00",
                error="#d13438",
                info="#5c2d91",
                compute="#0078d4",
                storage="#00bcf2",
                networking="#7fba00",
                database="#ff6c00",
                security="#5c2d91",
                management="#68217a",
                other="#737373"
            )
            
            typography = Typography(
                font_family="'Segoe UI', Arial, sans-serif",
                font_size=10,
                font_size_small=8,
                font_size_large=12
            )
            
            self._theme_config = ThemeConfig(
                name="professional",
                display_name="Professional",
                description="Clean Microsoft-style professional theme",
                colors=colors,
                typography=typography
            )
        
        return self._theme_config
    
    def get_mermaid_styles(self) -> str:
        """Get Mermaid professional styling."""
        colors = self.theme_config.colors
        
        return f"""    %% Professional theme styling
    classDef compute fill:{colors.compute},stroke:#005a9e,stroke-width:2px,color:#fff
    classDef storage fill:{colors.storage},stroke:#0082a6,stroke-width:2px,color:#fff
    classDef network fill:{colors.networking},stroke:#5c8a00,stroke-width:2px,color:#fff
    classDef database fill:{colors.database},stroke:#cc5500,stroke-width:2px,color:#fff
    classDef security fill:{colors.security},stroke:#4a2574,stroke-width:2px,color:#fff
    classDef management fill:{colors.management},stroke:#531968,stroke-width:2px,color:#fff
    classDef default fill:{colors.background},stroke:{colors.foreground},stroke-width:1px,color:{colors.foreground}"""
    
    def get_graphviz_styles(self) -> Dict[str, str]:
        """Get Graphviz professional styling."""
        colors = self.theme_config.colors
        typography = self.theme_config.typography
        
        return {
            'graph': {
                'bgcolor': colors.background,
                'fontname': typography.font_family,
                'fontsize': str(typography.font_size),
                'fontcolor': colors.foreground
            },
            'node': {
                'fontname': typography.font_family,
                'fontsize': str(typography.font_size),
                'style': 'rounded,filled',
                'fillcolor': colors.background,
                'color': colors.foreground,
                'fontcolor': colors.foreground
            },
            'edge': {
                'fontname': typography.font_family,
                'fontsize': str(typography.font_size - 1),
                'color': colors.foreground,
                'fontcolor': colors.foreground
            }
        }


class DarkTheme(BaseTheme):
    """Dark theme for low-light environments."""
    
    @property
    def theme_config(self) -> ThemeConfig:
        """Get dark theme configuration."""
        if self._theme_config is None:
            colors = ColorPalette(
                primary="#4fc3f7",
                secondary="#81c784",
                accent="#ffb74d",
                background="#1a202c",
                foreground="#e2e8f0",
                success="#4caf50",
                warning="#ff9800",
                error="#f44336",
                info="#2196f3",
                compute="#2d3748",
                storage="#2c5282",
                networking="#276749",
                database="#9c4221",
                security="#553c9a",
                management="#702459",
                other="#4a5568"
            )
            
            typography = Typography(
                font_family="'Segoe UI', Arial, sans-serif",
                font_size=10
            )
            
            self._theme_config = ThemeConfig(
                name="dark",
                display_name="Dark",
                description="Dark theme for low-light environments",
                colors=colors,
                typography=typography
            )
        
        return self._theme_config
    
    def get_mermaid_styles(self) -> str:
        """Get Mermaid dark styling."""
        colors = self.theme_config.colors
        
        return f"""    %% Dark theme styling
    classDef compute fill:{colors.compute},stroke:#4a5568,stroke-width:2px,color:{colors.foreground}
    classDef storage fill:{colors.storage},stroke:#3182ce,stroke-width:2px,color:{colors.foreground}
    classDef network fill:{colors.networking},stroke:#38a169,stroke-width:2px,color:{colors.foreground}
    classDef database fill:{colors.database},stroke:#dd6b20,stroke-width:2px,color:{colors.foreground}
    classDef security fill:{colors.security},stroke:#805ad5,stroke-width:2px,color:{colors.foreground}
    classDef management fill:{colors.management},stroke:#d53f8c,stroke-width:2px,color:{colors.foreground}
    classDef default fill:{colors.background},stroke:{colors.foreground},stroke-width:1px,color:{colors.foreground}"""
    
    def get_graphviz_styles(self) -> Dict[str, str]:
        """Get Graphviz dark styling."""
        colors = self.theme_config.colors
        typography = self.theme_config.typography
        
        return {
            'graph': {
                'bgcolor': colors.background,
                'fontname': typography.font_family,
                'fontsize': str(typography.font_size),
                'fontcolor': colors.foreground
            },
            'node': {
                'fontname': typography.font_family,
                'fontsize': str(typography.font_size),
                'style': 'rounded,filled',
                'fillcolor': colors.compute,
                'color': colors.foreground,
                'fontcolor': colors.foreground
            },
            'edge': {
                'fontname': typography.font_family,
                'fontsize': str(typography.font_size - 1),
                'color': colors.foreground,
                'fontcolor': colors.foreground
            }
        }


class LightTheme(BaseTheme):
    """Light theme with pastel colors."""
    
    @property
    def theme_config(self) -> ThemeConfig:
        """Get light theme configuration."""
        if self._theme_config is None:
            colors = ColorPalette(
                primary="#3182ce",
                secondary="#38b2ac",
                accent="#38a169",
                background="#ffffff",
                foreground="#2d3748",
                success="#38a169",
                warning="#dd6b20",
                error="#e53e3e",
                info="#3182ce",
                compute="#ebf8ff",
                storage="#e6fffa",
                networking="#f0fff4",
                database="#fffaf0",
                security="#faf5ff",
                management="#fdf2f8",
                other="#f7fafc"
            )
            
            self._theme_config = ThemeConfig(
                name="light",
                display_name="Light",
                description="Light theme with pastel colors",
                colors=colors
            )
        
        return self._theme_config
    
    def get_mermaid_styles(self) -> str:
        """Get Mermaid light styling."""
        colors = self.theme_config.colors
        
        return f"""    %% Light theme styling
    classDef compute fill:{colors.compute},stroke:{colors.primary},stroke-width:2px,color:#2c5282
    classDef storage fill:{colors.storage},stroke:{colors.secondary},stroke-width:2px,color:#285e61
    classDef network fill:{colors.networking},stroke:{colors.accent},stroke-width:2px,color:#276749
    classDef database fill:{colors.database},stroke:{colors.warning},stroke-width:2px,color:#9c4221
    classDef security fill:{colors.security},stroke:#805ad5,stroke-width:2px,color:#553c9a
    classDef management fill:{colors.management},stroke:#d53f8c,stroke-width:2px,color:#702459
    classDef default fill:{colors.background},stroke:{colors.foreground},stroke-width:1px,color:{colors.foreground}"""
    
    def get_graphviz_styles(self) -> Dict[str, str]:
        """Get Graphviz light styling."""
        colors = self.theme_config.colors
        typography = self.theme_config.typography
        
        return {
            'graph': {
                'bgcolor': colors.background,
                'fontname': typography.font_family,
                'fontsize': str(typography.font_size),
                'fontcolor': colors.foreground
            },
            'node': {
                'fontname': typography.font_family,
                'fontsize': str(typography.font_size),
                'style': 'rounded,filled',
                'fillcolor': colors.compute,
                'color': colors.primary,
                'fontcolor': colors.foreground
            },
            'edge': {
                'fontname': typography.font_family,
                'fontsize': str(typography.font_size - 1),
                'color': colors.foreground,
                'fontcolor': colors.foreground
            }
        }


class MinimalTheme(BaseTheme):
    """Minimal monochrome theme."""
    
    @property
    def theme_config(self) -> ThemeConfig:
        """Get minimal theme configuration."""
        if self._theme_config is None:
            colors = ColorPalette(
                primary="#374151",
                secondary="#6b7280",
                accent="#9ca3af",
                background="#ffffff",
                foreground="#374151",
                success="#374151",
                warning="#6b7280",
                error="#374151",
                info="#9ca3af",
                compute="#f9fafb",
                storage="#f9fafb",
                networking="#f9fafb",
                database="#f9fafb",
                security="#f9fafb",
                management="#f9fafb",
                other="#f9fafb"
            )
            
            self._theme_config = ThemeConfig(
                name="minimal",
                display_name="Minimal",
                description="Clean minimal monochrome theme",
                colors=colors
            )
        
        return self._theme_config
    
    def get_mermaid_styles(self) -> str:
        """Get Mermaid minimal styling."""
        colors = self.theme_config.colors
        
        return f"""    %% Minimal theme styling
    classDef default fill:{colors.compute},stroke:{colors.secondary},stroke-width:1px,color:{colors.foreground}"""
    
    def get_graphviz_styles(self) -> Dict[str, str]:
        """Get Graphviz minimal styling."""
        colors = self.theme_config.colors
        typography = self.theme_config.typography
        
        return {
            'graph': {
                'bgcolor': colors.background,
                'fontname': typography.font_family,
                'fontsize': str(typography.font_size),
                'fontcolor': colors.foreground
            },
            'node': {
                'fontname': typography.font_family,
                'fontsize': str(typography.font_size),
                'style': 'rounded,filled',
                'fillcolor': colors.compute,
                'color': colors.secondary,
                'fontcolor': colors.foreground
            },
            'edge': {
                'fontname': typography.font_family,
                'fontsize': str(typography.font_size - 1),
                'color': colors.secondary,
                'fontcolor': colors.foreground
            }
        }


class ColorfulTheme(BaseTheme):
    """Bright colorful theme."""
    
    @property
    def theme_config(self) -> ThemeConfig:
        """Get colorful theme configuration."""
        if self._theme_config is None:
            colors = ColorPalette(
                primary="#e74c3c",
                secondary="#3498db",
                accent="#2ecc71",
                background="#ffffff",
                foreground="#2c3e50",
                success="#27ae60",
                warning="#f39c12",
                error="#e74c3c",
                info="#3498db",
                compute="#ff6b6b",
                storage="#4ecdc4",
                networking="#45b7d1",
                database="#f9ca24",
                security="#6c5ce7",
                management="#fd79a8",
                other="#78e08f"
            )
            
            self._theme_config = ThemeConfig(
                name="colorful",
                display_name="Colorful",
                description="Bright and vibrant colorful theme",
                colors=colors
            )
        
        return self._theme_config
    
    def get_mermaid_styles(self) -> str:
        """Get Mermaid colorful styling."""
        colors = self.theme_config.colors
        
        return f"""    %% Colorful theme styling
    classDef compute fill:{colors.compute},stroke:#ee5a52,stroke-width:2px,color:#fff
    classDef storage fill:{colors.storage},stroke:#45b7b8,stroke-width:2px,color:#fff
    classDef network fill:{colors.networking},stroke:#3498db,stroke-width:2px,color:#fff
    classDef database fill:{colors.database},stroke:#f0932b,stroke-width:2px,color:#000
    classDef security fill:{colors.security},stroke:#a29bfe,stroke-width:2px,color:#fff
    classDef management fill:{colors.management},stroke:#e84393,stroke-width:2px,color:#fff
    classDef default fill:{colors.background},stroke:{colors.foreground},stroke-width:1px,color:{colors.foreground}"""
    
    def get_graphviz_styles(self) -> Dict[str, str]:
        """Get Graphviz colorful styling."""
        colors = self.theme_config.colors
        typography = self.theme_config.typography
        
        return {
            'graph': {
                'bgcolor': colors.background,
                'fontname': typography.font_family,
                'fontsize': str(typography.font_size),
                'fontcolor': colors.foreground
            },
            'node': {
                'fontname': typography.font_family,
                'fontsize': str(typography.font_size),
                'style': 'rounded,filled',
                'fillcolor': colors.primary,
                'color': colors.foreground,
                'fontcolor': '#ffffff'
            },
            'edge': {
                'fontname': typography.font_family,
                'fontsize': str(typography.font_size - 1),
                'color': colors.foreground,
                'fontcolor': colors.foreground
            }
        }


class ThemeManager(LoggerMixin):
    """Manager for visualization themes."""
    
    def __init__(self):
        """Initialize theme manager."""
        self._themes = {}
        self._register_default_themes()
    
    def _register_default_themes(self):
        """Register default themes."""
        self.register_theme(ProfessionalTheme())
        self.register_theme(DarkTheme())
        self.register_theme(LightTheme())
        self.register_theme(MinimalTheme())
        self.register_theme(ColorfulTheme())
    
    def register_theme(self, theme: BaseTheme):
        """Register a theme."""
        self._themes[theme.theme_config.name] = theme
        self.log_debug("Registered theme", theme=theme.theme_config.name)
    
    def get_theme(self, theme_name: str) -> Optional[BaseTheme]:
        """Get a theme by name."""
        return self._themes.get(theme_name)
    
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        return list(self._themes.keys())
    
    def get_theme_info(self, theme_name: str) -> Optional[Dict[str, str]]:
        """Get theme information."""
        theme = self.get_theme(theme_name)
        if theme:
            config = theme.theme_config
            return {
                'name': config.name,
                'display_name': config.display_name,
                'description': config.description
            }
        return None
    
    def get_all_themes_info(self) -> List[Dict[str, str]]:
        """Get information for all themes."""
        return [self.get_theme_info(name) for name in self.get_available_themes()]
