
# SmartCut AI - Full Pipeline (Colab)
# Combines Video Splitting, Transcription, Object Detection, and Embedding Generation
# Exports 'smartcut_data.json' for the local Dashboard.

import os
import json
import subprocess
import sys
import numpy as np
from pathlib import Path

# --- CONFIG ---
DRIVE_ROOT = "/content/drive/MyDrive/HackathonProject"
VIDEOS_DIR = os.path.join(DRIVE_ROOT, "videos")
CLIPS_DIR = os.path.join(DRIVE_ROOT, "clips")
OUTPUT_JSON = os.path.join(DRIVE_ROOT, "smartcut_data.json")

# --- INSTALL DEPENCENCIES ---
def install_deps():
    print("Installing AI dependencies... (This may take a few minutes)")
    subprocess.check_call([sys.executable, "-m", "pip", "install", 
                           "yt-dlp", "scenedetect[opencv]", "openai-whisper", "ultralytics", "sentence-transformers", "faiss-cpu", "librosa"])
    print("Dependencies installed.")

# --- 1. SPLIT VIDEO ---
def split_video_scenes(video_path):
    print(f"Splitting video: {video_path}")
    from scenedetect import VideoManager, SceneManager
    from scenedetect.detectors import ContentDetector
    from scenedetect.video_splitter import split_video_ffmpeg

    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=27.0))
    
    video_manager.set_downscale_factor()
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list()
    
    print(f"Found {len(scene_list)} scenes.")
    
    video_name = Path(video_path).stem
    output_template = os.path.join(CLIPS_DIR, f"{video_name}-Scene-$SCENE_NUMBER.mp4")
    
    split_video_ffmpeg(video_path, scene_list, output_template, show_progress=False)
    
    # Return list of generated clip paths
    clips = []
    for i in range(len(scene_list)):
        clip_path = os.path.join(CLIPS_DIR, f"{video_name}-Scene-{i+1:03d}.mp4")
        if os.path.exists(clip_path):
            clips.append({
                "path": clip_path,
                "start": scene_list[i][0].get_seconds(),
                "end": scene_list[i][1].get_seconds(),
                "scene_id": i+1
            })
    return clips

# --- 2. ANALYZE CLIP ---
def analyze_clip_ai(clip_info, whisper_model, yolo_model, sentence_model):
    path = clip_info["path"]
    print(f"Analyzing {os.path.basename(path)}...")
    
    # A. Audio Transcription (Whisper)
    try:
        transcription = whisper_model.transcribe(path)
        text = transcription['text'].strip()
    except Exception as e:
        print(f"Whisper error: {e}")
        text = ""
        
    # B. Object Detection (YOLO)
    # Sample middle frame
    objects = []
    try:
        results = yolo_model(path, stream=False)
        # Just take first frame results for summary
        if results:
            for r in results:
                for c in r.boxes.cls:
                    objects.append(yolo_model.names[int(c)])
            objects = list(set(objects)) # Unique
    except Exception as e:
        print(f"YOLO error: {e}")

    # C. Embedding (Sentence Transformer on description)
    # Create a rich description for semantic search
    description = f"Scene {clip_info['scene_id']}. "
    if text:
        description += f"Dialogue: {text}. "
    if objects:
        description += f"Contains: {', '.join(objects)}."
        
    embedding = sentence_model.encode(description).tolist()
    
    return {
        "clip_id": os.path.basename(path),
        "start_time": clip_info["start"],
        "end_time": clip_info["end"],
        "transcript": text,
        "objects": objects,
        "description": description,
        "embedding": embedding,
        "emotion_label": "neutral" # Placeholder or can infer from text
    }

# --- MAIN EXECUTOR ---
def run_pipeline():
    try:
        import google.colab
        from google.colab import drive
        if not os.path.exists("/content/drive"):
            drive.mount('/content/drive')
    except:
        print("Not in Colab, skipping drive mount.")

    os.makedirs(VIDEOS_DIR, exist_ok=True)
    os.makedirs(CLIPS_DIR, exist_ok=True)

    # Load Models
    print("Loading AI Models...")
    import whisper
    from ultralytics import YOLO
    from sentence_transformers import SentenceTransformer
    
    w_model = whisper.load_model("base")
    y_model = YOLO("yolov8n.pt") 
    s_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Find Videos
    videos = [f for f in os.listdir(VIDEOS_DIR) if f.endswith(".mp4")]
    if not videos:
        print(f"No videos found in {VIDEOS_DIR}. Please upload one.")
        return

    all_data = []

    for video_file in videos:
        video_path = os.path.join(VIDEOS_DIR, video_file)
        
        # 1. Split
        clips = split_video_scenes(video_path)
        
        # 2. Analyze
        print(f"Analyzing {len(clips)} clips for {video_file}...")
        for clip in clips:
            analysis = analyze_clip_ai(clip, w_model, y_model, s_model)
            all_data.append(analysis)
            
    # 3. Save JSON
    with open(OUTPUT_JSON, "w") as f:
        json.dump(all_data, f, indent=2)
        
    print(f"Done! Analysis saved to {OUTPUT_JSON}")
    print("Download this file and import it into your Local SmartCut Dashboard.")

if __name__ == "__main__":
    # Check if deps needed
    try:
        import scenedetect
        import whisper
        import ultralytics
    except ImportError:
        install_deps()
        
    run_pipeline()
