import random 
import string

def generate_random_string(Length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=Length))


def validate_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")

