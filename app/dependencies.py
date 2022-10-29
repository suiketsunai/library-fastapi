# json response
from fastapi.responses import JSONResponse

# creating session
from sqlalchemy.ext.asyncio import AsyncSession

# get schema
from .db import schemas

# database
from .db.database import ASYNC_SESSION

# define nor found response
response_404 = {404: {"model": schemas.Message}}

# get async session
async def get_session() -> AsyncSession:
    async with ASYNC_SESSION() as session:
        yield session


# get json error response
def error_json_response(
    code: int,
    message: str,
    error_type: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=code,
        content={
            "detail": [
                {
                    "msg": message,
                    "type": error_type,
                }
            ]
        },
    )
