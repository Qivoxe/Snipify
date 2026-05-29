from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.routers import urls, analytics
from app.database import engine, Base
from app.cache import get_redis
import asyncio

limiter = Limiter(key_func=get_remote_address)

async def sync_clicks_to_db():
    from app.cache import get_redis
    from app.database import AsyncSessionLocal
    from app.models import Url
    from sqlalchemy import select


    while True:
        await asyncio.sleep(300)
        try:
            r = await get_redis
            keys = await r.keys("clicks:")
            if not keys:
                continue

            async with AsyncSessionLocal() as db:
                for key in keys:
                    code = key.split(":")[1]
                    if count:
                        result = await db.execute(select(Url).where(Url.code == code))
                        url = result.scalar_one_or_none()
                        if url:
                            url.click_count += int(count)
                await db.commit()
        except Exception as e:
            print(f"Sync error: {e}")    


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
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(urls.router)
app.include_router(analytics.router)


@app.get("/")
def home():
    return {"message": "Welcome to Snipify"}


@app.get("/health")
def health():
    return {"status": "ok", "app": "Snipify"}


