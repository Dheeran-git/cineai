from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas import models as schemas
from app.models import database as models
import shutil
import os
from app.core.config import settings

router = APIRouter()

@router.post("/upload", response_model=schemas.Take)
async def upload_media(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db)
):
    print(f"DEBUG: Received upload request for file: {file.filename}")
    # Ensure storage path exists
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    
    file_path = os.path.join(settings.STORAGE_PATH, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create take record
    # For demo, we assume scene 12
    scene = db.query(models.Scene).filter(models.Scene.number == 12).first()
    if not scene:
        # Create default scene-take if not exists for demo
        project = db.query(models.Project).first()
        if not project:
            project = models.Project(name="The Perimeter")
            db.add(project)
            db.commit()
            db.refresh(project)
        
        scene = models.Scene(project_id=project.id, number=12, name="Abandoned Outpost")
        db.add(scene)
        db.commit()
        db.refresh(scene)

    take = models.Take(
        scene_id=scene.id,
        number=1, # Should be incremented in real app
        file_path=file_path,
        file_name=file.filename,
        file_size=os.path.getsize(file_path),
        duration=0.0, # Will be set by processing
        ai_metadata={},
        ai_reasoning={}
    )
    db.add(take)
    db.commit()
    db.refresh(take)
    
    # Trigger AI Pipeline
    from app.services.orchestrator import orchestrator
    background_tasks.add_task(orchestrator.process_take, take.id)
    
    return take

@router.get("/", response_model=List[schemas.Take])
async def get_takes(
    db: Session = Depends(deps.get_db)
):
    return db.query(models.Take).all()
