from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.schemas import ShortenRequest, ShortenResponse, StatsResponse
from app.utils import generate_short_code, validate_url, parse_user_agent
from app.database import get_db
from app.models import Url, Click
from app.cache import (
    get_from_cache,
    set_cache,
    incr_click,
    get_click_count,
)

router = APIRouter()

BASE_URL = "http://localhost:8000"

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post("/shorten", response_model=ShortenResponse)
@limiter.limit("10/minute")
async def shorten_url(
    request: Request,
    payload: ShortenRequest,
    db: AsyncSession = Depends(get_db),
):
    # Validate URL
    if not validate_url(payload.long_url):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL. Must start with http:// or https://",
        )

    # Generate unique short code
    code = generate_short_code()

    while True:
        result = await db.execute(select(Url).where(Url.code == code))
        existing = result.scalar_one_or_none()

        if not existing:
            break

        code = generate_short_code()

    # Save to database
    url = Url(
        code=code,
        long_url=payload.long_url,
    )

    db.add(url)

    await db.commit()
    await db.refresh(url)

    # Cache in Redis
    await set_cache(f"url:{code}", payload.long_url)

    return ShortenResponse(
        short_code=code,
        short_url=f"{BASE_URL}/{code}",
        long_url=url.long_url,
    )


@router.get("/stats/{code}", response_model=StatsResponse)
async def get_stats(
    code: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Url).where(Url.code == code))
    url = result.scalar_one_or_none()

    if not url:
        raise HTTPException(
            status_code=404,
            detail="Short code not found",
        )

    # Get live click count from Redis
    redis_clicks = await get_click_count(code)

    return StatsResponse(
        short_code=url.code,
        long_url=url.long_url,
        click_count=redis_clicks or url.click_count,
        created_at=url.created_at,
    )


@router.get("/{code}")
async def redirect_url(
    request: Request,
    code: str,
    db: AsyncSession = Depends(get_db),
):
    # Check Redis cache first
    long_url = await get_from_cache(f"url:{code}")

    # Fallback to database
    if not long_url:
        result = await db.execute(select(Url).where(Url.code == code))
        url = result.scalar_one_or_none()

        if not url:
            raise HTTPException(
                status_code=404,
                detail="Short code not found",
            )

        long_url = url.long_url

        # Store in Redis cache
        await set_cache(f"url:{code}", long_url)

    # Increment click count in Redis
    await incr_click(code)

    # Parse user agent
    ua_string = request.headers.get("user-agent", "")
    ua_data = parse_user_agent(ua_string)

    # Get client IP
    client_ip = get_remote_address(request)

    # Save analytics
    click = Click(
        code=code,
        ip=client_ip,
        country="IN",  # Replace with real geo lookup later
        device=ua_data["device"],
        browser=ua_data["browser"],
    )

    db.add(click)
    await db.commit()

    # Redirect user
    return RedirectResponse(
        url=long_url,
        status_code=307,
    )
