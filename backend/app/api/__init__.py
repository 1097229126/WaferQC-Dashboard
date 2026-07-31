"""
Main API router that includes all route modules
"""
from fastapi import APIRouter
from app.api.api import router as api_router

# Export the router for use in main.py
__all__ = ["api_router"]
