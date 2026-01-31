from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models import database as models
import logging

logger = logging.getLogger(__name__)

class TimelineService:
    def assemble_ai_rough_cut(self, project_id: int, db: Session) -> Dict[str, Any]:
        """
        Groups takes by scene and selects the highest scoring take for the initial timeline.
        """
        scenes = db.query(models.Scene).filter(models.Scene.project_id == project_id).order_by(models.Scene.number).all()
        
        tracks = {
            "v1": {"type": "video", "clips": []},
            "a1": {"type": "audio", "clips": []}
        }

        current_time_frames = 0
        fps = 24

        for scene in scenes:
            # Get highest scoring accepted or pending take
            best_take = db.query(models.Take).filter(
                models.Take.scene_id == scene.id
            ).order_by(models.Take.confidence_score.desc()).first()

            if not best_take:
                continue

            duration_frames = int((best_take.duration or 5) * fps)

            clip = {
                "id": f"clip_{best_take.id}",
                "name": f"SC_{scene.number}_T_{best_take.number}_{best_take.file_name}",
                "take_id": best_take.id,
                "start": current_time_frames,
                "duration": duration_frames,
                "score": best_take.confidence_score,
                "reasoning": best_take.ai_reasoning.get("summary", "")
            }

            tracks["v1"]["clips"].append(clip)
            tracks["a1"]["clips"].append(clip) # Audio matches video initially

            current_time_frames += duration_frames

        return {
            "project_id": project_id,
            "total_duration_frames": current_time_frames,
            "tracks": tracks
        }

timeline_service = TimelineService()
