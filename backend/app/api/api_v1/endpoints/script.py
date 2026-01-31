from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models import database as models

router = APIRouter()

@router.get("/coverage")
def get_script_coverage(db: Session = Depends(deps.get_db)):
    # In a real app, this would query the NLP alignment results across all takes
    takes = db.query(models.Take).all()
    
    # Mock data structure matching frontend ScriptCoverage.tsx expectations
    return {
        "overall_coverage": 82.0,
        "lines": [
            {
                "id": "l1",
                "text": "I told you we shouldn't have come here, Marcus. The perimeter is compromised.",
                "status": "covered",
                "takes": [t.id for t in takes if t.confidence_score > 90]
            },
            {
                "id": "l2",
                "text": "Since when do you care about perimeters? You just want to get back to the city.",
                "status": "covered",
                "takes": [t.id for t in takes if t.confidence_score > 80]
            },
            {
                "id": "l3",
                "text": "I care about staying alive. Look at this tech. This isn't local.",
                "status": "partial",
                "takes": [t.id for t in takes if t.confidence_score > 70]
            }
        ]
    }
