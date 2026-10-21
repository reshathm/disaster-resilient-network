from functools import wraps
from inspect import signature
from typing import Callable

from fastapi.routing import APIRoute

from app.state import ApplicationState


class LockedRoute(APIRoute):
    """Execute synchronous API endpoints under the shared state lock."""

    def __init__(self, path: str, endpoint: Callable, **kwargs):
        endpoint_signature = signature(endpoint)
        state_parameter = next(
            (
                name
                for name, parameter in endpoint_signature.parameters.items()
                if parameter.annotation is ApplicationState
                or getattr(parameter.annotation, "__origin__", None)
                is ApplicationState
            ),
            "state",
        )

        @wraps(endpoint)
        def locked_endpoint(*args, **kwargs):
            bound = endpoint_signature.bind(*args, **kwargs)
            state = bound.arguments[state_parameter]
            with state.lock:
                return endpoint(*args, **kwargs)

        super().__init__(
            path=path,
            endpoint=locked_endpoint,
            **kwargs,
        )
