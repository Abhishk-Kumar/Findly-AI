from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import get_settings
from backend.app.database.session import init_db
from backend.app.api.router import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite tables
    await init_db()
    yield


app = FastAPI(
    title="Findly AI Research Workspace API",
    description="Production-grade Autonomous AI Research Engine with LangGraph, Groq, and Multi-Source Intelligence",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler for clean structured errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = str(exc)
    # Sanitize any accidental sensitive substrings
    for key in ("gsk_", "tvly-", "Bearer "):
        if key in error_msg:
            error_msg = "A service provider authentication error occurred."

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": error_msg or "An unexpected internal server error occurred.",
            "type": exc.__class__.__name__,
        },
    )


# Health Check
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "2.0.0",
    }


# Include API routes
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
