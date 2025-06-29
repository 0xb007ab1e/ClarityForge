"""API module for ClarityForge."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .v1.endpoints import router as v1_router

# Create FastAPI application
app = FastAPI(
    title="ClarityForge API",
    description="API for the ClarityForge application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 router
app.include_router(v1_router)


# Health endpoint at root level
@app.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to ClarityForge API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/healthz",
    }
