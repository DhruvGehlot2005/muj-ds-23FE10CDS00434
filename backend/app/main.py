"""
@file main.py
@description FastAPI application entry point with CORS, Rate Limiting, and Security Headers
@module backend.app.main
"""

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.app.api.routes import limiter, router
from backend.app.config import settings
from backend.app.utils.logger import logger

app = FastAPI(
    title="ResLens: AI Resume Analyzer & Job Compatibility Assessment API",
    description="NLP-powered resume evaluation, target-role alignment, and job description matching system",
    version="1.0.0",
)

# Attach rate limiter to app state
app.state.limiter = limiter


# Custom 429 handler matching system error specification
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Returns standardized JSON error response on rate limit breach."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "RATE_LIMIT_EXCEEDED",
            "message": "Too many requests. Please try again later.",
            "details": {"retry_after": "60s"},
        },
        headers={"Retry-After": "60"},
    )


# Custom HTTPException handler matching system error specification
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Ensures all HTTP exceptions conform to the strict API error contract."""
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "message": str(exc.detail),
            "details": {},
        },
    )


# CORS configuration
allowed_origins = [
    settings.frontend_url,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://[::1]:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Injects essential OWASP security headers into all responses."""
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# Include API routes
app.include_router(router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint verifying API availability."""
    return {
        "name": "AI Resume Analyzer API",
        "status": "online",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {settings.backend_host}:{settings.backend_port}")
    uvicorn.run(
        "backend.app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
