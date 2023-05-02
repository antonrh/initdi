import functools
import inspect
import sys
import typing as t

try:
    import anyio  # noqa

    anyio_installed = True
except ImportError:
    anyio_installed = False


try:
    import lazy_object_proxy  # noqa

    lazy_object_proxy_installed = True
except ImportError:
    lazy_object_proxy_installed = False


HAS_SIGNATURE_EVAL_STR_ARG = sys.version_info > (3, 9)

T = t.TypeVar("T")


def get_full_qualname(obj: t.Any) -> str:
    qualname = getattr(obj, "__qualname__", f"unknown[{type(obj).__qualname__}]")
    module_name = getattr(obj, "__module__", "__main__")
    return f"{module_name}.{qualname}".removeprefix("builtins.")


@functools.lru_cache(maxsize=None)
def get_signature(obj: t.Callable[..., t.Any]) -> inspect.Signature:
    signature_kwargs: t.Dict[str, t.Any] = {}
    if HAS_SIGNATURE_EVAL_STR_ARG:
        signature_kwargs["eval_str"] = True
    return inspect.signature(obj, **signature_kwargs)


def is_builtin_type(tp: t.Type[t.Any]) -> bool:
    return tp.__module__ == "builtins"


def make_lazy(func: t.Callable[..., T], /, *args: t.Any, **kwargs: t.Any) -> T:
    if not lazy_object_proxy_installed:
        raise ImportError(
            "`lazy-object-proxy` library is not currently installed. Please make sure "
            "to install it first, or consider using `pyxdi[full]` instead."
        )
    return t.cast(T, lazy_object_proxy.Proxy(functools.partial(func, *args, **kwargs)))


async def run_async(func: t.Callable[..., T], /, *args: t.Any, **kwargs: t.Any) -> T:
    if not anyio_installed:
        raise ImportError(
            "`anyio` library is not currently installed. Please make sure to install "
            "it first, or consider using `pyxdi[full]` instead."
        )
    return await anyio.to_thread.run_sync(functools.partial(func, *args, **kwargs))
