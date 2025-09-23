# Contributing to CloudViz

Thank you for your interest in contributing to CloudViz! This document provides guidelines for contributing to our multi-cloud infrastructure visualization platform.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Code Standards](#code-standards)
- [Pull Request Process](#pull-request-process)
- [GitHub Copilot Safety Guidelines](#github-copilot-safety-guidelines)
- [Security Considerations](#security-considerations)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community Guidelines](#community-guidelines)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Docker (optional, for containerized development)
- GitHub account with 2FA enabled

### First Time Setup

1. **Fork the repository**
   ```bash
   # Navigate to https://github.com/navidrast/cloudviz and click "Fork"
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/cloudviz.git
   cd cloudviz
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/navidrast/cloudviz.git
   ```

## Development Environment Setup

### Local Development

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

4. **Verify installation**
   ```bash
   python -c "import cloudviz; print('✅ CloudViz installed successfully')"
   ```

### Running Tests

```bash
# Run all available tests
python -c "
import cloudviz
print('✅ Basic import test passed')
"

# Run linting
black cloudviz/
isort cloudviz/
flake8 cloudviz/
mypy cloudviz/

# Run security checks
bandit -r cloudviz/
safety check
```

## Code Standards

### Python Code Quality

- **Follow PEP 8** style guidelines
- **Add type hints** to all functions and methods
- **Write comprehensive docstrings** using Google or NumPy style
- **Maintain test coverage** above 85% (when tests are available)
- **Use meaningful variable and function names**

### Code Formatting

We use automated formatting tools:

```bash
# Format code
black cloudviz/
isort cloudviz/

# Check formatting (CI will verify this)
black --check cloudviz/
isort --check-only cloudviz/
```

### Example Code Structure

```python
"""Module docstring describing the purpose."""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def process_cloud_resources(
    resources: List[Dict[str, str]], 
    filter_type: Optional[str] = None
) -> Dict[str, int]:
    """Process cloud resources and return statistics.
    
    Args:
        resources: List of cloud resource dictionaries
        filter_type: Optional resource type filter
        
    Returns:
        Dictionary containing resource statistics
        
    Raises:
        ValueError: If resources list is empty
    """
    if not resources:
        raise ValueError("Resources list cannot be empty")
        
    # Implementation here
    return {"processed": len(resources)}
```

## Pull Request Process

### Before Creating a PR

1. **Sync with upstream**
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write code following our standards
   - Add tests for new functionality
   - Update documentation if needed

4. **Test locally**
   ```bash
   # Run linting and formatting
   black cloudviz/ && isort cloudviz/ && flake8 cloudviz/ && mypy cloudviz/
   
   # Run security checks
   bandit -r cloudviz/
   safety check
   ```

### Creating the PR

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**
   - Use a descriptive title (at least 10 characters)
   - Provide a detailed description explaining:
     - What changes were made
     - Why the changes were necessary
     - How to test the changes
     - Any potential risks or considerations

3. **PR Requirements**
   - ✅ All CI checks must pass
   - ✅ Code review from at least one maintainer
   - ✅ No conflicts with main branch
   - ✅ Documentation updated (if applicable)

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Local testing completed
- [ ] All CI checks pass
- [ ] Manual testing steps documented

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No sensitive data committed
```

## GitHub Copilot Safety Guidelines

### ✅ Safe Copilot Usage

**DO:**

1. **Review all generated code** before committing
   - Understand what the code does
   - Verify it follows our coding standards
   - Check for security vulnerabilities

2. **Use Copilot for boilerplate and patterns**
   ```python
   # Good: Using Copilot for standard patterns
   async def get_azure_resources() -> List[Resource]:
       """Get Azure resources using standard SDK patterns."""
       # Let Copilot suggest the Azure SDK boilerplate
   ```

3. **Validate suggestions against our codebase**
   - Ensure consistency with existing code
   - Verify naming conventions match
   - Check that imports are correct

4. **Use descriptive comments to guide Copilot**
   ```python
   # Get all virtual machines from Azure subscription with pagination
   # Handle authentication errors gracefully
   # Return structured resource data
   def fetch_azure_vms():
       # Copilot will provide better suggestions with clear intent
   ```

5. **Test all generated code thoroughly**
   - Run unit tests
   - Perform integration testing
   - Verify error handling

### ❌ Unsafe Copilot Usage

**DON'T:**

1. **Blindly accept all suggestions**
   ```python
   # Bad: Don't commit without understanding
   def mysterious_function():
       # Some complex code you don't understand
       pass
   ```

2. **Let Copilot generate sensitive data**
   - API keys, passwords, or tokens
   - Database connection strings
   - Cloud credentials or secrets
   
3. **Use Copilot-generated code without proper attribution**
   - Always review licensing implications
   - Understand copyright considerations
   - Ensure compliance with open source licenses

4. **Ignore security warnings**
   ```python
   # Bad: Don't ignore security implications
   def unsafe_sql_query(user_input):
       query = f"SELECT * FROM users WHERE id = {user_input}"  # SQL injection risk!
   ```

### Copilot Best Practices

1. **Context-Aware Prompting**
   ```python
   # Good: Provide context for better suggestions
   class AzureResourceExtractor:
       """Extract Azure resources following CloudViz patterns."""
       
       def __init__(self, subscription_id: str):
           # Copilot understands the CloudViz context
           self.subscription_id = subscription_id
   ```

2. **Incremental Development**
   - Use Copilot for small, focused functions
   - Build complex functionality step by step
   - Validate each piece before moving forward

3. **Code Review Integration**
   ```python
   # Add comments explaining Copilot-generated sections
   def process_resources(resources: List[Dict]) -> ProcessedData:
       """Process cloud resources.
       
       Note: Core logic generated with GitHub Copilot assistance,
       reviewed and validated for CloudViz patterns.
       """
   ```

4. **Security-First Mindset**
   - Always review for security vulnerabilities
   - Use static analysis tools (bandit, safety)
   - Follow the principle of least privilege

### Copilot Code Review Checklist

Before committing Copilot-generated code:

- [ ] **Functionality**: Does the code work as intended?
- [ ] **Security**: Are there any security vulnerabilities?
- [ ] **Style**: Does it follow our coding standards?
- [ ] **Performance**: Is the code efficient?
- [ ] **Maintainability**: Is the code readable and maintainable?
- [ ] **Testing**: Are appropriate tests included?
- [ ] **Documentation**: Is the code properly documented?

## Security Considerations

### Sensitive Data Protection

**Never commit:**
- API keys, passwords, or authentication tokens
- Cloud credentials (Azure, AWS, GCP service accounts)
- Database connection strings with credentials
- Private keys or certificates
- Personal identifiable information (PII)

**Use instead:**
- Environment variables for configuration
- Cloud-native secret management services
- Encrypted configuration files (when appropriate)
- GitHub Secrets for CI/CD credentials

### Code Security

1. **Input Validation**
   ```python
   def validate_resource_name(name: str) -> bool:
       """Validate resource name to prevent injection attacks."""
       if not isinstance(name, str):
           return False
       # Allow only alphanumeric, hyphens, and underscores
       return re.match(r'^[a-zA-Z0-9_-]+$', name) is not None
   ```

2. **Error Handling**
   ```python
   try:
       resource = azure_client.get_resource(resource_id)
   except AuthenticationError:
       logger.error("Authentication failed - check credentials")
       raise
   except Exception as e:
       logger.error(f"Unexpected error: {type(e).__name__}")
       # Don't expose internal details in error messages
       raise CloudVizError("Failed to retrieve resource")
   ```

3. **Logging Security**
   ```python
   # Good: Log without sensitive data
   logger.info(f"Processing {len(resources)} resources")
   
   # Bad: Don't log sensitive information
   # logger.info(f"Using API key: {api_key}")
   ```

## Testing Guidelines

### Test Structure (When Available)

```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
└── fixtures/          # Test data and fixtures
```

### Writing Tests

```python
import pytest
from cloudviz.core import ResourceProcessor

def test_resource_processor_initialization():
    """Test ResourceProcessor initialization."""
    processor = ResourceProcessor()
    assert processor is not None

def test_resource_processing_with_empty_list():
    """Test processing with empty resource list."""
    processor = ResourceProcessor()
    with pytest.raises(ValueError, match="Resources list cannot be empty"):
        processor.process([])
```

### Test Guidelines

- Write tests for new functionality
- Test edge cases and error conditions
- Use descriptive test names
- Mock external services (Azure, AWS, GCP APIs)
- Include integration tests for API endpoints

## Documentation

### Code Documentation

- Use clear, concise docstrings
- Document parameters, return values, and exceptions
- Include usage examples for complex functions
- Keep documentation up-to-date with code changes

### README Updates

When adding new features:
- Update relevant README sections
- Add new configuration options
- Include usage examples
- Update installation instructions if needed

## Community Guidelines

### Communication

- Be respectful and professional
- Use inclusive language
- Provide constructive feedback
- Help others learn and grow

### Issue Reporting

- Use the issue templates
- Provide clear reproduction steps
- Include relevant system information
- Search for existing issues first

### Code Reviews

- Focus on code quality and security
- Provide specific, actionable feedback
- Be respectful of different approaches
- Ask questions to understand intent

## Getting Help

- **Documentation**: Check the [docs/wiki/](docs/wiki/) directory
- **Issues**: Search existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact the maintainers for sensitive issues

## License

By contributing to CloudViz, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to CloudViz! Together, we're building better cloud infrastructure visualization tools. 🚀