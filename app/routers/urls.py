from fastapi import APIRouter, HTTPException
from app.schemas import ShortenRequest, ShortenResponse, StatsResponse
from app.utils import generate_short_code, validate_url
from datetime import datetime

router = APIRouter()

url_store: dict = {}
click_store: dict = {}

BASE_URL = "http://localhost:8000/"
