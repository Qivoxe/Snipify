# Snipify 🔗

> Production-grade URL shortener with real-time analytics, Redis caching, and rate limiting — built with FastAPI.

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat&logo=python)

---

## Features

- **URL Shortening** — Generate a unique 6-character short code for any URL
- **Instant Redirects** — Cache-aside pattern with Redis; redirects served without DB reads after first lookup
- **Real-time Analytics** — Track clicks, devices, browsers, and top countries per link
- **Atomic Click Counting** — Redis `INCR` counters flushed to PostgreSQL every 5 minutes in the background
- **Rate Limiting** — Sliding-window rate limit (10 requests/min per IP) via SlowAPI
- **Auto Docs** — OpenAPI (Swagger UI) at `/docs`, ReDoc at `/redoc`
- **Containerized** — Full Docker + docker-compose setup for one-command local deployment

---

## Sreenshot
<img width="1787" height="892" alt="Screenshot (101)" src="https://github.com/user-attachments/assets/037ba33b-27f1-450d-bbcb-88debcfba3dc" />
<img width="1818" height="882" alt="Screenshot (100)" src="https://github.com/user-attachments/assets/699fa7c2-2234-4f56-93e2-f7e8da8ad926" />
<img width="1920" height="847" alt="Screenshot (99)" src="https://github.com/user-attachments/assets/d4808db5-dc93-45f6-aaea-b6bed99b88e1" />

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI (async) |
| Database | PostgreSQL + SQLAlchemy (async) + Alembic migrations |
| Cache | Redis (cache-aside, atomic INCR) |
| Task Queue | Celery (background click sync) |
| Rate Limiting | SlowAPI |
| Validation | Pydantic v2 |
| Containerization | Docker + docker-compose |

---

## Architecture

```
POST /shorten
  → validate URL
  → generate unique 6-char code
  → save to PostgreSQL
  → cache in Redis (1hr TTL)
  → return short URL

GET /{code}
  → check Redis cache (fast path)
  → fallback to PostgreSQL on cache miss
  → store in Redis for next request
  → INCR click counter atomically in Redis
  → log click metadata (device, browser, country) to DB
  → 307 redirect to original URL

GET /analytics/{code}
  → aggregate clicks from PostgreSQL
  → add live Redis counter (not yet flushed)
  → return total clicks, top countries, device breakdown

Background task (every 5 min)
  → flush Redis click counters → PostgreSQL
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/shorten` | Shorten a URL |
| `GET` | `/{code}` | Redirect to original URL |
| `GET` | `/stats/{code}` | Click count + metadata |
| `GET` | `/analytics/{code}` | Full analytics breakdown |
| `GET` | `/health` | Health check |

---

## Run Locally

### Option 1 — Without Docker (SQLite + local Redis)

```bash
# 1. Clone the repo
git clone https://github.com/Qivoxe/Snipify.git
cd Snipify

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy env file
cp .env.example .env

# 5. Start the server
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs`


## Environment Variables

Copy `.env.example` to `.env` and fill in:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/snipify
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-random-secret-key
APP_ENV=development
```

---

## Project Structure

```
snipify/
├── app/
│   ├── main.py          # FastAPI app, lifespan, background tasks
│   ├── config.py        # Environment variable management
│   ├── database.py      # Async SQLAlchemy engine + session
│   ├── models.py        # ORM models (Url, Click tables)
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── cache.py         # Redis client + helper functions
│   ├── utils.py         # Short code generator, URL validator
│   └── routers/
│       ├── urls.py      # POST /shorten, GET /{code}, GET /stats
│       └── analytics.py # GET /analytics/{code}
├── tests/
│   └── test_urls.py
├── .env.example
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## Key Concepts Demonstrated

- **Cache-aside pattern** — read from cache, fall back to DB, populate cache on miss
- **Atomic operations** — Redis `INCR` ensures no lost clicks under concurrent requests
- **Async Python** — fully async FastAPI + SQLAlchemy + Redis for high throughput
- **Background tasks** — periodic worker syncs counters without blocking requests
- **Rate limiting** — sliding window algorithm prevents API abuse
- **Database migrations** — Alembic versioned schema changes

---

## Author

**Shivam** — [github.com/Qivoxe](https://github.com/Qivoxe)
