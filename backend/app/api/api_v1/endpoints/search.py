"""
Semantic Search API Endpoints for SmartCut AI
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import os
from pydantic import BaseModel
from app.api.deps import get_db
from app.services.semantic_search_service import semantic_search_service, SearchResult
from app.services.intent_embedding_service import intent_embedding_service

router = APIRouter()


# Request/Response Models
class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    filters: Optional[Dict[str, Any]] = None


class ReasoningResponse(BaseModel):
    matched_because: List[str]
    emotion_detected: str
    timing_pattern: str
    confidence_score: float
    query_intent: Dict


class SearchResultResponse(BaseModel):
    result_id: int
    take_id: int
    moment_id: int
    start_time: float
    end_time: float
    confidence: float
    transcript_snippet: str
    emotion_label: str
    file_name: str
    video_url: str
    reasoning: ReasoningResponse


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultResponse]


class FeedbackRequest(BaseModel):
    query: str
    result_id: int
    is_relevant: bool
    editor_notes: Optional[str] = None


# Endpoints
@router.post("/intent", response_model=SearchResponse)
async def search_by_intent(request: SearchRequest, db: Session = Depends(get_db)):
    """
    Search footage by editorial intent using semantic similarity.
    
    Example queries:
    - "hesitant reaction before answering"
    - "tense pause before dialogue"  
    - "awkward silence after confession"
    """
    results = semantic_search_service.search_by_intent(
        query=request.query,
        top_k=request.top_k,
        filters=request.filters
    )
    
    return SearchResponse(
        query=request.query,
        total_results=len(results),
        results=[
            SearchResultResponse(
                result_id=r.result_id,
                take_id=r.take_id,
                moment_id=r.moment_id,
                start_time=r.start_time,
                end_time=r.end_time,
                confidence=r.confidence,
                transcript_snippet=r.transcript_snippet,
                emotion_label=r.emotion_label,
                file_name=r.file_name,
                video_url=f"/media_files/{os.path.basename(r.file_path)}" if r.file_path else "",
                reasoning=ReasoningResponse(**r.reasoning)
            )
            for r in results
        ]
    )


@router.get("/suggestions")
async def get_query_suggestions(
    q: str = Query("", description="Partial query for suggestions")
):
    """
    Get autocomplete suggestions for search queries.
    """
    suggestions = semantic_search_service.get_suggestions(q)
    return {"suggestions": suggestions}


@router.get("/explain/{result_id}")
async def explain_result(result_id: int):
    """
    Get detailed explanation for a specific search result.
    """
    if result_id < 0 or result_id >= len(semantic_search_service.metadata):
        raise HTTPException(status_code=404, detail="Result not found")
    
    meta = semantic_search_service.metadata[result_id]
    
    # Generate detailed explanation
    explanation = {
        "result_id": result_id,
        "take_id": meta["take_id"],
        "timestamp": {
            "start": meta["start_time"],
            "end": meta["end_time"]
        },
        "analysis": {
            "emotion": meta["emotion_label"],
            "transcript": meta["transcript_snippet"],
            "audio_features": meta["audio_features"],
            "timing_data": meta["timing_data"]
        },
        "explanation_text": _generate_explanation_text(meta)
    }
    
    return explanation


def _generate_explanation_text(meta: Dict) -> str:
    """Generate a prose explanation of why this moment is significant."""
    parts = []
    
    emotion = meta.get("emotion_label", "neutral")
    parts.append(f"This moment shows a {emotion} emotional state")
    
    transcript = meta.get("transcript_snippet", "")
    if transcript:
        parts.append(f"with dialogue: \"{transcript}\"")
    else:
        parts.append("without verbal dialogue (non-verbal reaction)")
    
    audio = meta.get("audio_features", {})
    if audio.get("pause_before_duration", 0) > 0.5:
        parts.append(f"There is a notable {audio['pause_before_duration']:.1f}s pause before speaking")
    
    timing = meta.get("timing_data", {})
    if timing.get("pattern"):
        parts.append(f"The timing pattern suggests {timing['pattern'].replace('_', ' ')}")
    
    return ". ".join(parts) + "."


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Submit relevance feedback to improve search over time.
    This feeds into the Editor DNA / training system.
    """
    # In a full implementation, this would store to database
    # For now, we log and acknowledge
    feedback_data = {
        "query": request.query,
        "result_id": request.result_id,
        "is_relevant": request.is_relevant,
        "notes": request.editor_notes
    }
    
    # TODO: Store in SearchFeedback table and retrain embeddings
    
    return {
        "status": "received",
        "message": "Thank you! Your feedback helps improve search quality.",
        "feedback": feedback_data
    }


@router.get("/stats")
async def get_search_stats():
    """
    Get statistics about the search index.
    """
    return {
        "total_indexed_moments": semantic_search_service.index.ntotal if semantic_search_service.index else 0,
        "embedding_dimension": semantic_search_service.dimension,
        "index_status": "ready" if semantic_search_service.index else "not_initialized"
    }
