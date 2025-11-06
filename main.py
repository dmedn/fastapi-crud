import uvicorn
from fastapi import FastAPI
from core import settings
from api import router as api_router

app = FastAPI()
app.include_router(api_router, prefix=settings.api.prefix)

if __name__ == '__main__':
    uvicorn.run("main:app", port=settings.run.port, host=settings.run.host, reload=True)
