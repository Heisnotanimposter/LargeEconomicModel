# Contributing to Economic Data API

Thank you for considering contributing to the Economic Data API! This document provides guidelines and instructions for contributing.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages

### Suggesting Features

Feature suggestions are welcome! Please create an issue with:
- Clear description of the feature
- Use case and benefits
- Potential implementation approach (optional)
- Examples of similar features in other projects (optional)

### Code Contributions

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/LargeEconomicModel.git
   cd LargeEconomicModel
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r api_requirements.txt
   pip install pytest black flake8 mypy  # Development tools
   ```

4. **Make your changes**
   - Write clear, documented code
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed

5. **Test your changes**
   ```bash
   # Run tests
   pytest
   
   # Check code formatting
   black api/
   
   # Run linter
   flake8 api/
   
   # Type checking
   mypy api/
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```
   
   Use conventional commit messages:
   - `feat:` - New features
   - `fix:` - Bug fixes
   - `docs:` - Documentation changes
   - `style:` - Code style changes (formatting, etc.)
   - `refactor:` - Code refactoring
   - `test:` - Adding or updating tests
   - `chore:` - Maintenance tasks

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Provide a clear description of your changes
   - Reference any related issues

## 📝 Code Style Guidelines

### Python Code Style

We follow PEP 8 with some modifications:
- Line length: 100 characters (soft limit), 120 (hard limit)
- Use type hints for function parameters and return values
- Use docstrings for all public modules, functions, classes, and methods

Example:
```python
def get_indicator(
    indicator_id: str,
    country_code: str,
    start_date: Optional[date] = None
) -> Optional[EconomicIndicatorResponse]:
    """
    Fetch economic indicator data.
    
    Args:
        indicator_id: Unique identifier for the indicator
        country_code: ISO 3166-1 alpha-3 country code
        start_date: Optional start date for data
        
    Returns:
        EconomicIndicatorResponse or None if not found
    """
    # Implementation
    pass
```

### Documentation Style

- Use Google-style docstrings
- Include examples where helpful
- Document all parameters and return values
- Add type hints

### Testing Guidelines

- Write unit tests for all new features
- Aim for >80% code coverage
- Use descriptive test names
- Use fixtures for common test data
- Test edge cases and error conditions

Example:
```python
def test_get_indicator_valid_country():
    """Test getting indicator with valid country code"""
    response = client.get("/api/v1/indicators/GDP?country=USA")
    assert response.status_code == 200
    data = response.json()
    assert data["country_code"] == "USA"
```

## 🏗️ Project Structure

When adding new features, maintain the existing structure:

```
api/
├── core/           # Core configurations and utilities
├── models/         # Data models (Pydantic and SQLAlchemy)
├── providers/      # Data source providers
├── routers/        # API endpoint routers
├── middleware/     # Middleware (auth, rate limiting)
└── main.py         # FastAPI application
```

## 🔧 Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL (optional)
- Redis (optional)
- Git

### Development Dependencies
```bash
pip install -r api_requirements.txt
pip install pytest pytest-asyncio pytest-cov black flake8 mypy
```

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=api --cov-report=html

# Specific test file
pytest tests/test_api.py

# Specific test
pytest tests/test_api.py::test_health_check

# Verbose output
pytest -v
```

### Code Quality Checks
```bash
# Format code
black api/

# Check formatting (without modifying)
black --check api/

# Linting
flake8 api/

# Type checking
mypy api/
```

## 📚 Adding New Data Providers

To add a new data provider:

1. Create a new file in `api/providers/`
2. Inherit from `BaseDataProvider`
3. Implement required methods:
   - `get_indicator()`
   - `list_indicators()`
   - `list_countries()`
4. Add provider to `ProviderManager`
5. Add configuration in `api/core/config.py`
6. Add documentation
7. Add tests

Example:
```python
from api.providers.base import BaseDataProvider

class NewProvider(BaseDataProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://api.newprovider.com"
        self.name = "New Provider"
    
    async def get_indicator(self, ...):
        # Implementation
        pass
```

## 🧪 Testing New Features

1. Write unit tests
2. Test manually using:
   - Interactive docs: http://localhost:8000/docs
   - Python examples
   - cURL commands
3. Test edge cases
4. Test error handling
5. Update documentation

## 📖 Documentation

When adding features, update:
- Code docstrings
- API_README.md (if adding endpoints)
- QUICKSTART.md (if affecting setup)
- Examples (if useful for users)
- CHANGELOG.md

## 🐛 Debugging

### Enable Debug Mode
```bash
# In .env
DEBUG=true
LOG_LEVEL=DEBUG
```

### View Logs
```bash
# Docker
docker-compose logs -f api

# Local
# Logs will appear in console with uvicorn --reload
```

### Common Issues

1. **Import errors**: Make sure you're in the virtual environment
2. **Database errors**: Check DATABASE_URL in .env
3. **API key errors**: Verify keys in .env
4. **Rate limiting**: Disable temporarily with ENABLE_RATE_LIMITING=false

## 📋 Pull Request Checklist

Before submitting a PR, ensure:
- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] No linting errors
- [ ] Type hints are added
- [ ] Docstrings are complete
- [ ] Examples are updated (if needed)

## 🎯 Areas for Contribution

Current priorities:
- [ ] Additional data providers (Eurostat, BIS, etc.)
- [ ] Forecasting models
- [ ] WebSocket support
- [ ] Client SDKs (Python, JavaScript, R)
- [ ] GraphQL API
- [ ] Admin dashboard
- [ ] Data export formats
- [ ] Performance optimizations
- [ ] Additional analytics functions

## 💬 Communication

- **GitHub Issues**: For bugs and feature requests
- **Pull Requests**: For code contributions
- **Discussions**: For general questions and ideas

## 📜 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help maintain a positive community

## 🙏 Recognition

Contributors will be:
- Listed in CHANGELOG.md
- Mentioned in release notes
- Added to contributors list (if significant contribution)

Thank you for contributing to Economic Data API! 🎉

