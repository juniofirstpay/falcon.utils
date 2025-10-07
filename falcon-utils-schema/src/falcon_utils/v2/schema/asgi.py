import dataclasses
import falcon.asgi
from collections.abc import Callable, Mapping, Sequence
from typing import Any, TypeVar


T = TypeVar("T")

marshmallow_available = False
marshmallow_dataclass_available = False
pydantic_available = False
unflatten_available = False

try:
    import marshmallow

    marshmallow_available = True
except ImportError:
    pass

try:
    import marshmallow_dataclass

    marshmallow_dataclass_available = True
except ImportError as e:
    pass

try:
    import pydantic

    pydantic_available = True
except ImportError:
    pass

if not any(
    (pydantic_available, marshmallow_dataclass_available, marshmallow_available)
):
    raise Exception("no schema validators installed")

try:
    import unflatten

    unflatten_available = True
except ImportError:
    pass


async def map_data(
    req: falcon.asgi.Request,
    resp: falcon.asgi.Response,
    resource: object,
    params: Mapping[str, Any],
    *,
    schema: type[T],
    context: Mapping[str, Any] | Callable[..., Mapping[str, Any]] | None = None,
    raise_ex: bool = True,
):
    if pydantic_available and issubclass(schema, pydantic.BaseModel):
        try:
            req.context.data = schema.model_validate(await req.media, context=context)
        except pydantic.ValidationError as e:
            if raise_ex:
                raise e
            else:
                req.context.validation_err = e
    elif (
        marshmallow_dataclass_available
        and dataclasses.is_dataclass(schema)
        and hasattr(schema, "Schema")
    ):
        try:
            req.context.data = schema.Schema().load(await req.media)
        except marshmallow.ValidationError as e:
            if raise_ex:
                raise e
            else:
                req.context.validation_err = e
    elif marshmallow_available and issubclass(schema, marshmallow.Schema):
        try:
            req.context.data = schema().load(await req.media)
        except marshmallow.ValidationError as e:
            if raise_ex:
                raise e
            else:
                req.context.validation_err = e


async def map_query(
    req: falcon.asgi.Request,
    resp: falcon.asgi.Response,
    resource: object,
    params: Mapping[str, Any],
    *,
    schema: type[T],
    fields: Sequence[str] | None = None,
    context: Mapping[str, Any] | Callable[..., Mapping[str, Any]] | None = None,
    raise_ex: bool = True,
):
    if unflatten_available:
        params = unflatten.unflatten(req.params)
    else:
        params = req.params

    if fields:
        params = dict(
            [(field, params.get(field)) for field in fields if field in params]
        )

    if pydantic_available and issubclass(schema, pydantic.BaseModel):
        try:
            req.context.query = schema.model_validate(params, context=context)
        except pydantic.ValidationError as e:
            if raise_ex:
                raise e
            else:
                req.context.validation_err = e
    elif (
        marshmallow_dataclass_available
        and dataclasses.is_dataclass(schema)
        and hasattr(schema, "Schema")
    ):
        try:
            req.context.query = schema.Schema().load(params)
        except marshmallow.ValidationError as e:
            if raise_ex:
                raise e
            else:
                req.context.validation_err = e
    elif marshmallow_available and issubclass(schema, marshmallow.Schema):
        try:
            req.context.query = schema().load(params)
        except marshmallow.ValidationError as e:
            if raise_ex:
                raise e
            else:
                req.context.validation_err = e
