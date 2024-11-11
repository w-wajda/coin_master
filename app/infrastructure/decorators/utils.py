from collections.abc import Callable
from functools import (
    partial,
    wraps,
)
from inspect import (
    Parameter,
    signature,
)
from typing import (
    Any,
    ParamSpec,
    TypeVar,
    cast,
)


P = ParamSpec("P")
RT = TypeVar("RT")


def _fastapi_update_wrapper(wrapper: Callable[..., Any], wrapped: Callable[P, RT]) -> Callable[P, RT]:
    wrapped_signature = signature(wrapped)
    wrapped_parameters = list(signature(wrapped).parameters.values())
    wrapper_parameters = [
        param
        # omit *args and **kwargs
        for param in signature(wrapper).parameters.values()
        if param.kind not in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD)
    ]
    combined_parameters = wrapped_parameters + wrapper_parameters

    wrapper = wraps(wrapped)(wrapper)

    wrapper.__signature__ = wrapped_signature.replace(  # type: ignore
        parameters=combined_parameters,
    )

    return cast(Callable[P, RT], wrapper)


def fastapi_wraps(wrapped: Callable[P, RT]) -> Callable[[Callable[..., Any]], Callable[P, RT]]:
    return partial(_fastapi_update_wrapper, wrapped=wrapped)  # type: ignore
