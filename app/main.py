from fastapi import FastAPI
from app.routers import urls

app = FastAPI(
    title = "Snipify",
    description = "Real-time URL shortner with analytics",
    version = "1.0.0"
)

app.include_router(urls.router)

@app.get("/")
def home():
    return {"message": "Welcome to Snipify "}

@app.get("/health")
def health():
    return {"status":"ok", "app":"Snipify"}

