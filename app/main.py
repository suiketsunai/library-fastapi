# API
from fastapi import FastAPI

# redirect
from fastapi.responses import RedirectResponse

# pagination
from fastapi_pagination import add_pagination

# event router
from .routers import events, publishers


app = FastAPI()

app.include_router(events.router)
app.include_router(publishers.router)


@app.get("/", include_in_schema=False)
async def home_page():
    return RedirectResponse("/docs")


add_pagination(app)
