from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models import database as models

router = APIRouter()

@router.get("/heatmap/{take_id}")
def get_emotion_heatmap(take_id: int, db: Session = Depends(deps.get_db)):
    take = db.query(models.Take).get(take_id)
    if not take:
        raise HTTPException(status_code=404, detail="Take not found")

    # Mock heatmap data (intensity over time)
    return {
        "take_id": take_id,
        "data": [
            {"time": i, "intensity": 40 + (i % 20) + (take_id % 10)} 
            for i in range(0, 100, 5)
        ],
        "primary_emotion": "Tension",
        "confidence": 0.88
    }

@router.get("/risk")
def get_reshoot_risk(db: Session = Depends(deps.get_db)):
    return {
        "risk_level": "Low",
        "factors": [
            {"name": "Coverage", "status": "Good", "risk": 10},
            {"name": "Technical", "status": "Stable", "risk": 5},
            {"name": "Continuity", "status": "Warning", "risk": 35}
        ],
        "reasoning": "Scene 12 has high coverage but minor continuity drift detected in Prop markers."
    }
