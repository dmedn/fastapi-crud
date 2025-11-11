import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core import settings
from app.api import router as api_router
from app.core.models import db_helper

# print(settings.db.url)
# print(db_helper)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(settings.db.url)
    print(db_helper)
    yield
    print(settings.db.url)
    print(db_helper)
    await db_helper.dispose()


main_app = FastAPI(lifespan=lifespan)
main_app.include_router(api_router, prefix=settings.api.prefix)

if __name__ == '__main__':
    uvicorn.run("main:main_app", port=settings.run.port, host=settings.run.host, reload=True)
