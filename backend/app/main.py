"""
SkyBus FastAPI Application Entry Point.
Main application configuration, middleware, and router registration.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import time
import os

from app.config import settings
from app.database import create_tables
from app.routers import auth, routes, buses, bookings, payments, users, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    create_tables()
    logger.info("Database tables created/verified")
    yield
    # Shutdown
    logger.info("Shutting down SkyBus API")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="SkyBus Intercity Bus Booking Platform API",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions gracefully."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred. Please try again later."
        },
    )


# Register routers
app.include_router(auth.router)
app.include_router(routes.router)
app.include_router(buses.router)
app.include_router(bookings.router)
app.include_router(payments.router)
app.include_router(users.router)
app.include_router(admin.router)


# ============================================================
# Serve React Frontend (Production)
# ============================================================

frontend_dist = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "static"
)

if os.path.exists(frontend_dist):

    assets_dir = os.path.join(frontend_dist, "assets")

    if os.path.exists(assets_dir):
        app.mount(
            "/assets",
            StaticFiles(directory=assets_dir),
            name="static-assets"
        )

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        """
        Serve React frontend for all non-API routes.
        """
        # Skip API endpoints
        if (
            full_path.startswith("api")
            or full_path.startswith("docs")
            or full_path.startswith("redoc")
            or full_path.startswith("openapi.json")
            or full_path.startswith("assets")
            or full_path.startswith("health")
        ):
            return JSONResponse(
                status_code=404,
                content={"detail": "Not Found"}
            )

        index_path = os.path.join(frontend_dist, "index.html")

        if os.path.exists(index_path):
            return FileResponse(index_path)

        return JSONResponse(
            status_code=404,
            content={"detail": "Frontend build not found"}
        )


# Health check endpoint
@app.get("/", tags=["Health"])
def root():
    """API root - health check."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.APP_VERSION,
    }


# Coupon validation endpoint (public-facing)
@app.post("/api/coupons/validate", tags=["Coupons"])
def validate_coupon_endpoint(
    code: str,
    amount: float,
    route_id: int = None,
):
    """
    Validate a coupon code (requires authentication handled in frontend).
    This is a simplified endpoint for coupon preview.
    """
    from app.database import SessionLocal
    from app.services.coupon_service import validate_coupon

    db = SessionLocal()

    try:
        # For preview, use user_id=0 (actual validation happens during booking)
        result = validate_coupon(
            code=code,
            amount=amount,
            user_id=0,
            route_id=route_id,
            db=db,
        )
        return result

    finally:
        db.close()
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment verification."""
    return {"status": "ok"}
