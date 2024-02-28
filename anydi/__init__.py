"""AnyDI public objects and functions."""
from typing import Any

from ._container import Container, request, singleton, transient
from ._module import Module, provider
from ._scanner import injectable
from ._types import Marker, Provider, Scope


def dep() -> Any:
    """A marker for dependency injection."""
    return Marker()


__all__ = [
    "Container",
    "Module",
    "Provider",
    "Scope",
    "dep",
    "injectable",
    "provider",
    "request",
    "singleton",
    "transient",
]
