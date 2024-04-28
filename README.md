# pytest-ndb

Interactively debug a failing pytest test in a notebook or REPL. See `Usage` below for examples.

In our opinion, developers should often prefer to debug failing tests using a debugger such as `pdb`. However for certain applications, such as those that occur in data science with large complex data sets or long running models, this is can be quite difficult. Debugging a failing test can mean having to analyze data, for which there is little support in a debugger and where notebooks truly shine.

Traditionally to debug in a notebook, all of the code from the test, including fixtures and parametrizations, must be copied. For simple tests this might not be an issue, but for a complex test it can be quite time consuming. Instead, you can use `pytest-ndb`!

## Usage

When tests fail, `pytest` will produce a summary of the failures.

```
FAILED pytest_ndb/tests.py::test_fixture_single_fails - AssertionError: assert 'x' == 'y'
FAILED pytest_ndb/tests.py::test_fixture_double_fails - AssertionError: assert 'y' == 'x'
FAILED pytest_ndb/tests.py::test_parametrization_fails[5] - AssertionError: assert 'z' == 'w'
```

When this occurs, you can take the path produced by this summary and feed it into `pytest_ndb.run` in a notebook passing the package and the path.

```python
import pytest_ndb

test_locals = pytest_ndb.run(pytest_ndb, "pytest_ndb/tests.py::test_fixture_single_fails")
```

This produces the following output.

```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-7.4.0, pluggy-1.2.0
rootdir: /home/richard/dev/pytest-ndb
plugins: hypothesis-6.80.0, anyio-3.7.0, asyncio-0.21.0, localserver-0.0.0, cov-4.1.0, xdist-3.3.1, cython-0.2.1
asyncio: mode=strict
collected 1 item
Traceback (most recent call last):
  File "/home/richard/dev/pytest-ndb/pytest_ndb/__init__.py", line 125, in run
    test_function(
  File "/home/richard/dev/pytest-ndb/pytest_ndb/__init__.py", line 30, in __call__
    res = self.func(*args, **kwargs)
  File "/home/richard/dev/pytest-ndb/pytest_ndb/tests.py", line 33, in test_fixture_single_fails
    assert fixture_1 == "y"
AssertionError: assert 'x' == 'y'
```

As the test runs, the local variables are captured and returned as a dictionary. In the above code, this is put in to the variable `test_locals`.

```python
print(test_locals)
{'fixture_1': 'x', 'x': 5}
```

In the notebook, you can now interact with and investigate these Python objects! You can even run tests with parametrizations:

```python
import pytest_ndb

test_locals = pytest_ndb.run(pytest_ndb, "pytest_ndb/tests.py::test_parametrization_fails[5]")
```

## Requirements

`pytest-ndb` requires:

 - At least Python 3.8.
 - pytest between versions `7.0` and `8.2` inclusive. Other versions **may** work.
 - The test path provided to `pytets-ndb` must identify a unique test (only one parametrization).
 - If parametrizations are used, they must be deterministic.

## Installation

```bash
pip install pytest-ndb
```

## Development state

`pytest-ndb` is largely a hack on the `pytest` internals, and likely will always be. In addition, we must guess at the root path of your package, and in certain cases we may guess wrong. While we test this package using parametrizations and fixtures, other `pytest` features may not work.

Is something not working? Report an issue on our [GitHub issue tracker](https://github.com/rhshadrach/pytest-ndb/issues)!
