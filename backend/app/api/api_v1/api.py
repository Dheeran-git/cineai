from fastapi import APIRouter
from app.api.api_v1.endpoints import projects, media, processing, timeline, export, script, intelligence, training, search

api_router = APIRouter()
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(media.router, prefix="/media", tags=["media"])
api_router.include_router(processing.router, prefix="/processing", tags=["processing"])
api_router.include_router(timeline.router, prefix="/timeline", tags=["timeline"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(script.router, prefix="/script", tags=["script"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])
api_router.include_router(training.router, prefix="/training", tags=["training"])
api_router.include_router(search.router, prefix="/search", tags=["semantic-search"])
