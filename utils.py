from __future__ import annotations

from functools import partial
from typing import Any


def dict_mkeys(d: dict[str, Any], *keys: str) -> tuple[Any, ...]:
    """
    Return a tuple of values from a single dictionary.

    Returns a tuple of values, where each value Vn corresponds
    to Kn in *KEYS, such that `V1 = D[K1]`.
    """
    res = map(lambda k: d[k], keys)
    return tuple(res)

def not_zero(*args: int, check_none=False) -> bool:
    """
    Return true if all arguments are not zero.
    """
    if check_none:
        values = map(lambda x: x != 0 and x is not None, args)
    else:
        values = map(lambda x: x != 0, args)
    return all(values)

not_zero_or_none = partial(not_zero, check_none=True)

def subst_none(val: Any | None, alt: Any) -> Any:
    """
    Return VAL unless it is None, otherwise return ALT.
    """
    return alt if val is None else val

def dict_or(d: dict, *keys: Any, default: Any=None) -> tuple[Any, Any]:
    """
    Return one of several keys from D.

    This tries each key in order that they are provided: if one
    is found, `(KEY, VALUE)`. If none of the keys are defined,
    `(None, DEFAULT)` is returned.
    """
    for key in keys:
        if key in d:
            return (key, d[key])
    return (None, default)
