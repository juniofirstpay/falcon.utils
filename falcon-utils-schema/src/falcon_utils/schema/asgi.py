from typing import Callable, Union
from marshmallow import Schema
from marshmallow_dataclass import dataclass

__all__ = ("map_data", "map_query")

def map_data(schema: Union[Schema]) -> Callable:
    async def hook(req, resp, resource, params):
        media = await req.media
        if hasattr(schema, 'Schema'):
            # provided schema is a marshmallow dataclass
            req.context.data = schema.Schema().load(media)
        else:
            req.context.data = schema(**media)
    return hook

def map_query(schema: Union[Schema]) -> Callable:
    async def hook(req, resp, resource, params):
        media = req.params
        
        if hasattr(schema, 'Schema'):
            # provided schema is a marshmallow dataclass
            req.context.query = schema.Schema().load(media)
        else:
            req.context.query = schema(**media)
    return hook
    

