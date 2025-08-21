# Contributing to Google Trends Analyzer

We welcome contributions to the Google Trends Analyzer project! This document provides guidelines for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Release Process](#release-process)

## 🤝 Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/google-trends-analyzer.git
   cd google-trends-analyzer
   ```

2. **Set Up Development Environment**
   ```bash
   # Run the installation script with dev dependencies
   bash scripts/install.sh --dev
   
   # Or manually:
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

4. **Verify Installation**
   ```bash
   pytest
   trends-analyzer --help
   ```

## 🔧 Making Changes

### Branch Naming Convention

- `feature/description` - for new features
- `bugfix/description` - for bug fixes
- `docs/description` - for documentation updates
- `refactor/description` - for code refactoring

### Commit Message Format

Follow the conventional commit format:

```
type(scope): short description

Longer description if needed

Fixes #issue_number
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat(analyzer): add support for regional comparison`
- `fix(exporter): handle empty dataframes in CSV export`
- `docs(readme): update installation instructions`

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=trends_analyzer --cov-report=html

# Run specific test file
pytest tests/test_core/test_analyzer.py

# Run tests with verbose output
pytest -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the source code structure
- Use descriptive test names
- Include both positive and negative test cases
- Mock external API calls

Example test structure:
```python
class TestTrendsAnalyzer:
    def test_initialization_default(self):
        """Test analyzer initialization with defaults."""
        # Test implementation
        
    def test_get_trends_with_valid_input(self):
        """Test trends collection with valid input."""
        # Test implementation
        
    def test_get_trends_with_invalid_input(self):
        """Test trends collection handles invalid input."""
        # Test implementation
```

### Test Coverage

Maintain test coverage above 90%. Check coverage with:
```bash
pytest --cov=trends_analyzer --cov-report=term-missing
```

## 📝 Style Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use [flake8](https://flake8.pycqa.org/) for linting

### Code Quality Tools

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

### Documentation Style

- Use clear, concise language
- Include code examples
- Document all public APIs
- Use Google-style docstrings

Example docstring:
```python
def get_trends(
    self,
    keywords: List[str],
    timeframe: str = 'today 3-m',
    geo: str = 'US'
) -> pd.DataFrame:
    """
    Get Google Trends data for specified keywords.
    
    Args:
        keywords: List of keywords to analyze
        timeframe: Time range for analysis (e.g., 'today 3-m')
        geo: Geographic region code (e.g., 'US', 'GB')
        
    Returns:
        DataFrame containing trends data with date and keyword columns
        
    Raises:
        ValueError: If keywords list is empty or contains invalid values
        ConnectionError: If unable to connect to Google Trends API
        
    Example:
        >>> analyzer = TrendsAnalyzer()
        >>> data = analyzer.get_trends(['python'], 'today 12-m', 'US')
        >>> print(data.head())
    """
```

## 📤 Pull Request Process

### Before Submitting

1. **Run the full test suite**
   ```bash
   pytest
   ```

2. **Check code quality**
   ```bash
   black --check src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

3. **Update documentation** if needed

4. **Add/update tests** for new functionality

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

### Review Process

1. All PRs require at least one review
2. All tests must pass
3. Code coverage must not decrease
4. Documentation must be updated for new features

## 🏗️ Project Structure

```
google-trends-analyzer/
├── src/trends_analyzer/          # Main package
│   ├── core/                     # Core functionality
│   ├── exporters/                # Data exporters
│   ├── utils/                    # Utilities
│   └── cli/                      # Command-line interface
├── tests/                        # Test suite
├── docs/                         # Documentation
├── examples/                     # Usage examples
├── config/                       # Configuration templates
├── scripts/                      # Utility scripts
└── docker/                       # Docker configuration
```

## 🔄 Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- MAJOR.MINOR.PATCH
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes (backward compatible)

### Release Steps

1. Update version in `setup.py` and `__init__.py`
2. Update `CHANGELOG.md`
3. Create release PR
4. Tag release after merge
5. Create GitHub release
6. Publish to PyPI

## 🐛 Bug Reports

### Before Reporting

1. Check existing issues
2. Try the latest version
3. Provide minimal reproduction case

### Bug Report Template

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python: [e.g., 3.9.7]
- Package Version: [e.g., 1.0.0]

**Additional Context**
Any other relevant information
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other approaches you've considered

**Additional Context**
Any other relevant information
```

## 📞 Getting Help

- 📧 Email: support@trends-analyzer.com
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/google-trends-analyzer/discussions)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/google-trends-analyzer/issues)

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to Google Trends Analyzer! 🎉