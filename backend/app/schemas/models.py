from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Shared properties
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    settings: Optional[dict] = {}

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    created_at: datetime
    status: str
    model_config = ConfigDict(from_attributes=True)

class SceneBase(BaseModel):
    number: int
    name: Optional[str] = None
    description: Optional[str] = None

class SceneCreate(SceneBase):
    project_id: int

class Scene(SceneBase):
    id: int
    project_id: int
    model_config = ConfigDict(from_attributes=True)

class TakeBase(BaseModel):
    number: int
    file_name: str
    file_size: int
    duration: float

class TakeCreate(TakeBase):
    scene_id: int
    file_path: str

class Take(TakeBase):
    id: int
    scene_id: int
    confidence_score: float
    ai_metadata: dict
    ai_reasoning: dict
    is_accepted: str
    editor_notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
