"""
API роутеры
"""
from fastapi import APIRouter

from app.api import auth, users, projects, ratings, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(ratings.router, prefix="/ratings", tags=["ratings"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])


