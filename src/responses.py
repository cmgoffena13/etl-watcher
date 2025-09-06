import orjson
from fastapi.responses import JSONResponse


class ORJSONResponse(JSONResponse):
    """
    Function to convert JSON directly to bytes.
    Faster Serialization than default.
    Requester needs to use orjson to decode.
    """

    media_type = "application/json"

    def render(self, content) -> bytes:
        return orjson.dumps(content)
