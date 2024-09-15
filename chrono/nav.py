from arcade import View, get_window
from typing import Callable
from weakref import ref, ReferenceType


def _kill_callback(name: str):
    # If a navigation for some reason becomes invalid 99% of the time we want it to get removed.
    def _kill(_):
        get_window().deregister_nav(name)  # type: ignore

    return _kill


class Navigation:

    def navigate(self) -> View:
        raise NotImplementedError


# TODO: Create a Navigation that only works when leaving specific views / objects
# I haven't yet cause a) maybe not needed b) requires weakref


class CreationNavigation(Navigation):
    """
    Navigate to the next view by creating the view
    """

    def __init__(self, tgt: type[View], *tgt_args, **tgt_kwargs) -> None:
        self._tgt: type[View] = tgt
        self._args = tgt_args
        self._kwargs = tgt_kwargs

    def update_args(self, *tgt_args):
        self._args = tgt_args

    def update_kwargs(self, **tgt_kwargs):
        self._kwargs = tgt_kwargs

    def navigate(self) -> View:
        return self._tgt(*self._args, **self._kwargs)


class PreserveNavigation(Navigation):
    """
    Navigate to an exsisting view
    """

    def __init__(self, name: str, tgt: View, callback: Callable) -> None:
        self._tgt: ReferenceType[View] = ref(tgt, _kill_callback(name))
        self._clbk: Callable = callback

    def navigate(self) -> View | None:
        self._clbk()
        return self._tgt()
