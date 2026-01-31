# Video Splitter Script for Member 1
# Responsibilities:
# 1. Download video using yt-dlp
# 2. Split video into scenes using PySceneDetect
# 3. Save clips to Drive folder

import os
import subprocess
import sys
from pathlib import Path

# --- Configuration ---
# Folder structure as per README
DRIVE_ROOT = "/content/drive/MyDrive/HackathonProject"
VIDEOS_DIR = os.path.join(DRIVE_ROOT, "videos")
CLIPS_DIR = os.path.join(DRIVE_ROOT, "clips")

def install_dependencies():
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp", "scenedetect[opencv]"])

def mount_drive():
    from google.colab import drive
    if not os.path.exists("/content/drive"):
        drive.mount('/content/drive')
    
    # Create directories if they don't exist
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    os.makedirs(CLIPS_DIR, exist_ok=True)
    print(f"Directories checked: {VIDEOS_DIR}, {CLIPS_DIR}")

def download_video(url, output_name="raw_video"):
    """Downloads video (best quality) to VIDEOS_DIR"""
    output_path = os.path.join(VIDEOS_DIR, f"{output_name}.mp4")
    if os.path.exists(output_path):
        print(f"Video already exists at {output_path}")
        return output_path
    
    print(f"Downloading {url}...")
    # yt-dlp command
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", output_path,
        url
    ]
    subprocess.check_call(cmd)
    print(f"Downloaded to {output_path}")
    return output_path

def split_video(video_path, threshold=27.0):
    """Splits video into scenes using distinct scene detection"""
    from scenedetect import VideoManager, SceneManager
    from scenedetect.detectors import ContentDetector
    from scenedetect.scene_manager import save_images, write_scene_list_html
    
    print(f"Processing {video_path}...")
    
    # We will use ffmpeg validation via scenedetect to split
    # Or we can just get scene list and use ffmpeg manually if scenedetect split_video_ffmpeg is tricky in Colab
    # But scenedetect has a split_video_ffmpeg function.
    
    # For this script, we'll keep it simple: Use scenedetect CLI or API.
    # API approach:
    
    # 1. Detect Scenes
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    
    video_manager.set_downscale_factor()
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    
    scene_list = scene_manager.get_scene_list()
    print(f"{len(scene_list)} scenes detected.")
    
    # 2. Split video
    # Note: split_video_ffmpeg requires ffmpeg installed (Colab usually has it)
    from scenedetect.video_splitter import split_video_ffmpeg
    
    video_name = Path(video_path).stem
    # Output pattern: clips/video_name-Scene-001.mp4
    output_file_template = os.path.join(CLIPS_DIR, f"{video_name}-Scene-$SCENE_NUMBER.mp4")
    
    split_video_ffmpeg(video_path, scene_list, output_file_template, show_progress=True)
    print("Splitting complete.")

def main():
    # 1. Setup
    try:
        import google.colab
        IN_COLAB = True
    except ImportError:
        IN_COLAB = False
        print("Not running in Colab. Ensure directories and dependencies exist manually.")
        # Local fallback or exit? 
        # For now, let's assume this script is meant for Colab as per filename.
        
    if IN_COLAB:
        install_dependencies()
        mount_drive()
    
    # 2. Input
    url = input("Enter YouTube URL (or press Enter to skip download if testing): ").strip()
    if url:
        video_path = download_video(url, output_name="demo_video")
    else:
        # Look for existing video
        files = [f for f in os.listdir(VIDEOS_DIR) if f.endswith(".mp4")]
        if files:
            video_path = os.path.join(VIDEOS_DIR, files[0])
            print(f"Using existing video: {video_path}")
        else:
            print("No video found.")
            return

    # 3. Process
    split_video(video_path)
    
    print("Member 1 Task Complete: Clips generated.")

if __name__ == "__main__":
    main()
