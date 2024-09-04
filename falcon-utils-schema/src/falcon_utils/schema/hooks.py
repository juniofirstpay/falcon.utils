from typing import Callable, Union
from marshmallow import Schema
from marshmallow_dataclass import dataclass

__all__ = ("validate", "map_query")

def validate(schema: Union[Schema]) -> Callable:
    def hook(req, resp, resource, params):
        if hasattr(schema, 'Schema', False):
            # provided schema is a marshmallow dataclass
            req.context.data = schema.Schema().load(**req.media)
        else:
            req.context.data = schema(**req.media)
    return hook

def map_query(schema: Union[Schema]) -> Callable:
    def hook(req, resp, resource, params):
        if hasattr(schema, 'Schema', False):
            # provided schema is a marshmallow dataclass
            req.context.query = schema.Schema().load(**req.media)
        else:
            req.context.query = schema(**req.media)
    return hook
    

