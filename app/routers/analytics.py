from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.schemas import AnalyticsResponse, CountryCount, DeviceCount
from app.database import get_db
from app.models import Url, Click
from app.cache import get_click_count

router = APIRouter(prefix="/analytics")

@router.get("/{code}", response_model=AnalyticsResponse)
async def get_analytics(code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Url).where(Url.code == code))
    url = result.scalar_one_or_none()

    if not url:
        raise HTTPException(status_code=404, detail="Short code not found")

    # top countries
    country_result = await db.execute(
        select(Click.country, func.count(Click.id).label("count"))
        .where(Click.code == code)
        .group_by(Click.country)
        .order_by(func.count(Click.id).desc())
        .limit(5)
    )
    top_countries = [CountryCount(country=r.country or "unknown", count=r.count)
                     for r in country_result.all()]

    # device breakdown
    device_result = await db.execute(
        select(Click.device, func.count(Click.id).label("count"))
        .where(Click.code == code)
        .group_by(Click.device)
        .order_by(func.count(Click.id).desc())
    )
    devices = [DeviceCount(device=r.device or "unknown", count=r.count)
               for r in device_result.all()]

    redis_clicks = await get_click_count(code)

    return AnalyticsResponse(
        short_code=url.code,
        long_url=url.long_url,
        total_clicks=url.click_count + redis_clicks,
        top_countries=top_countries,
        devices=devices,
        created_at=url.created_at
    )