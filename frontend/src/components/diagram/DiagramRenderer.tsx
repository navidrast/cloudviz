import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  ButtonGroup,
  CircularProgress,
  Alert,
  Toolbar,
  IconButton,
  Tooltip,
  Paper,
  useTheme,
} from '@mui/material';
import {
  ZoomIn,
  ZoomOut,
  ZoomOutMap,
  Download,
  Fullscreen,
  FullscreenExit,
  Refresh,
  Share,
} from '@mui/icons-material';
import mermaid from 'mermaid';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import { OutputFormat, DiagramResponse } from '../../types/api';

interface DiagramRendererProps {
  diagram?: DiagramResponse;
  loading?: boolean;
  error?: any;
  onRefresh?: () => void;
  onExport?: (format: OutputFormat) => void;
  enableExport?: boolean;
  enableFullscreen?: boolean;
  title?: string;
}

const DiagramRenderer: React.FC<DiagramRendererProps> = ({
  diagram,
  loading,
  error,
  onRefresh,
  onExport,
  enableExport = true,
  enableFullscreen = true,
  title = 'Infrastructure Diagram',
}) => {
  const theme = useTheme();
  const mermaidRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [zoom, setZoom] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [mermaidError, setMermaidError] = useState<string | null>(null);

  useEffect(() => {
    // Initialize Mermaid with configuration
    mermaid.initialize({
      startOnLoad: false,
      theme: theme.palette.mode === 'dark' ? 'dark' : 'default',
      securityLevel: 'loose',
      fontFamily: theme.typography.fontFamily,
      flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
        curve: 'basis',
      },
      sequence: {
        useMaxWidth: true,
        wrap: true,
      },
      er: {
        useMaxWidth: true,
      },
      journey: {
        useMaxWidth: true,
      },
      gitGraph: {
        useMaxWidth: true,
      },
    });
  }, [theme]);

  const renderMermaidDiagram = useCallback(async () => {
    if (!diagram?.content || !mermaidRef.current) return;

    try {
      setMermaidError(null);
      
      // Clear previous content
      mermaidRef.current.innerHTML = '';
      
      // Generate unique ID for this diagram
      const diagramId = `mermaid-${Date.now()}`;
      
      // Validate and render the diagram
      const { svg } = await mermaid.render(diagramId, diagram.content);
      
      // Insert the SVG into the container
      mermaidRef.current.innerHTML = svg;
      
      // Apply zoom
      const svgElement = mermaidRef.current.querySelector('svg');
      if (svgElement) {
        svgElement.style.maxWidth = '100%';
        svgElement.style.height = 'auto';
        svgElement.style.transform = `scale(${zoom})`;
        svgElement.style.transformOrigin = 'top left';
      }
    } catch (err) {
      console.error('Mermaid rendering error:', err);
      setMermaidError(err instanceof Error ? err.message : 'Failed to render diagram');
    }
  }, [diagram?.content, zoom]);

  useEffect(() => {
    if (diagram?.content && mermaidRef.current) {
      renderMermaidDiagram();
    }
  }, [diagram?.content, renderMermaidDiagram]);

  const handleZoomIn = () => {
    const newZoom = Math.min(zoom * 1.2, 3);
    setZoom(newZoom);
    updateZoom(newZoom);
  };

  const handleZoomOut = () => {
    const newZoom = Math.max(zoom / 1.2, 0.3);
    setZoom(newZoom);
    updateZoom(newZoom);
  };

  const handleZoomReset = () => {
    setZoom(1);
    updateZoom(1);
  };

  const updateZoom = (newZoom: number) => {
    if (mermaidRef.current) {
      const svgElement = mermaidRef.current.querySelector('svg');
      if (svgElement) {
        svgElement.style.transform = `scale(${newZoom})`;
      }
    }
  };

  const handleFullscreen = () => {
    if (!isFullscreen && containerRef.current) {
      containerRef.current.requestFullscreen?.();
      setIsFullscreen(true);
    } else if (document.fullscreenElement) {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const handleExportSVG = () => {
    if (mermaidRef.current) {
      const svgElement = mermaidRef.current.querySelector('svg');
      if (svgElement) {
        const svgData = new XMLSerializer().serializeToString(svgElement);
        const blob = new Blob([svgData], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'diagram.svg';
        link.click();
        URL.revokeObjectURL(url);
      }
    }
    onExport?.(OutputFormat.SVG);
  };

  const handleExportPNG = async () => {
    if (mermaidRef.current) {
      try {
        const canvas = await html2canvas(mermaidRef.current, {
          backgroundColor: theme.palette.background.paper,
          scale: 2, // Higher resolution
        });
        
        canvas.toBlob((blob) => {
          if (blob) {
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'diagram.png';
            link.click();
            URL.revokeObjectURL(url);
          }
        });
      } catch (err) {
        console.error('PNG export failed:', err);
      }
    }
    onExport?.(OutputFormat.PNG);
  };

  const handleExportPDF = async () => {
    if (mermaidRef.current) {
      try {
        const canvas = await html2canvas(mermaidRef.current, {
          backgroundColor: theme.palette.background.paper,
          scale: 2,
        });
        
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF({
          orientation: canvas.width > canvas.height ? 'landscape' : 'portrait',
          unit: 'px',
          format: [canvas.width, canvas.height],
        });
        
        pdf.addImage(imgData, 'PNG', 0, 0, canvas.width, canvas.height);
        pdf.save('diagram.pdf');
      } catch (err) {
        console.error('PDF export failed:', err);
      }
    }
    onExport?.(OutputFormat.PDF);
  };

  const handleShare = () => {
    if (navigator.share && diagram?.content) {
      navigator.share({
        title: 'CloudViz Infrastructure Diagram',
        text: 'Check out this infrastructure diagram from CloudViz',
        url: window.location.href,
      });
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href);
    }
  };

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
            <CircularProgress size={48} />
            <Typography variant="h6" sx={{ ml: 2 }}>
              Rendering diagram...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error" action={
            onRefresh && (
              <Button color="inherit" size="small" onClick={onRefresh}>
                Retry
              </Button>
            )
          }>
            Failed to load diagram: {(error as any)?.detail || (error as any)?.message}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!diagram) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="h6" color="textSecondary">
              No diagram available
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Extract resources and render a diagram to view it here
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card ref={containerRef} sx={{ height: isFullscreen ? '100vh' : 'auto' }}>
      {/* Toolbar */}
      <Toolbar sx={{ borderBottom: 1, borderColor: 'divider' }} variant="dense">
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          {title}
        </Typography>
        
        {/* Zoom Controls */}
        <ButtonGroup size="small" sx={{ mr: 1 }}>
          <Tooltip title="Zoom In">
            <IconButton onClick={handleZoomIn}>
              <ZoomIn />
            </IconButton>
          </Tooltip>
          <Tooltip title="Reset Zoom">
            <IconButton onClick={handleZoomReset}>
              <ZoomOutMap />
            </IconButton>
          </Tooltip>
          <Tooltip title="Zoom Out">
            <IconButton onClick={handleZoomOut}>
              <ZoomOut />
            </IconButton>
          </Tooltip>
        </ButtonGroup>

        {/* Export Controls */}
        {enableExport && (
          <ButtonGroup size="small" sx={{ mr: 1 }}>
            <Tooltip title="Export as SVG">
              <IconButton onClick={handleExportSVG}>
                <Download />
              </IconButton>
            </Tooltip>
            <Tooltip title="Export as PNG">
              <IconButton onClick={handleExportPNG}>
                <Download />
              </IconButton>
            </Tooltip>
            <Tooltip title="Export as PDF">
              <IconButton onClick={handleExportPDF}>
                <Download />
              </IconButton>
            </Tooltip>
          </ButtonGroup>
        )}

        {/* Other Controls */}
        <Tooltip title="Share">
          <IconButton onClick={handleShare} size="small">
            <Share />
          </IconButton>
        </Tooltip>
        
        {onRefresh && (
          <Tooltip title="Refresh">
            <IconButton onClick={onRefresh} size="small">
              <Refresh />
            </IconButton>
          </Tooltip>
        )}

        {enableFullscreen && (
          <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}>
            <IconButton onClick={handleFullscreen} size="small">
              {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
            </IconButton>
          </Tooltip>
        )}
      </Toolbar>

      {/* Diagram Content */}
      <CardContent sx={{ 
        overflow: 'auto',
        height: isFullscreen ? 'calc(100vh - 64px)' : 'auto',
        maxHeight: isFullscreen ? 'none' : '80vh',
        p: 2,
      }}>
        {mermaidError ? (
          <Alert severity="error">
            <Typography variant="subtitle2">Diagram Rendering Error</Typography>
            <Typography variant="body2">{mermaidError}</Typography>
            <Box sx={{ mt: 2 }}>
              <Button size="small" onClick={renderMermaidDiagram}>
                Retry Rendering
              </Button>
            </Box>
          </Alert>
        ) : (
          <Paper 
            elevation={0} 
            sx={{ 
              p: 2,
              overflow: 'auto',
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
            }}
          >
            <div 
              ref={mermaidRef}
              style={{
                textAlign: 'center',
                minHeight: '200px',
              }}
            />
          </Paper>
        )}

        {/* Diagram Info */}
        {diagram.metadata && (
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="caption" color="textSecondary">
              Format: {diagram.format} • 
              Created: {new Date(diagram.metadata.created_at).toLocaleString()}
            </Typography>
            <Typography variant="caption" color="textSecondary">
              Zoom: {Math.round(zoom * 100)}%
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default DiagramRenderer;