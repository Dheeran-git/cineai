from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas import models
from app.models import database as db_models

router = APIRouter()

@router.get("/", response_model=models.Project)
def get_current_project(
    db: Session = Depends(deps.get_db)
):
    # For demo purposes, we return the first project or create one
    project = db.query(db_models.Project).first()
    if not project:
        project = db_models.Project(
            name="The Perimeter",
            description="Sci-fi short film set in an abandoned outpost.",
            settings={"aspect_ratio": "2.39:1", "target_fps": 24}
        )
        db.add(project)
        db.commit()
        db.refresh(project)
    return project

@router.post("/", response_model=models.Project)
def create_project(
    project_in: models.ProjectCreate,
    db: Session = Depends(deps.get_db)
):
    project = db_models.Project(
        name=project_in.name,
        description=project_in.description,
        settings=project_in.settings
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
