# Contributing to CloudViz

Thank you for your interest in contributing to CloudViz! This guide will help you get started with contributing to the project.

## 🤝 How to Contribute

There are many ways to contribute to CloudViz:

- **🐛 Report bugs** - Help us identify and fix issues
- **💡 Suggest features** - Share ideas for new functionality
- **📝 Improve documentation** - Help make our docs better
- **🔧 Submit code** - Fix bugs or implement new features
- **🧪 Write tests** - Improve test coverage
- **🎨 Design improvements** - Enhance user experience

## 🚀 Getting Started

### 1. Fork the Repository

```bash
# Fork the repo on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/cloudviz.git
cd cloudviz

# Add the original repo as upstream
git remote add upstream https://github.com/navidrast/cloudviz.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements/dev.txt

# Install pre-commit hooks
pre-commit install

# Set up environment variables
cp .env.example .env
# Edit .env with your cloud provider credentials
```

### 3. Run Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=cloudviz

# Run specific test file
pytest tests/test_azure_provider.py

# Run linting
flake8 cloudviz/
black --check cloudviz/
isort --check-only cloudviz/
```

### 4. Start Development Server

```bash
# Start the API server
uvicorn cloudviz.api.main:app --reload --host 0.0.0.0 --port 8000

# Verify it's working
curl http://localhost:8000/health
```

## 📋 Development Guidelines

### Code Style

We use Python code formatting tools to maintain consistency:

```bash
# Format code
black cloudviz/
isort cloudviz/

