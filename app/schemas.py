from pydantic import BaseModel
from datetime import datetime


class ShortenRequest(BaseModel):
    long_url: str


class ShortenResponse(BaseModel):
    short_url: str
    long_url: str
    short_code: str


class StatsResponse(BaseModel):
    short_code: str
    long_url: str
    click_count: int
    created_at: datetime