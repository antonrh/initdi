"""PyxDI FastAPI extension."""
import typing as t

from fastapi import Depends, FastAPI, params
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute
from starlette.requests import Request

from pyxdi import PyxDI
from pyxdi.utils import get_signature

from .starlette.middleware import RequestScopedMiddleware
from .utils import HasInterface, patch_parameter_interface

__all__ = ["RequestScopedMiddleware", "install", "get_di", "Inject"]


def install(app: FastAPI, di: PyxDI) -> None:
    """Install PyxDI into a FastAPI application.

    Args:
        app: The FastAPI application instance.
        di: The PyxDI container.

    This function installs the PyxDI container into a FastAPI application by attaching
    it to the application state. It also patches the route dependencies to inject the
    required dependencies using PyxDI.
    """
    app.state.di = di  # noqa

    patched = []

    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        for dependant in _iter_dependencies(route.dependant):
            if dependant.cache_key in patched:
                continue
            patched.append(dependant.cache_key)
            call, *params = dependant.cache_key
            if not call:
                continue  # pragma: no cover
            for parameter in get_signature(call).parameters.values():
                patch_parameter_interface(call, parameter, di)


def get_di(request: Request) -> PyxDI:
    """Get the PyxDI container from a FastAPI request.

    Args:
        request: The FastAPI request.

    Returns:
        The PyxDI container associated with the request.
    """
    return t.cast(PyxDI, request.app.state.di)


class GetInstance(params.Depends, HasInterface):
    """Parameter dependency class for injecting dependencies using PyxDI."""

    def __init__(self) -> None:
        super().__init__(dependency=self._dependency, use_cache=True)
        HasInterface.__init__(self)

    async def _dependency(self, di: PyxDI = Depends(get_di)) -> t.Any:
        return await di.aget_instance(self.interface)


def Inject() -> t.Any:  # noqa
    """Decorator for marking a function parameter as requiring injection.

    The `Inject` decorator is used to mark a function parameter as requiring injection
    of a dependency resolved by PyxDI.

    Returns:
        The `InjectParam` instance representing the parameter dependency.
    """
    return GetInstance()


def _iter_dependencies(dependant: Dependant) -> t.Iterator[Dependant]:
    """Iterate over the dependencies of a dependant."""
    yield dependant
    if dependant.dependencies:
        for sub_dependant in dependant.dependencies:
            yield from _iter_dependencies(sub_dependant)
