import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import requests

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

app = FastAPI(title="Global News Proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

NEWSAPI_BASE = "https://newsapi.org/v2"


def newsapi_get(path: str, params: dict):
    if not NEWSAPI_KEY:
        raise RuntimeError("NEWSAPI_KEY is not set. Obtain a key from https://newsapi.org/")
    headers = {"X-Api-Key": NEWSAPI_KEY}
    resp = requests.get(f"{NEWSAPI_BASE}/{path}", params=params, headers=headers, timeout=10)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/top")
def top_headlines(country: Optional[str] = None, category: Optional[str] = None, q: Optional[str] = None, sources: Optional[str] = None):
    params = {}
    if country:
        params["country"] = country
    if category:
        params["category"] = category
    if q:
        params["q"] = q
    if sources:
        params["sources"] = sources
    # If no filters provided, default to US top headlines to avoid NewsAPI parameter errors
    if not params:
        params["country"] = "us"
    params["pageSize"] = 50
    try:
        data = newsapi_get("top-headlines", params)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(content=data)


@app.get("/api/search")
def everything(q: str, language: Optional[str] = None, from_param: Optional[str] = None, to: Optional[str] = None):
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter `q` is required")
    params = {"q": q, "pageSize": 50}
    if language:
        params["language"] = language
    if from_param:
        params["from"] = from_param
    if to:
        params["to"] = to
    try:
        data = newsapi_get("everything", params)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(content=data)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
