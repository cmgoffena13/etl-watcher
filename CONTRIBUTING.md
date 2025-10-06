# Contributing to Watcher

Thank you for your interest in contributing to Watcher! I welcome contributions from the community and appreciate your help in making this project better.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Process](#development-process)
3. [Code Standards](#code-standards)
4. [Testing Guidelines](#testing-guidelines)
5. [Pull Request Process](#pull-request-process)
6. [Issue Guidelines](#issue-guidelines)
7. [Recognition](#recognition)
8. [Questions?](#questions)
9. [Code of Conduct](#code-of-conduct)

## Getting Started

### Prerequisites

- **Python 3.12+** - Required for development
- **PostgreSQL** - Testing Database outside of Docker (we recommend [Supabase](https://supabase.com) for easy setup)
- **Git** - Version control
- **UV** - Python package manager (install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork**: `git clone https://github.com/yourusername/watcher.git`
3. **Navigate to the project**: `cd watcher`
4. **Install `uv`** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
5. **Install Python 3.12**
   ```bash
   uv python install 3.12
   ```
6. **Sync Python packages**
   ```bash
   uv sync --frozen --compile-bytecode
   ```
7. **Add pre-commit hooks** (you might need to run `source .venv/bin/activate` if your uv environment is not being recognized)
   ```bash
   pre-commit install --install-hooks
   ```
8. **Set up environment variables**: Copy `.env.example` and configure the environment variables
9. **Run tests**: `make test`

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Test Database Configuration
TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/watcher_test

# Optional: Slack Integration
DEV_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Optional: Logfire Integration
DEV_LOGFIRE_TOKEN=your-logfire-token-here
```

### Development Commands

```bash
# Start development server
make dev-compose

# Run tests
make test

# Format code
make format

# Add database migration
make add-migration msg="description of changes"

# Apply migrations
make trigger-migration
```

### Performance Profiling

Watcher includes built-in performance profiling for development using pyinstrument to help identify bottlenecks and optimize your pipeline operations.

#### On-Demand Profiling

Profile any API endpoint by adding `?profile=true` to the URL:

#### Using Scalar API Docs

1. **Start your app**: `make dev-compose`
2. **Open Scalar**: http://localhost:8000/scalar
3. **Add `?profile=true`** as a query parameter to any endpoint URL in the interface
4. **Execute the request** - you'll get an interactive HTML profile directly in your browser

#### Profile Features

- **Interactive Call Stack**: Click to expand/collapse function calls
- **Timing Breakdown**: See exactly where time is spent
- **Database Operations**: Identify slow queries and connection issues
- **Memory Usage**: Track memory allocation patterns
- **Search & Filter**: Find specific functions or modules

#### Configuration

Profiling is enabled by default in development mode. To disable:

```bash
# Set in your environment
DEV_PROFILING_ENABLED=false
```

## Development Process

### Reporting Issues

When reporting bugs, please include:

- **Environment details**: OS, Docker version, Docker Compose version
- **Steps to reproduce**: Clear, numbered steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Error messages**: Full error logs if applicable
- **Screenshots**: If UI-related issues

### Suggesting Features

For feature requests, please provide:

- **Use case**: Why is this feature needed?
- **Expected behavior**: How should it work?
- **Alternatives considered**: What other approaches were considered?
- **Additional context**: Any other relevant information

### Submitting Changes

1. **Create a feature branch**: `git checkout -b feature/your-feature-name`
2. **Make your changes**: Follow our code standards
3. **Add tests**: Ensure new functionality is tested
4. **Run the test suite**: `make test`
5. **Format your code**: `make format`
6. **Commit your changes**: Use clear, descriptive commit messages
7. **Push to your fork**: `git push origin feature/your-feature-name`
8. **Submit a pull request**: Create a PR with a clear description

## Code Standards

### Python Code

- **Follow PEP 8**: Use `ruff` for linting (configured in `ruff.toml`)
- **Type hints**: Use type annotations for all function parameters and return values
- **Docstrings**: Write clear docstrings for all public functions and classes
    - Working to get the entire codebase up to standards
- **Variable names**: Use descriptive, clear variable names

### Database Code

- **SQLModel**: Use SQLModel for all database models
- **Migrations**: Always create migrations for schema changes
- **Indexes**: Add appropriate indexes for performance
- **Constraints**: Use proper foreign key and check constraints

### API Code

- **FastAPI**: Follow FastAPI best practices
- **Pydantic**: Use Pydantic models for request/response validation
- **Error handling**: Provide clear error messages and appropriate HTTP status codes

### Code Organization

- **File structure**: Follow the existing project structure

## Testing Guidelines

### Test Requirements

- **New features**: Must include tests
- **Bug fixes**: Include tests that reproduce the bug
- **API endpoints**: Test both success and error cases
- **Database operations**: Test with real database operations
- **Edge cases**: Test boundary conditions and error scenarios

### Test Structure

```python
def test_feature_name():
    """Test description of what this test verifies."""
    # Arrange: Set up test fixture data
    # Act: Execute the code being tested
    # Assert: Verify the expected outcome
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest src/tests/routes/test_pipeline.py

# Run specific test
pytest src/tests/routes/test_pipeline.py::test_create_pipeline
```

### Test Data

- **Fixtures**: Use pytest fixtures for common test data
- **Database**: Use test database for all database tests
- **Cleanup**: Ensure tests clean up after themselves
- **Isolation**: Tests should not depend on each other (produce any data needed in the test itself)

## Pull Request Process

### Before Submitting

- [ ] **Tests pass**: All tests must pass locally
- [ ] **Code formatted**: Run `make format` to ensure consistent formatting
- [ ] **Linting clean**: No linting errors or warnings
- [ ] **Documentation updated**: Update relevant documentation in /docs
- [ ] **Commit messages clear**: Use descriptive commit messages
- [ ] **Branch up to date**: Rebase on latest main branch

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or breaking changes documented)
```

### Review Process

1. **Automated checks**: All pre-commit checks must pass
2. **Code review**: At least one maintainer review required
3. **Testing**: Manual testing may be requested
4. **Documentation**: Documentation updates may be required
5. **Feedback**: Address all feedback promptly

### Merge Requirements

- All automated checks pass
- At least one approval from maintainers
- No requested changes pending
- Up to date with main branch

## Issue Guidelines

### Bug Reports

Use this template for bug reports:

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Ubuntu 20.04, macOS, Windows]
- Docker version: [e.g. Docker 24.0.0]
- Docker Compose version: [e.g. Docker Compose 2.20.0]

**Additional context**
Any other context about the problem.
```

### Feature Requests

Use this template for feature requests:

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
A clear description of any alternative solutions.

**Additional context**
Any other context about the feature request.
```

## Recognition

Contributors will be recognized in:

- **CONTRIBUTORS.md**: List of all contributors
- **Release notes**: Mentioned in release announcements
- **Project documentation**: Credited in relevant sections
- **GitHub**: Listed as contributors on the project

## Questions?

- **GitHub Issues**: Open an issue for questions
- **Discussions**: Use GitHub Discussions for general questions
- **Documentation**: Check existing documentation first
- **Code**: Look at existing code for examples

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

---

Thank you for contributing to Watcher! Your contributions help make this project better for everyone.
