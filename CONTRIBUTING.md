# Contributing to MindPy

Thank you for your interest in contributing to MindPy! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)
- [Development Guidelines](#development-guidelines)

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Git
- pip package manager

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/AnujaGajaweera/MindPy.git
   cd mindpy
   ```

3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/AnujaGajaweera/MindPy.git
   ```

## Development Setup

### Install Dependencies

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev,llm,api]"
```

### Install Pre-commit Hooks

Install pre-commit hooks to automatically check code before commits:

```bash
pre-commit install
```

### Verify Installation

Run the test suite to ensure everything is set up correctly:

```bash
pytest
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_events.py
```

### Run with Coverage

```bash
pytest --cov=mindpy --cov-report=html
```

### Run Specific Test Markers

```bash
pytest -m unit      # Run only unit tests
pytest -m integration  # Run only integration tests
```

### Run Async Tests

The project uses pytest-asyncio for async test support:

```bash
pytest -v
```

## Code Style

MindPy uses several tools to maintain code quality:

### Black

Black is used for code formatting:

```bash
black mindpy tests
```

### Ruff

Ruff is used for linting:

```bash
ruff check mindpy tests
```

### MyPy

MyPy is used for type checking:

```bash
mypy mindpy
```

### Pre-commit

Pre-commit hooks run all these checks automatically before commits:

```bash
pre-commit run --all-files
```

### Style Guidelines

- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Use descriptive variable names
- Add comments for complex logic

## Submitting Changes

### Branch Naming

Use descriptive branch names:

```
feature/add-new-skill-system
fix/mining-pathfinding-bug
docs/update-api-documentation
```

### Commit Messages

Follow conventional commit format:

```
feat: add new mining skill
fix: resolve pathfinding deadlock
docs: update contributing guide
refactor: simplify event bus
test: add inventory tests
```

### Pull Request Process

1. Update your branch with the latest from upstream:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. Run tests and linting:
   ```bash
   pytest
   black mindpy tests
   ruff check mindpy tests
   mypy mindpy
   ```

3. Create a pull request with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots for UI changes
   - Test results

4. Address review feedback and update as needed

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added for new functionality
- [ ] Documentation updated
- [ ] All tests pass
- [ ] No linting errors
- [ ] Commit messages follow conventional format

## Reporting Bugs

### Before Reporting

1. Check existing issues to avoid duplicates
2. Verify the bug still exists in the latest version
3. Search for similar issues

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment**
- OS: [e.g. Windows 10, macOS 12.0]
- Python version: [e.g. 3.12.0]
- MindPy version: [e.g. 0.1.0]

**Additional context**
Add any other context about the problem here.
```

## Feature Requests

### Before Requesting

1. Check existing feature requests
2. Consider if the feature fits the project scope
3. Think about implementation complexity

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
A clear description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

## Development Guidelines

### Architecture Principles

- **Modularity**: Keep components loosely coupled
- **Testability**: Write testable code with clear interfaces
- **Documentation**: Document public APIs and complex logic
- **Performance**: Consider performance implications of changes
- **Security**: Validate user inputs and handle errors gracefully

### Adding New Features

1. Update the architecture documentation if needed
2. Add comprehensive tests
3. Update the API documentation
4. Add examples if applicable
5. Consider backward compatibility

### Breaking Changes

- Document breaking changes clearly
- Provide migration guide if needed
- Update version appropriately (semantic versioning)
- Announce in release notes

### Testing Guidelines

- Write unit tests for all new functions
- Add integration tests for complex workflows
- Test edge cases and error conditions
- Maintain test coverage above 80%

### Documentation Guidelines

- Update README for user-facing changes
- Update API documentation for new functions
- Add examples for new features
- Keep documentation in sync with code

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Documentation**: Check existing docs first
- **Code Examples**: Look at examples directory

## Code of Conduct

MindPy follows the Python Community Code of Conduct. Be respectful, inclusive, and constructive in all interactions.

## License

By contributing to MindPy, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are recognized in the project's CONTRIBUTORS file and in release notes. Thank you for your contributions!
