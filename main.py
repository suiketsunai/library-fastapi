# asgi server
import uvicorn

# app settings
from app.settings import settings

if __name__ == "__main__":
    # run server
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
    )
