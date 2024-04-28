from __future__ import annotations

import contextlib
import importlib
import sys
import traceback
from pathlib import Path
from typing import Any, Iterator, no_type_check


class _persistent_locals:
    """Decorator to persist local variables of a function.

    From SO: https://stackoverflow.com/q/9186395/10285434
    """

    def __init__(self, func):
        self._locals = {}
        self.func = func

    def __call__(self, *args, **kwargs):
        def tracer(frame, event, arg):
            if event == "return":
                self._locals = frame.f_locals.copy()

        # tracer is activated on next call, return or exception
        sys.setprofile(tracer)
        try:
            # trace the function call
            res = self.func(*args, **kwargs)
        finally:
            # disable tracer and replace with old one
            sys.setprofile(None)
        return res

    @property
    def locals(self):
        return self._locals


@contextlib.contextmanager
def temp_setattr(obj: Any, attr: str, value: Any) -> Iterator[None]:
    """Temporarily set attribute on an object.

    Vendored from pandas.

    Args:
        obj: Object whose attribute will be modified.
        attr: Attribute to modify.
        value: Value to temporarily set attribute to.

    Yields:
        obj with modified attribute.
    """
    old_value = getattr(obj, attr)
    setattr(obj, attr, value)
    try:
        yield obj
    finally:
        setattr(obj, attr, old_value)


@no_type_check
def run(package, test: str) -> dict[str, Any]:
    """Run a pytest test via string and get the local variables of the test.

    Args:
        package: Package that test exists in.
        test: pytest test relative to the root directory of the project. The test
            specified must be a single test (including parametrizations).

    Returns:
        Local variables from the test, regardless if the test succeeds or fails.
    """
    from _pytest.config import _prepareconfig
    from _pytest.config.exceptions import UsageError
    from _pytest.fixtures import FixtureRequest
    from _pytest.main import Session
    from _pytest.runner import SetupState

    # We don't understand what finalizers do, and they seem to cause issues. So far
    # disabling them entirely has worked.
    def disable_finalizers(*args, **kwargs):
        pass

    SetupState.addfinalizer = disable_finalizers
    FixtureRequest._schedule_finalizers = disable_finalizers

    path = (Path(package.__file__).parent / "..").resolve()
    if path.parts[-1] == "src":
        # Go up one more level
        path = path / ".."
    path = path / test

    # Sometimes repo location is read-only
    with temp_setattr(sys, "dont_write_bytecode", True):
        # n0 to disable pytest-xdist; this will raise if xdist is not installed
        config_args = [path]
        if importlib.util.find_spec("xdist") is not None:
            # xdist is available; disable it
            config_args.append("-n0")
        config = _prepareconfig(config_args)
        session = Session.from_config(config)
        config._do_configure()
        config.hook.pytest_sessionstart(session=session)
        try:
            config.hook.pytest_collection(session=session)
        except UsageError as err:
            raise ValueError(f"No tests found for {test}") from err

    # Only one test is supported
    if len(session.items) == 0:
        raise ValueError(f"No tests found with for {test}")
    elif len(session.items) > 1:
        raise ValueError(f"Multiple tests found for {test}")

    item = session.items[0]
    request = item._request

    kwargs = {}
    for name in item.fixturenames:
        kwargs[name] = request.getfixturevalue(name)

    test_function = _persistent_locals(item.function)
    try:
        test_function(**{arg: kwargs[arg] for arg in item._fixtureinfo.argnames})
    except Exception:
        traceback.print_exc()
    finally:
        result = {
            k: v for k, v in test_function.locals.items() if not _is_pytest_internal(k)
        }
        return result


def _is_pytest_internal(name: str) -> bool:
    if name.startswith("@py_assert"):
        return True
    if name.startswith("@py_format"):
        return True
    return False
