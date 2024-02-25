import pytest

import pytest_ndb

from . import package


def test_basic_passes():
    expected = {"x": 5}
    result = pytest_ndb.run(package, "package/tests.py::test_basic_passes")
    assert result == expected


def test_basic_fails():
    expected = {"x": 5}
    result = pytest_ndb.run(package, "package/tests.py::test_basic_fails")
    assert result == expected


def test_incorrect_path():
    msg = "No tests found for package/tests.py::test_foo"
    with pytest.raises(ValueError, match=msg):
        pytest_ndb.run(package, "package/tests.py::test_foo")


def test_fixture_single_passes():
    path = "package/tests.py::test_fixture_single_passes"
    expected = {"fixture_1": "x", "x": 5}
    result = pytest_ndb.run(package, path)
    assert result == expected


def test_fixture_single_fails():
    path = "package/tests.py::test_fixture_single_fails"
    expected = {"fixture_1": "x", "x": 5}
    result = pytest_ndb.run(package, path)
    assert result == expected


def test_fixture_double_passes():
    path = "package/tests.py::test_fixture_double_passes"
    expected = {"fixture_1": "x", "fixture_2": "y", "x": 5}
    result = pytest_ndb.run(package, path)
    assert result == expected


def test_fixture_double_fails():
    path = "package/tests.py::test_fixture_double_fails"
    expected = {"fixture_1": "x", "fixture_2": "y", "x": 5}
    result = pytest_ndb.run(package, path)
    assert result == expected


def test_parametrization_passes():
    path = "package/tests.py::test_parametrization_passes[5]"
    expected = {"x": 5, "y": "z"}
    result = pytest_ndb.run(package, path)
    assert result == expected


def test_parametrization_fails():
    path = "package/tests.py::test_parametrization_fails[5]"
    expected = {"x": 5, "y": "z"}
    result = pytest_ndb.run(package, path)
    assert result == expected
