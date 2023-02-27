import threading
import typing as t

from .core import Provider
from .types import ProviderObj, Scope

T = t.TypeVar("T")

_lock = threading.RLock()


def transient(target: T) -> T:
    setattr(target, "__pyxdi_scope__", "transient")
    return target


def request(target: T) -> T:
    setattr(target, "__pyxdi_scope__", "request")
    return target


def singleton(target: T) -> T:
    setattr(target, "__pyxdi_scope__", "singleton")
    return target


@t.overload
def provider(
    func: None = ...,
    *,
    scope: t.Optional[Scope] = None,
    override: bool = False,
) -> t.Callable[..., t.Any]:
    ...


@t.overload
def provider(
    func: ProviderObj,
    *,
    scope: t.Optional[Scope] = None,
    override: bool = False,
) -> t.Callable[[ProviderObj], t.Any]:
    ...


def provider(
    func: t.Union[ProviderObj, None] = None,
    *,
    scope: t.Optional[Scope] = None,
    override: bool = False,
) -> t.Union[ProviderObj, t.Callable[[Provider], t.Any]]:
    def decorator(target: T) -> T:
        setattr(
            target,
            "__pyxdi_provider__",
            {
                "scope": scope,
                "override": override,
            },
        )
        return target

    if func is None:
        return decorator
    return decorator(func)


def inject(target: T) -> T:
    setattr(target, "__pyxdi_inject__", True)
    return target
