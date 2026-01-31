from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="active") # active, archived
    
    scenes = relationship("Scene", back_populates="project")
    settings = Column(JSON, default={})

class Scene(Base):
    __tablename__ = "scenes"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    number = Column(Integer)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)

    project = relationship("Project", back_populates="scenes")
    takes = relationship("Take", back_populates="scene")

class Take(Base):
    __tablename__ = "takes"

    id = Column(Integer, primary_key=True, index=True)
    scene_id = Column(Integer, ForeignKey("scenes.id"))
    number = Column(Integer)
    file_path = Column(String)
    file_name = Column(String)
    file_size = Column(Integer)
    duration = Column(Float) # in seconds
    
    # AI Data
    confidence_score = Column(Float, default=0.0)
    ai_metadata = Column(JSON, default={}) # Stores YOLO, Whisper, OCR results
    ai_reasoning = Column(JSON, default={}) # Stores "why" for each stage
    
    # Human Override
    is_accepted = Column(Enum("pending", "accepted", "rejected", name="take_status"), default="pending")
    editor_notes = Column(String, nullable=True)

    scene = relationship("Scene", back_populates="takes")
    cameras = relationship("Camera", back_populates="take")

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    take_id = Column(Integer, ForeignKey("takes.id"))
    label = Column(String) # CAM-A, CAM-B
    is_master = Column(Enum("yes", "no", name="master_status"), default="no")
    camera_metadata = Column(JSON, default={})  # Renamed from 'metadata' (reserved in SQLAlchemy)

    take = relationship("Take", back_populates="cameras")


class MomentEmbedding(Base):
    """Stores intent embeddings for semantic search."""
    __tablename__ = "moment_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    take_id = Column(Integer, ForeignKey("takes.id"))
    start_time = Column(Float)  # seconds
    end_time = Column(Float)
    embedding_blob = Column(String)  # Base64 encoded numpy array
    emotion_label = Column(String, default="neutral")
    audio_features = Column(JSON, default={})
    timing_data = Column(JSON, default={})
    transcript_snippet = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class SearchFeedback(Base):
    """Stores editor feedback for training/Editor DNA."""
    __tablename__ = "search_feedback"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String)
    result_moment_id = Column(Integer)
    is_relevant = Column(String)  # "yes", "no"
    editor_notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
