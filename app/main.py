# API
from fastapi import FastAPI, status

# exceptions
from fastapi.exceptions import RequestValidationError

# redirect & json response
from fastapi.responses import JSONResponse, RedirectResponse

# pagination
from fastapi_pagination import add_pagination

# event router
from .routers import authors, books, publishers

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc):
    for err in exc.errors():
        err["msg"] = err["msg"].capitalize() + "."
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


app.include_router(publishers.router)
app.include_router(authors.router)
app.include_router(books.router)


@app.get("/", include_in_schema=False)
async def home_page():
    return RedirectResponse("/docs")


add_pagination(app)