# Check formatting
black --check cloudviz/
isort --check-only cloudviz/
flake8 cloudviz/
```

### Code Standards

- **Python**: Follow PEP 8 style guide
- **Type Hints**: Use type hints for all functions and methods
- **Docstrings**: Use Google-style docstrings
- **Comments**: Write clear, concise comments
- **Error Handling**: Always handle exceptions gracefully

### Example Code Style

```python
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AzureResourceExtractor:
    """Azure resource extraction service.
    
    This class handles the extraction of resources from Azure subscriptions,
    including virtual machines, storage accounts, and databases.
    
    Attributes:
        client: Azure management client instance
        subscription_id: Azure subscription identifier
    """
    
    def __init__(self, subscription_id: str) -> None:
        """Initialize the Azure resource extractor.
        
        Args:
            subscription_id: Azure subscription ID
            
        Raises:
            ValueError: If subscription_id is invalid
        """
        if not subscription_id:
            raise ValueError("Subscription ID cannot be empty")
            
        self.subscription_id = subscription_id
        self.client = self._create_client()
    
    def extract_resources(
        self, 
        resource_groups: Optional[List[str]] = None,
        resource_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Extract resources from Azure subscription.
        
        Args:
            resource_groups: List of resource groups to scan
            resource_types: List of resource types to include
            
        Returns:
            Dictionary containing extracted resource information
            
        Raises:
            AzureAPIError: If Azure API calls fail
        """
        try:
            logger.info(f"Starting resource extraction for subscription {self.subscription_id}")
            
            resources = []
            # Implementation here...
            
            logger.info(f"Extracted {len(resources)} resources successfully")
            return {"resources": resources, "total": len(resources)}
            
        except Exception as e:
            logger.error(f"Failed to extract resources: {e}")
            raise AzureAPIError(f"Resource extraction failed: {e}")
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/                 # Unit tests
│   ├── test_azure.py
│   ├── test_aws.py
│   └── test_gcp.py
├── integration/          # Integration tests
│   ├── test_api.py
│   └── test_workflows.py
├── fixtures/            # Test data and fixtures
└── conftest.py         # Pytest configuration
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch
from cloudviz.providers.azure import AzureResourceExtractor


class TestAzureResourceExtractor:
    """Test cases for Azure resource extraction."""
    
    @pytest.fixture
    def extractor(self):
        """Create Azure resource extractor instance."""
        return AzureResourceExtractor("test-subscription-id")
    
    def test_extract_resources_success(self, extractor):
        """Test successful resource extraction."""
        # Mock Azure API responses
        with patch.object(extractor, '_get_virtual_machines') as mock_vms:
            mock_vms.return_value = [
                {"name": "test-vm", "type": "VirtualMachine"}
            ]
            
            result = extractor.extract_resources()
            
            assert result["total"] == 1
            assert result["resources"][0]["name"] == "test-vm"
    
    def test_extract_resources_with_filters(self, extractor):
        """Test resource extraction with filters."""
        result = extractor.extract_resources(
            resource_groups=["production"],
            resource_types=["VirtualMachine"]
        )
        
        assert isinstance(result, dict)
        assert "resources" in result
    
    def test_extract_resources_failure(self, extractor):
        """Test resource extraction failure handling."""
        with patch.object(extractor, '_get_virtual_machines') as mock_vms:
            mock_vms.side_effect = Exception("API Error")
            
            with pytest.raises(AzureAPIError):
                extractor.extract_resources()
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_azure.py

# Run tests with coverage
pytest --cov=cloudviz --cov-report=html

# Run tests in parallel
pytest -n auto

# Run only failed tests
pytest --lf
```

## 🐛 Bug Reports

When reporting bugs, please include:

### Bug Report Template

```markdown
**Bug Description**
A clear description of what the bug is.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g. Ubuntu 22.04]
- Python: [e.g. 3.9.0]
- CloudViz version: [e.g. 1.0.0]
- Cloud provider: [e.g. Azure]

**Additional Context**
- Error logs
- Screenshots
- Configuration files (without sensitive data)
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
A clear description of what you want to happen.

**Problem Statement**
What problem does this feature solve?

**Proposed Solution**
How would you like this feature to work?

**Alternatives Considered**
Any alternative solutions you've considered.

**Additional Context**
Any other context, mockups, or examples.
```

## 🔄 Pull Request Process

### 1. Create a Branch

```bash
# Create feature branch
git checkout -b feature/add-gcp-support

# Or bug fix branch
git checkout -b fix/azure-authentication-issue
```

### 2. Make Changes

- Write code following our style guidelines
- Add tests for new functionality
- Update documentation if needed
- Ensure all tests pass

### 3. Commit Changes

```bash
# Add changes
git add .

# Commit with descriptive message
git commit -m "feat: add GCP Compute Engine support

- Implement GCP resource extraction
- Add Compute Engine instance discovery
- Include cost calculation for GCP resources
- Add tests for GCP provider

Fixes #123"
```

### Commit Message Format

We follow [Conventional Commits](https://conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 4. Push and Create PR

```bash
# Push branch
git push origin feature/add-gcp-support

# Create pull request on GitHub
# Include description of changes and link to issues
```

### Pull Request Template

```markdown
**Description**
Brief description of changes made.

**Type of Change**
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

**Testing**
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Manual testing completed

**Checklist**
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced

**Related Issues**
Fixes #123
```

## 📚 Documentation Guidelines

### Documentation Structure

- **API docs**: Use OpenAPI/Swagger specifications
- **User guides**: Step-by-step instructions with examples
- **Code docs**: Inline comments and docstrings
- **Architecture docs**: System design and decisions

### Writing Style

- **Clear and concise**: Use simple, direct language
- **Examples**: Include code examples and screenshots
- **Structure**: Use headings, lists, and tables for organization
- **Accuracy**: Keep documentation up-to-date with code changes

## 🏷️ Issue Labels

We use the following labels to categorize issues:

### Type Labels
- `bug`: Something isn't working
- `enhancement`: New feature or improvement
- `documentation`: Documentation improvements
- `question`: Further information is requested

### Priority Labels
- `priority/critical`: Critical issues requiring immediate attention
- `priority/high`: High priority issues
- `priority/medium`: Medium priority issues
- `priority/low`: Low priority issues

### Component Labels
- `azure`: Azure provider related
- `aws`: AWS provider related
- `gcp`: GCP provider related
- `api`: REST API related
- `visualization`: Diagram generation related
- `n8n`: n8n integration related

### Status Labels
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `wontfix`: This will not be worked on
- `duplicate`: Duplicate issue

## 🎯 Areas for Contribution

Looking for ideas? Here are areas where we'd love contributions:

### High Priority
- **Cloud Provider Support**: Additional cloud providers (Oracle Cloud, IBM Cloud)
- **Visualization Improvements**: New diagram layouts and themes
- **Performance Optimization**: Faster resource discovery and rendering
- **Testing**: Improved test coverage and integration tests

### Medium Priority
- **Documentation**: More examples and tutorials
- **Monitoring**: Better metrics and observability
- **CLI Tool**: Command-line interface for CloudViz
- **Mobile Support**: Responsive diagram viewing

### Nice to Have
- **AI/ML Features**: Intelligent resource recommendations
- **Integration**: Additional workflow tools beyond n8n
- **Compliance**: Security and compliance reporting
- **Analytics**: Advanced cost and usage analytics

## 📞 Getting Help

Need help with your contribution?

- **Discord**: Join our [Discord community](https://discord.gg/cloudviz)
- **GitHub Discussions**: Use [GitHub Discussions](https://github.com/navidrast/cloudviz/discussions)
- **Email**: Contact maintainers at contribute@cloudviz.dev

## 🏆 Recognition

Contributors are recognized in:

- **README**: Listed in the contributors section
- **Changelog**: Mentioned in release notes
- **Blog**: Featured in contributor spotlight posts
- **Swag**: CloudViz stickers and swag for significant contributions

## 📄 License

By contributing to CloudViz, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to CloudViz!** 🎉

Your contributions help make CloudViz better for everyone in the cloud infrastructure community.