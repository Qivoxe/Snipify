import random
import string
from user_agents import parse

def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))

def validate_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")

def parse_user_agent(ua_string: str) -> dict:
    ua = parse(ua_string)
    if ua.is_mobile:
        device = "mobile"
    elif ua.is_tablet:
        device = "tablet"
    else:
        device = "desktop"
    return {
        "device": device,
        "browser": ua.browser.family
    }