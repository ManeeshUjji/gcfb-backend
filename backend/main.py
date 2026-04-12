from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

from routers import forecast, dispatch, inventory, sites
from models.model_utils import load_model
from schemas import HealthResponse

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GCFB Operational Intelligence API",
    description="Backend API for the Greater Cleveland Food Bank dashboard",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and their processing time."""
    start_time = datetime.now()
    
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    processing_time = (datetime.now() - start_time).total_seconds()
    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"Status: {response.status_code} Time: {processing_time:.3f}s"
    )
    
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages."""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "body": exc.body
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors gracefully."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if os.getenv("DEBUG", "False") == "True" else "An error occurred processing your request"
        }
    )


@app.on_event("startup")
async def startup_event():
    """Load model and initialize resources on startup."""
    logger.info("Starting GCFB Operational Intelligence API...")
    
    try:
        load_model()
        logger.info("ML model loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load ML model: {e}")
    
    # Initialize database and seed data if empty
    try:
        from db import init_db, get_session, PartnerSite
        init_db()
        logger.info("Database initialized")
        
        # Check if database needs seeding
        session = get_session()
        site_count = session.query(PartnerSite).count()
        
        if site_count == 0:
            logger.info("Database is empty, seeding data...")
            import subprocess
            import sys
            subprocess.run([sys.executable, "data/seed.py"], check=True)
            logger.info("Database seeded successfully")
        else:
            logger.info(f"Database already contains {site_count} partner sites")
            
        session.close()
    except Exception as e:
        logger.warning(f"Database initialization/seeding failed: {e}")
        logger.warning("API will run with limited functionality")
    
    logger.info("API ready to accept requests")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "GCFB Operational Intelligence API",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns API status, database connectivity, and model availability.
    """
    model_loaded = False
    database_status = "unknown"
    
    try:
        load_model()
        model_loaded = True
    except Exception as e:
        logger.warning(f"Model not loaded: {e}")
    
    try:
        from db import get_engine
        from sqlalchemy import text
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        database_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        database_status = "disconnected"
    
    return HealthResponse(
        status="healthy" if model_loaded and database_status == "connected" else "degraded",
        database=database_status,
        ml_model_loaded=model_loaded,
        timestamp=datetime.now()
    )


app.include_router(forecast.router, prefix="/api", tags=["forecast"])
app.include_router(sites.router, prefix="/api", tags=["sites"])
app.include_router(dispatch.router, prefix="/api", tags=["dispatch"])
app.include_router(inventory.router, prefix="/api", tags=["inventory"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
