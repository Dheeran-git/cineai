"""
Simple Audio Analysis for Video Clips
Member 2: AI Engineer - Embeddings (Bonus Feature)

Provides basic audio analysis including silence detection and volume analysis.
Complements visual CLIP embeddings with audio metadata.
"""

import librosa
import numpy as np
from typing import Dict, Optional
import os


def analyze_audio_simple(audio_path: str, silence_threshold: float = 0.02) -> Dict:
    """
    Simple audio analysis for silence detection and volume levels

    Args:
        audio_path: Path to audio file (or video file - librosa extracts audio)
        silence_threshold: RMS threshold below which audio is considered silent

    Returns:
        Dictionary with audio analysis:
        {
            "duration": float,           # Duration in seconds
            "is_silent": bool,           # True if >80% of audio is silent
            "avg_volume": float,         # Average RMS energy (0-1 scale)
            "silence_percentage": float, # Percentage of silent frames
            "peak_volume": float,        # Peak RMS energy
            "volume_variance": float     # Variance in volume (stability)
        }
    """
    try:
        # Load audio (librosa automatically extracts audio from video files)
        y, sr = librosa.load(audio_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)

        # Calculate RMS (Root Mean Square) energy for volume analysis
        rms = librosa.feature.rms(y=y)[0]
        avg_rms = np.mean(rms)
        peak_rms = np.max(rms)
        variance_rms = np.var(rms)

        # Silence detection
        silence_frames = np.sum(rms < silence_threshold)
        silence_percentage = (silence_frames / len(rms)) * 100

        # Determine if clip is predominantly silent (>80% silent)
        is_silent = silence_percentage > 80

        return {
            "duration": float(duration),
            "is_silent": bool(is_silent),
            "avg_volume": float(avg_rms),
            "silence_percentage": float(silence_percentage),
            "peak_volume": float(peak_rms),
            "volume_variance": float(variance_rms),
            "sample_rate": int(sr),
            "status": "success"
        }

    except Exception as e:
        return {
            "duration": 0,
            "is_silent": True,
            "avg_volume": 0,
            "silence_percentage": 100,
            "peak_volume": 0,
            "volume_variance": 0,
            "sample_rate": 0,
            "status": "error",
            "error": str(e)
        }


def analyze_audio_detailed(audio_path: str) -> Dict:
    """
    Detailed audio analysis with advanced features

    Args:
        audio_path: Path to audio file (or video file)

    Returns:
        Dictionary with detailed audio analysis including:
        - Volume metrics (RMS, loudness)
        - Spectral features (spectral centroid, rolloff)
        - Temporal features (zero crossing rate)
        - Silence detection
    """
    try:
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)

        # Volume analysis
        rms = librosa.feature.rms(y=y)[0]
        avg_rms = np.mean(rms)
        peak_rms = np.max(rms)

        # Silence detection
        silence_threshold = 0.02
        silence_frames = np.sum(rms < silence_threshold)
        silence_percentage = (silence_frames / len(rms)) * 100

        # Spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        avg_spectral_centroid = np.mean(spectral_centroid)

        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        avg_spectral_rolloff = np.mean(spectral_rolloff)

        # Zero crossing rate (indicator of percussive vs tonal content)
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        avg_zcr = np.mean(zcr)

        # Tempo detection (optional, can be slow)
        try:
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        except:
            tempo = 0

        return {
            "duration": float(duration),
            "is_silent": bool(silence_percentage > 80),
            "avg_volume": float(avg_rms),
            "peak_volume": float(peak_rms),
            "silence_percentage": float(silence_percentage),
            "spectral_centroid": float(avg_spectral_centroid),
            "spectral_rolloff": float(avg_spectral_rolloff),
            "zero_crossing_rate": float(avg_zcr),
            "tempo": float(tempo),
            "sample_rate": int(sr),
            "status": "success"
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def batch_analyze_audio(video_clips: list, detailed: bool = False) -> Dict[str, Dict]:
    """
    Batch audio analysis for multiple video clips

    Args:
        video_clips: List of video file paths
        detailed: If True, use detailed analysis; otherwise simple analysis

    Returns:
        Dictionary mapping clip paths to audio analysis results
    """
    results = {}

    analysis_func = analyze_audio_detailed if detailed else analyze_audio_simple

    for clip_path in video_clips:
        if os.path.exists(clip_path):
            results[clip_path] = analysis_func(clip_path)
        else:
            results[clip_path] = {
                "status": "error",
                "error": f"File not found: {clip_path}"
            }

    return results


def classify_audio_content(audio_analysis: Dict) -> str:
    """
    Classify audio content based on analysis metrics

    Args:
        audio_analysis: Dictionary from analyze_audio_simple or analyze_audio_detailed

    Returns:
        Classification string: "silent", "quiet", "normal", "loud", "error"
    """
    if audio_analysis.get("status") == "error":
        return "error"

    avg_volume = audio_analysis.get("avg_volume", 0)
    silence_pct = audio_analysis.get("silence_percentage", 100)

    if silence_pct > 80:
        return "silent"
    elif avg_volume < 0.01:
        return "quiet"
    elif avg_volume > 0.1:
        return "loud"
    else:
        return "normal"


if __name__ == "__main__":
    # Test script
    import sys
    from pathlib import Path

    if len(sys.argv) < 2:
        print("Usage: python audio_analysis.py <video_or_audio_path>")
        print("Example: python audio_analysis.py sample_clip.mp4")
        sys.exit(1)

    media_path = sys.argv[1]

    print(f"Analyzing audio from: {media_path}")
    print("\n" + "="*60)

    # Simple analysis
    print("\n1. Simple Audio Analysis:")
    simple_result = analyze_audio_simple(media_path)

    if simple_result["status"] == "success":
        print(f"   Duration: {simple_result['duration']:.2f}s")
        print(f"   Is Silent: {simple_result['is_silent']}")
        print(f"   Avg Volume: {simple_result['avg_volume']:.4f}")
        print(f"   Peak Volume: {simple_result['peak_volume']:.4f}")
        print(f"   Silence %: {simple_result['silence_percentage']:.1f}%")
        print(f"   Classification: {classify_audio_content(simple_result)}")
    else:
        print(f"   Error: {simple_result['error']}")

    # Detailed analysis
    print("\n2. Detailed Audio Analysis:")
    detailed_result = analyze_audio_detailed(media_path)

    if detailed_result["status"] == "success":
        print(f"   Duration: {detailed_result['duration']:.2f}s")
        print(f"   Avg Volume: {detailed_result['avg_volume']:.4f}")
        print(f"   Spectral Centroid: {detailed_result['spectral_centroid']:.2f} Hz")
        print(f"   Spectral Rolloff: {detailed_result['spectral_rolloff']:.2f} Hz")
        print(f"   Zero Crossing Rate: {detailed_result['zero_crossing_rate']:.4f}")
        print(f"   Tempo: {detailed_result['tempo']:.1f} BPM")
    else:
        print(f"   Error: {detailed_result['error']}")

    print("\n" + "="*60)
    print("Audio analysis complete!")
