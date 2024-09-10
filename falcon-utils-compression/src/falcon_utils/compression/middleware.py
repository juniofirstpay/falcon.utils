import brotli
import json
import falcon.asgi


class Middleware:

    def __init__(self, compression_quality=0):
        self._compression_quality = compression_quality

    async def compress(self, data: bytes):
        return brotli.compress(
            data,
            mode=brotli.BrotliEncoderMode.TEXT,
            quality=self._compression_quality,
        )

    async def process_response(
        self, req, resp: falcon.asgi.Response, resource, req_succeeed
    ):

        if hasattr(req.context, "compress") and req.context.compress == False:
            return

        if req_succeeed:
            try:
                if isinstance(resp.data, bytes):
                    data = await self.compress(resp.data)
                if isinstance(resp.text, str):
                    data = await self.compress(resp.text.encode('utf-8'))
                elif isinstance(resp.media, str):
                    data = await self.compress(resp.media.encode("utf-8"))
                elif isinstance(
                    resp.media,
                    (
                        dict,
                        list,
                    ),
                ):
                    data = await self.compress(json.dumps(resp.media).encode("utf-8"))
                
                resp.data = data
                resp.append_header("content-encoding", "br")
                resp.complete = True
            except Exception as e:
                print(e)


__all__ = ("Middleware",)
