from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import urls
from app.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield


    await engine.dispose()


app = FastAPI(
    title="Snipify",
    description="Real-time URL shortner with analytics",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(urls.router)


@app.get("/")
def home():
    return {"message": "Welcome to Snipify"}


@app.get("/health")
def health():
    return {"status": "ok", "app": "Snipify"}


