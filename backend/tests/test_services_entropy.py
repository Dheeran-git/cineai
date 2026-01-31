import sys
import os
import pytest
import asyncio
from unittest.mock import MagicMock

# Add backend to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.audio_service import audio_service
from app.services.cv_service import cv_service

@pytest.mark.asyncio
async def test_audio_analysis_variety():
    """Verify that different file paths produce different audio analysis results."""
    # Test with 5 different 'files' (using paths that will hash differently)
    paths = [f"test_audio_{i}.mp4" for i in range(5)]
    results = []
    
    for path in paths:
        # Mocking os.stat and getmtime to ensure consistent but different seeds for test stability
        with MagicMock() as mock_stat:
            # We don't actually need to mock stats if we just want to see variety from path hash
            res = await audio_service.analyze_audio(path)
            results.append(res)
            
    # Check for variety in transcripts and descriptions
    transcripts = [r["transcript"] for r in results]
    descriptions = [r["audio_description"] for r in results]
    
    # Assert that we have some uniqueness (at least 3 unique items for 5 tests is a safe bet for random/hash spread)
    assert len(set(transcripts)) >= 3, f"Not enough variety in transcripts: {transcripts}"
    assert len(set(descriptions)) >= 3, f"Not enough variety in descriptions: {descriptions}"
    print(f"\n[Variety Test] Transcripts: {set(transcripts)}")

@pytest.mark.asyncio
async def test_video_analysis_variety():
    """Verify that different file paths produce different video analysis results."""
    paths = [f"test_video_{i}.mp4" for i in range(5)]
    results = []
    
    for path in paths:
        # We need to mock os.path.exists for cv_service if it's not available
        # But we're testing the FALLBACK path mainly (where CV2_AVAILABLE might be false)
        res = await cv_service.analyze_video(path)
        results.append(res)
        
    narratives = [r["video_description"] for r in results]
    objects = [tuple(r["objects"]) for r in results]
    
    assert len(set(narratives)) >= 3, f"Not enough variety in narratives: {narratives}"
    assert len(set(objects)) >= 3, f"Not enough variety in detected objects: {objects}"
    print(f"\n[Variety Test] Narratives: {set(narratives)}")

if __name__ == "__main__":
    asyncio.run(test_audio_analysis_variety())
    asyncio.run(test_video_analysis_variety())
