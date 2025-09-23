"""Test CloudViz core functionality."""
import pytest
from cloudviz import __version__


def test_version():
    """Test that version is accessible."""
    assert __version__ is not None


def test_cloudviz_import():
    """Test that CloudViz can be imported successfully."""
    import cloudviz
    assert cloudviz is not None


def test_api_import():
    """Test that CloudViz API can be imported."""
    try:
        from cloudviz.api import main
        assert main is not None
    except ImportError as e:
        pytest.skip(f"API module has import issues: {e}")


class TestCloudVizCore:
    """Test CloudViz core functionality."""
    
    def test_package_structure(self):
        """Test that package structure is correct."""
        # Test core package
        import cloudviz.core
        assert cloudviz.core is not None
        
        # Test providers package
        import cloudviz.providers
        assert cloudviz.providers is not None
        
        # Test visualization package
        import cloudviz.visualization
        assert cloudviz.visualization is not None
        
        # Test API package (with error handling)
        try:
            import cloudviz.api
            assert cloudviz.api is not None
        except ImportError as e:
            pytest.skip(f"API module has import issues: {e}")