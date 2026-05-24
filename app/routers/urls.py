from fastapi import APIRouter, HTTPException
from app.schemas import ShortenRequest, ShortenResponse, StatsResponse
from app.utils import generate_short_code, validate_url
from datetime import datetime

router = APIRouter()

url_store: dict = {}
click_store: dict = {}

BASE_URL = "http://localhost:8000/"

@router.post("/shorten", response_model=ShortenResponse)
def shorten_url(request: ShortenRequest):
    if not validate_url(request.long_url):
        raise HTTPException(status_code=400, detail="Invalid URL. Must start with http:// or https://")

    code = generate_short_code()
    url_store[code] = {
        "long_url": request.long_url,
        "created_at": datetime.utcnow(),
    }
    click_store[code] = 0

    return ShortenResponse(
        short_code=code,
        short_url=f"{BASE_URL}/{code}",
        long_url=request.long_url
    )

@router.get("/stats/{code}", response_model=StatsResponse)
def get_stats(code: str):
    if code not in url_store:
        raise HTTPException(status_code=404, detail="Short code not found")

    return StatsResponse(
        short_code=code,
        long_url=url_store[code]["long_url"],
        click_count=click_store[code],
        created_at=url_store[code]["created_at"]
    )

@router.get("/{code}")
def redirect(code: str):
    if code not in url_store:
        raise HTTPException(status_code=404, detail="Short code not found")

    click_store[code] += 1
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=url_store[code]["long_url"], status_code=307)
