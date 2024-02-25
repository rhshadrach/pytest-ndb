import pytest


@pytest.fixture
def fixture_1():
    return "x"


@pytest.fixture
def fixture_2():
    return "y"


def test_basic_passes():
    x = 5
    assert x == 5


def test_basic_fails():
    x = 5
    assert x == 5


def test_fixture_single_passes(fixture_1):
    x = 5
    assert x == 5
    assert fixture_1 == "x"


def test_fixture_single_fails(fixture_1):
    x = 5
    assert x == 5
    assert fixture_1 == "y"


def test_fixture_double_passes(fixture_1, fixture_2):
    x = 5
    assert x == 5
    assert fixture_1 == "x"
    assert fixture_2 == "y"


def test_fixture_double_fails(fixture_1, fixture_2):
    x = 5
    assert x == 5
    assert fixture_1 == "x"
    assert fixture_2 == "x"


@pytest.mark.parametrize("x", [5])
def test_parametrization_passes(x):
    y = "z"
    assert x == 5
    assert y == "z"


@pytest.mark.parametrize("x", [5])
def test_parametrization_fails(x):
    y = "z"
    assert x == 5
    assert y == "w"
