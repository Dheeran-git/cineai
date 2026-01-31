from fastapi import APIRouter, Depends
from app.services.orchestrator import orchestrator

router = APIRouter()

@router.get("/status/{take_id}")
async def get_processing_status(take_id: int):
    return await orchestrator.get_status(take_id)

@router.post("/start/{take_id}")
async def start_processing(take_id: int):
    # In a real app, this would be a background task or celery task
    # For now, we return that it's started
    import asyncio
    asyncio.create_task(orchestrator.process_take(take_id))
    return {"message": "Processing started", "take_id": take_id}
