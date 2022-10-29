# API
from fastapi import FastAPI

# get sqlalchemy functions
from sqlalchemy import select

# get sqlalchemy loading strategy
from sqlalchemy.orm import selectinload

# get event router
from . import events

# get database models
from .db import models

# get async session
from .db.database import ASYNC_SESSION

app = FastAPI()

app.include_router(events.router)


@app.get("/")
async def home_page():
    async with ASYNC_SESSION() as session:
        return {
            "msg": (
                await session.scalars(
                    select(models.Publisher).options(
                        selectinload(models.Publisher.books)
                    )
                )
            ).all()
        }
