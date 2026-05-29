from pydantic import BaseModel
from datetime import datetime

class ShortenRequest(BaseModel):
    long_url: str

class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    long_url: str

class StatsResponse(BaseModel):
    short_code: str
    long_url: str
    click_count: int
    created_at: datetime

class CountryCount(BaseModel):
    country: str
    count: int

class DeviceCount(BaseModel):
    device: str
    count: int

class AnalyticsResponse(BaseModel):
    short_code: str
    long_url: str
    total_clicks: int
    top_countries: list[CountryCount]
    devices: list[DeviceCount]
    created_at: datetime