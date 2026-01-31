from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas import models
from app.models import database as db_models

router = APIRouter()


def format_duration(seconds: float) -> str:
    """Convert seconds to 'Xh Ym' format"""
    if seconds == 0:
        return "0h 0m"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"

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


@router.get("/dashboard-stats")
def get_dashboard_stats(
    db: Session = Depends(deps.get_db)
) -> Dict[str, Any]:
    """Get real-time dashboard statistics aggregated from all takes"""

    # Get all takes
    takes = db.query(db_models.Take).all()

    if not takes:
        # Return empty stats if no takes exist
        return {
            "totalFootage": "0h 0m",
            "processingProgress": 0,
            "aiConfidenceHealth": 0,
            "issues": {
                "focus": 0,
                "audio": 0,
                "continuity": 0,
                "narrative": 0
            },
            "approvedCount": 0,
            "pendingReviewCount": 0,
            "totalTakes": 0
        }

    # Calculate total footage
    total_duration = sum(take.duration or 0 for take in takes)
    total_footage = format_duration(total_duration)

    # Calculate processing progress (takes with ai_metadata are processed)
    completed_takes = sum(1 for take in takes if take.ai_metadata)
    processing_progress = (completed_takes / len(takes) * 100) if takes else 0

    # Calculate AI confidence health (average confidence across takes)
    confidences = [take.confidence_score for take in takes if take.confidence_score is not None and take.confidence_score > 0]
    ai_confidence = (sum(confidences) / len(confidences)) if confidences else 0

    # Count issues from ai_metadata
    issues = {"focus": 0, "audio": 0, "continuity": 0, "narrative": 0}
    for take in takes:
        if take.ai_metadata and isinstance(take.ai_metadata, dict):
            metadata = take.ai_metadata

            # Check CV issues
            cv_data = metadata.get("cv", {})
            if isinstance(cv_data, dict) and cv_data.get("focus_issues"):
                issues["focus"] += 1

            # Check Audio issues
            audio_data = metadata.get("audio", {})
            if isinstance(audio_data, dict) and audio_data.get("issues"):
                issues["audio"] += 1

            # Check NLP issues
            nlp_data = metadata.get("nlp", {})
            if isinstance(nlp_data, dict):
                if nlp_data.get("continuity_breaks"):
                    issues["continuity"] += 1
                if nlp_data.get("narrative_gaps"):
                    issues["narrative"] += 1

    # Count approvals and pending
    approved_count = sum(1 for take in takes if take.is_accepted == "accepted")
    pending_count = sum(1 for take in takes if take.is_accepted == "pending")

    return {
        "totalFootage": total_footage,
        "processingProgress": round(processing_progress, 1),
        "aiConfidenceHealth": round(ai_confidence, 1),
        "issues": issues,
        "approvedCount": approved_count,
        "pendingReviewCount": pending_count,
        "totalTakes": len(takes)
    }
