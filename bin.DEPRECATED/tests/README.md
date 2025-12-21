# Brick Configuration System Tests

This directory contains comprehensive unit tests for all Python modules in the `bin.DEPRECATED/` directory.

## Test Coverage

The test suite covers:

- **test_globals.py** - Tests for global constants and utilities (`lib/globals.py`)
- **test_stats.py** - Tests for statistics tracking (`lib/stats.py`)
- **test_brick.py** - Tests for the Brick class (`lib/brick.py`)
- **test_generate.py** - Tests for parametric brick generation (`lib/generate.py`)
- **test_remix.py** - Tests for STL file remixing (`lib/remix.py`)
- **test_bricks.py** - Tests for the main orchestration class (`lib/bricks.py`)
- **test_configure.py** - Tests for the configuration script (`configure.py`)

## Running Tests

### Run all tests
```bash
cd bin.DEPRECATED/tests
python run_tests.py
```

### Run with verbose output
```bash
python run_tests.py -v
```

### Run a specific test module
```bash
python run_tests.py test_brick
# or
python run_tests.py brick
```

### Run with minimal output
```bash
python run_tests.py -q
```

### Run using unittest directly
```bash
# Run all tests
python -m unittest discover -s bin.DEPRECATED/tests -p "test_*.py"

# Run specific test file
python -m unittest bin.DEPRECATED.tests.test_brick

# Run specific test class
python -m unittest bin.DEPRECATED.tests.test_brick.TestBrick

# Run specific test method
python -m unittest bin.DEPRECATED.tests.test_brick.TestBrick.test_brick_creation_with_defaults
```

## Test Structure

Each test module follows this structure:

1. **Module docstring** - Describes what is being tested
2. **Imports** - Standard library, unittest, mocks, and module under test
3. **Test classes** - One or more TestCase classes
4. **setUp/tearDown** - Fixtures for test setup and cleanup
5. **Test methods** - Individual test cases starting with `test_`

## Testing Best Practices

### Assertions
- Use specific assertions (`assertEqual`, `assertIsInstance`, etc.)
- Include descriptive failure messages
- Test both success and failure cases

### Mocking
- Use `unittest.mock` for external dependencies
- Mock file I/O, network calls, and system calls
- Isolate units under test

### Coverage
- Test normal operation
- Test edge cases
- Test error handling
- Test parameter validation

## Common Test Patterns

### Testing a function
```python
def test_function_name(self):
    """Function should do expected behavior."""
    result = function_under_test(arg1, arg2)
    self.assertEqual(result, expected_value)
```

### Testing exceptions
```python
def test_invalid_input_raises(self):
    """Function should raise ValueError for invalid input."""
    with self.assertRaises(ValueError) as context:
        function_under_test(invalid_arg)
    self.assertIn('error message', str(context.exception))
```

### Testing with mocks
```python
@patch('module.external_dependency')
def test_with_mock(self, mock_dep):
    """Function should call external dependency correctly."""
    mock_dep.return_value = 'mocked result'
    result = function_under_test()
    mock_dep.assert_called_once()
```

## Dependencies

Tests require:
- Python 3.10+ (for match/case statements)
- unittest (standard library)
- unittest.mock (standard library)
- numpy (for remix tests with STL mocking)

## Continuous Integration

To integrate with CI/CD:

```bash
# Run tests with coverage
python -m coverage run -m unittest discover -s bin.DEPRECATED/tests
python -m coverage report
python -m coverage html
```

## Contributing

When adding new functionality:

1. Write tests first (TDD approach)
2. Ensure tests pass before committing
3. Maintain >80% code coverage
4. Document test purpose in docstrings
5. Use descriptive test names

## Troubleshooting

### Import errors
If you get import errors, ensure you're running from the correct directory:
```bash
cd /home/harald/3d/bricks
python bin.DEPRECATED/tests/run_tests.py
```

### Mock issues
If mocks aren't working as expected:
- Check the patch path matches the import path
- Use `patch.object` for instance methods
- Remember mocks are checked in reverse order of decorators

### Test failures
- Read the full traceback
- Check test assumptions against actual code
- Verify test data is valid
- Use `-v` flag for more details
