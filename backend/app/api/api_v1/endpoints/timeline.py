from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.services.timeline_service import timeline_service
from app.models import database as models

router = APIRouter()

@router.get("/")
def get_timeline(db: Session = Depends(deps.get_db)):
    project = db.query(models.Project).first()
    if not project:
        raise HTTPException(status_code=404, detail="No project found")
    
    return timeline_service.assemble_ai_rough_cut(project.id, db)

@router.post("/override/{take_id}")
def override_take(
    take_id: int, 
    is_accepted: str, 
    notes: str = None, 
    db: Session = Depends(deps.get_db)
):
    take = db.query(models.Take).get(take_id)
    if not take:
        raise HTTPException(status_code=404, detail="Take not found")
    
    take.is_accepted = is_accepted
    if notes:
        take.editor_notes = notes
    
    db.commit()
    return {"status": "updated", "take_id": take_id}
