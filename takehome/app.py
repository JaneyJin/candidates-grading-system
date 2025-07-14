from pathlib import Path

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from takehome import logger
from takehome.config import settings
from takehome.routes import router

# ============================ Team Matcher Server ============================

# Note to challengers:
# You may add additional files as needed to complete the challenge.

# Docs:
# - FastAPI: https://fastapi.tiangolo.com/

# You may modify this file as needed.

# =============================================================================

MOCK_FLAKY_ENDPOINT = "http://localhost:8001/generate_score"
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Candidate Grading System",
    description="A FastAPI application for managing projects, candidates, and team formation",
    version="1.0.0"
)

templates = Jinja2Templates(directory=Path(BASE_DIR, "templates"))

# 包含API路由
app.include_router(router)


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    logger.info("Secret Key: %s", settings.SECRET_KEY)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/health")
def health_check():
    """健康检查端点"""
    return {"status": "healthy", "message": "Candidate Grading System is running"}
