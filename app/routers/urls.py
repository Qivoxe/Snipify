from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas import ShortenRequest, ShortenResponse, StatsResponse
from app.utils import generate_short_code, validate_url
from app.database import get_db
from app.models import Url
from app.cache import get_from_cache, set_cache, incr_click, get_click_count




router = APIRouter()
BASE_URL = "http://localhost:8000"

@router.post("/shorten", response_model=ShortenResponse)
async def shorten_url(request: ShortenRequest, db: AsyncSession = Depends(get_db)):
    if not validate_url(request.long_url):
        raise HTTPException(status_code=400, detail="Invalid URL. Must start with http:// or https://")

    code = generate_short_code()


    while True:
        result = await db.execute(select(Url).where(Url.code == code))
        if not result.scalar_one_or_none():
            break
        code = generate_short_code()

    url = Url(code=code, long_url=request.long_url)
    db.add(url)
    await db.commit()
    await db.refresh(url)

# cache the mapping 
    await set_cache(f"url:{code}", request.long_url)


    return ShortenResponse(
        short_code=code,
        short_url=f"{BASE_URL}/{code}",
        long_url=url.long_url
    )

@router.get("/stats/{code}", response_model=StatsResponse)
async def get_stats(code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Url).where(Url.code == code))
    url = result.scalar_one_or_none()

    if not url:
        raise HTTPException(status_code=404, detail="Short code not found")

    # live count 
    redis_clicks = await get_click_count(code)

    return StatsResponse(
        short_code=url.code,
        long_url=url.long_url,
        click_count=url.click_count,
        created_at=url.created_at
    )

@router.get("/{code}")
async def redirect(code: str, db: AsyncSession = Depends(get_db)):
    # check Redis cache first
    long_url = await get_from_cache(f"url:{code}")

    if not long_url:
        
        result = await db.execute(select(Url).where(Url.code == code))
        url = result.scalar_one_or_none()
        if not url:
            raise HTTPException(status_code=404, detail="Short code not found")
        long_url = url.long_url
        
        await set_cache(f"url:{code}", long_url)

   
    await incr_click(code)

    return RedirectResponse(url=long_url, status_code=307)
