"""
Frame Extraction Utilities for CLIP Embeddings
Member 2: AI Engineer - Embeddings

Extracts representative frames from video clips for CLIP embedding generation.
Pattern follows backend/app/services/cv_service.py lines 63-83.
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import os


def extract_frames_triple(video_path: str, output_dir: Optional[str] = None) -> List[np.ndarray]:
    """
    Extract 3 frames from video: start (frame 0), middle, end

    This follows the same pattern as cv_service.py for consistency.

    Args:
        video_path: Path to .mp4 video clip
        output_dir: Optional directory to save frames as .jpg files

    Returns:
        List of 3 numpy arrays in RGB format (not BGR)

    Raises:
        FileNotFoundError: If video file doesn't exist
        ValueError: If video cannot be opened or has no frames
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if frame_count == 0:
        cap.release()
        raise ValueError(f"Video has no frames: {video_path}")

    # Sample indices: start, middle, end (same as cv_service.py)
    indices = [0, frame_count // 2, max(0, frame_count - 1)]
    frames = []

    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()

        if ret:
            # Convert BGR (OpenCV default) to RGB (for PIL/CLIP)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)

            # Optional: save frame to disk
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                frame_filename = f"{os.path.basename(video_path)}_frame_{idx}.jpg"
                frame_path = os.path.join(output_dir, frame_filename)
                cv2.imwrite(frame_path, frame)  # Save as BGR (standard for cv2.imwrite)
        else:
            print(f"Warning: Could not read frame {idx} from {video_path}")

    cap.release()

    if len(frames) == 0:
        raise ValueError(f"No frames could be extracted from {video_path}")

    return frames


def extract_middle_frame(video_path: str) -> np.ndarray:
    """
    Extract single middle frame from video (fallback strategy)

    Args:
        video_path: Path to .mp4 video clip

    Returns:
        Single numpy array in RGB format

    Raises:
        FileNotFoundError: If video file doesn't exist
        ValueError: If video cannot be opened or frame cannot be read
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if frame_count == 0:
        cap.release()
        raise ValueError(f"Video has no frames: {video_path}")

    # Get middle frame
    middle_idx = frame_count // 2
    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_idx)
    ret, frame = cap.read()

    cap.release()

    if not ret:
        raise ValueError(f"Could not read middle frame from {video_path}")

    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    return frame_rgb


def get_video_info(video_path: str) -> Dict[str, any]:
    """
    Extract video metadata

    Args:
        video_path: Path to .mp4 video clip

    Returns:
        Dictionary with video metadata:
        {
            "fps": float,
            "frame_count": int,
            "duration": float (seconds),
            "resolution": tuple (width, height),
            "codec": str
        }

    Raises:
        FileNotFoundError: If video file doesn't exist
        ValueError: If video cannot be opened
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))

    # Calculate duration
    duration = frame_count / fps if fps > 0 else 0

    # Convert fourcc to codec string
    codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])

    cap.release()

    return {
        "fps": fps,
        "frame_count": frame_count,
        "duration": duration,
        "resolution": (width, height),
        "codec": codec,
        "file_path": video_path,
        "file_size_mb": os.path.getsize(video_path) / (1024 * 1024)
    }


def extract_frames_at_timestamps(video_path: str, timestamps: List[float]) -> List[np.ndarray]:
    """
    Extract frames at specific timestamps

    Args:
        video_path: Path to .mp4 video clip
        timestamps: List of timestamps in seconds

    Returns:
        List of numpy arrays in RGB format

    Raises:
        FileNotFoundError: If video file doesn't exist
        ValueError: If video cannot be opened
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []

    for timestamp in timestamps:
        # Convert timestamp to frame number
        frame_number = int(timestamp * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()

        if ret:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)
        else:
            print(f"Warning: Could not read frame at timestamp {timestamp}s")

    cap.release()

    return frames


if __name__ == "__main__":
    # Test script
    import sys

    if len(sys.argv) < 2:
        print("Usage: python frame_extractor.py <video_path>")
        print("Example: python frame_extractor.py sample_clip.mp4")
        sys.exit(1)

    video_path = sys.argv[1]

    print(f"Testing frame extraction on: {video_path}")
    print("\n" + "="*60)

    # Get video info
    print("\n1. Video Information:")
    try:
        info = get_video_info(video_path)
        print(f"   FPS: {info['fps']}")
        print(f"   Frame Count: {info['frame_count']}")
        print(f"   Duration: {info['duration']:.2f}s")
        print(f"   Resolution: {info['resolution'][0]}x{info['resolution'][1]}")
        print(f"   Codec: {info['codec']}")
        print(f"   File Size: {info['file_size_mb']:.2f} MB")
    except Exception as e:
        print(f"   Error: {e}")

    # Extract 3 frames
    print("\n2. Extracting 3 frames (start, middle, end):")
    try:
        frames = extract_frames_triple(video_path)
        print(f"   Successfully extracted {len(frames)} frames")
        for i, frame in enumerate(frames):
            print(f"   Frame {i}: shape {frame.shape}, dtype {frame.dtype}")
    except Exception as e:
        print(f"   Error: {e}")

    # Extract middle frame only
    print("\n3. Extracting middle frame only:")
    try:
        middle_frame = extract_middle_frame(video_path)
        print(f"   Successfully extracted middle frame")
        print(f"   Frame shape: {middle_frame.shape}, dtype: {middle_frame.dtype}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n" + "="*60)
    print("Frame extraction test complete!")
