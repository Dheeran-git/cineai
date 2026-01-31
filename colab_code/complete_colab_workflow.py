"""
===================================================================================
🎬 COMPLETE COLAB WORKFLOW - Semantic Video Search Embeddings
Member 2: AI Engineer - Visual Embeddings
===================================================================================

RUN THIS NOTEBOOK IN GOOGLE COLAB WITH GPU RUNTIME:
Runtime → Change runtime type → GPU (T4)

This script will:
1. Mount Google Drive
2. Install dependencies
3. Copy shared videos to your working folder
4. Split videos into clips
5. Generate CLIP embeddings
6. Save everything to Drive
===================================================================================
"""

# ===================================================================================
# CELL 1: Mount Google Drive & Setup
# ===================================================================================
print("=" * 60)
print("🔌 STEP 1: Mounting Google Drive...")
print("=" * 60)

from google.colab import drive
import os
import shutil

drive.mount('/content/drive')

# Your base project path
base_path = "/content/drive/MyDrive/Videos/HackathonProject"

# Create folder structure
folders = ['videos', 'clips', 'embeddings', 'db', 'colab_code']
for f in folders:
    os.makedirs(os.path.join(base_path, f), exist_ok=True)

print(f"✓ Created project structure at: {base_path}")
print(f"✓ Folders: {folders}")

# ===================================================================================
# CELL 2: Install Dependencies
# ===================================================================================
print("\n" + "=" * 60)
print("📦 STEP 2: Installing dependencies...")
print("=" * 60)

# Install required packages
import subprocess
subprocess.run(['pip', 'install', '-q', 'torch', 'torchvision', 'transformers', 
                'pillow', 'opencv-python', 'tqdm', 'scenedetect[opencv]'], check=True)

print("✓ All dependencies installed!")

# ===================================================================================
# CELL 3: Import Libraries
# ===================================================================================
print("\n" + "=" * 60)
print("📚 STEP 3: Importing libraries...")
print("=" * 60)

import torch
import numpy as np
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import cv2
from tqdm import tqdm
import json
from pathlib import Path
import time
from typing import List, Dict, Optional
import glob

print(f"✓ PyTorch version: {torch.__version__}")
print(f"✓ CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"✓ GPU: {torch.cuda.get_device_name(0)}")

# ===================================================================================
# CELL 4: Define Frame Extraction Functions
# ===================================================================================
print("\n" + "=" * 60)
print("🎞️ STEP 4: Defining frame extraction functions...")
print("=" * 60)

def get_video_info(video_path: str) -> Dict:
    """Get video metadata using OpenCV."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    
    info = {
        "fps": cap.get(cv2.CAP_PROP_FPS),
        "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "duration": cap.get(cv2.CAP_PROP_FRAME_COUNT) / max(cap.get(cv2.CAP_PROP_FPS), 1)
    }
    cap.release()
    return info

def extract_frames_triple(video_path: str) -> List[np.ndarray]:
    """Extract 3 frames: start, middle, end."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_count < 3:
        frame_indices = [0]
    else:
        frame_indices = [0, frame_count // 2, frame_count - 1]
    
    frames = []
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, min(idx, frame_count - 1)))
        ret, frame = cap.read()
        if ret:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)
    
    cap.release()
    return frames

def extract_middle_frame(video_path: str) -> np.ndarray:
    """Extract single middle frame."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    middle_idx = frame_count // 2
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_idx)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise ValueError(f"Cannot read frame from: {video_path}")
    
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

print("✓ Frame extraction functions defined!")

# ===================================================================================
# CELL 5: Define CLIP Embedding Generator
# ===================================================================================
print("\n" + "=" * 60)
print("🧠 STEP 5: Loading CLIP model...")
print("=" * 60)

class CLIPEmbeddingGenerator:
    """CLIP-based visual embedding generator for video clips."""
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        self.embedding_dim = 512
        
        print(f"Loading CLIP model: {model_name}")
        print(f"Device: {self.device}")
        
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model.eval()
        
        print("✓ CLIP model loaded successfully!")
    
    def embed_image(self, image: np.ndarray) -> np.ndarray:
        """Generate 512-dim CLIP embedding for an image."""
        pil_image = Image.fromarray(image.astype('uint8'))
        inputs = self.processor(images=pil_image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
        
        # L2 normalize
        embedding = image_features / image_features.norm(dim=-1, keepdim=True)
        return embedding.cpu().numpy().flatten()
    
    def embed_video_clip(self, video_path: str, strategy: str = "triple") -> np.ndarray:
        """Generate embedding for a video clip."""
        try:
            if strategy == "triple":
                frames = extract_frames_triple(video_path)
                embeddings = [self.embed_image(frame) for frame in frames]
                embedding = np.mean(embeddings, axis=0)
                embedding = embedding / np.linalg.norm(embedding)
            else:
                frame = extract_middle_frame(video_path)
                embedding = self.embed_image(frame)
            
            return embedding
        except Exception as e:
            print(f"Error processing {video_path}: {e}")
            return np.zeros(self.embedding_dim, dtype=np.float32)
    
    def embed_text_query(self, query: str) -> np.ndarray:
        """Generate CLIP text embedding for search."""
        inputs = self.processor(text=[query], return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
        
        embedding = text_features / text_features.norm(dim=-1, keepdim=True)
        return embedding.cpu().numpy().flatten()
    
    def batch_process_videos(
        self,
        videos_dir: str,
        output_dir: str,
        strategy: str = "triple",
        file_patterns: List[str] = ["*.mp4", "*.avi", "*.mov", "*.mkv"]
    ) -> Dict:
        """Process all videos in a directory."""
        videos_dir = Path(videos_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Find all videos
        video_paths = []
        for pattern in file_patterns:
            video_paths.extend(videos_dir.glob(pattern))
            video_paths.extend(videos_dir.glob(pattern.upper()))
        video_paths = sorted(set(video_paths))
        
        print(f"\n{'='*60}")
        print(f"Found {len(video_paths)} video files in {videos_dir}")
        print(f"{'='*60}\n")
        
        if len(video_paths) == 0:
            return {"error": "No video files found", "path": str(videos_dir)}
        
        embeddings = []
        paths = []
        metadata = {}
        
        start_time = time.time()
        
        for video_path in tqdm(video_paths, desc="Generating CLIP embeddings"):
            embedding = self.embed_video_clip(str(video_path), strategy)
            
            if np.linalg.norm(embedding) > 0:
                embeddings.append(embedding)
                paths.append(str(video_path))
                
                try:
                    info = get_video_info(str(video_path))
                    metadata[video_path.name] = {
                        "status": "success",
                        "duration": info["duration"],
                        "resolution": f"{info['width']}x{info['height']}"
                    }
                except:
                    metadata[video_path.name] = {"status": "success"}
            else:
                metadata[video_path.name] = {"status": "failed"}
        
        total_time = time.time() - start_time
        
        # Save results
        embeddings_array = np.array(embeddings, dtype=np.float32)
        paths_array = np.array(paths)
        
        np.save(output_dir / "video_embeddings.npy", embeddings_array)
        np.save(output_dir / "video_paths.npy", paths_array)
        
        config = {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "frame_strategy": strategy,
            "device": self.device,
            "total_videos": len(video_paths),
            "processed": len(embeddings),
            "failed": len(video_paths) - len(embeddings),
            "processing_time": total_time
        }
        
        with open(output_dir / "embedding_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        with open(output_dir / "frame_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n{'='*60}")
        print("✓ PROCESSING COMPLETE!")
        print(f"{'='*60}")
        print(f"  Videos processed: {len(embeddings)}/{len(video_paths)}")
        print(f"  Embedding shape: {embeddings_array.shape}")
        print(f"  Total time: {total_time:.1f}s")
        print(f"  Output: {output_dir}")
        print(f"{'='*60}\n")
        
        return config

# Initialize generator
generator = CLIPEmbeddingGenerator()

# ===================================================================================
# CELL 6: Process Your Videos
# ===================================================================================
print("\n" + "=" * 60)
print("🎬 STEP 6: Processing videos from your Google Drive...")
print("=" * 60)

# Your video source path (where the shared videos are)
# NOTE: The shared folder link needs to be added to "Shared with me" first
# Then you can access it via the path below

videos_source = os.path.join(base_path, "videos")
embeddings_output = os.path.join(base_path, "embeddings")

# Check what videos we have
video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.MP4', '*.AVI', '*.MOV', '*.MKV']
all_videos = []
for ext in video_extensions:
    all_videos.extend(glob.glob(os.path.join(videos_source, ext)))

print(f"\n📂 Videos directory: {videos_source}")
print(f"📹 Found {len(all_videos)} video files:")
for v in all_videos[:10]:  # Show first 10
    print(f"   - {os.path.basename(v)}")
if len(all_videos) > 10:
    print(f"   ... and {len(all_videos) - 10} more")

if len(all_videos) == 0:
    print("\n⚠️ NO VIDEOS FOUND!")
    print("Please copy your videos to:", videos_source)
    print("\nTo add shared folder videos:")
    print("1. Go to the shared link in Google Drive")
    print("2. Right-click the videos → 'Add shortcut to Drive'")
    print("3. Or download and upload to your 'videos' folder")
else:
    # Process all videos
    print("\n🚀 Starting embedding generation...")
    stats = generator.batch_process_videos(
        videos_dir=videos_source,
        output_dir=embeddings_output,
        strategy="triple"
    )

# ===================================================================================
# CELL 7: Verify Outputs
# ===================================================================================
print("\n" + "=" * 60)
print("✅ STEP 7: Verifying outputs...")
print("=" * 60)

embeddings_path = os.path.join(embeddings_output, "video_embeddings.npy")
paths_path = os.path.join(embeddings_output, "video_paths.npy")

if os.path.exists(embeddings_path):
    embeddings = np.load(embeddings_path)
    paths = np.load(paths_path, allow_pickle=True)
    
    print(f"\n📊 Embeddings Summary:")
    print(f"   Shape: {embeddings.shape}")
    print(f"   Dtype: {embeddings.dtype}")
    print(f"   Number of videos: {len(paths)}")
    
    # Verify L2 normalization
    norms = np.linalg.norm(embeddings, axis=1)
    print(f"   L2 norms (should be ~1.0): {norms[:5]}")
    
    print(f"\n📁 Output files saved to: {embeddings_output}")
    print("   - video_embeddings.npy")
    print("   - video_paths.npy")
    print("   - embedding_config.json")
    print("   - frame_metadata.json")
else:
    print("⚠️ No embeddings generated yet. Check the videos folder.")

# ===================================================================================
# CELL 8: Test Search (Optional)
# ===================================================================================
print("\n" + "=" * 60)
print("🔍 STEP 8: Testing semantic search...")
print("=" * 60)

if os.path.exists(embeddings_path):
    # Test search queries
    test_queries = [
        "close-up shot of a person",
        "outdoor scene with nature",
        "dialogue conversation",
        "action scene"
    ]
    
    embeddings = np.load(embeddings_path)
    paths = np.load(paths_path, allow_pickle=True)
    
    print("\n🔎 Sample search results:")
    for query in test_queries[:2]:
        query_embedding = generator.embed_text_query(query)
        
        # Cosine similarity via dot product (embeddings are normalized)
        similarities = np.dot(embeddings, query_embedding)
        top_indices = np.argsort(similarities)[::-1][:3]
        
        print(f"\n   Query: '{query}'")
        for i, idx in enumerate(top_indices):
            print(f"   {i+1}. {os.path.basename(paths[idx])} (score: {similarities[idx]:.3f})")

print("\n" + "=" * 60)
print("🎉 ALL DONE!")
print("=" * 60)
print("\nNext steps:")
print("1. Copy embeddings to your backend: backend/storage/")
print("2. Start the FastAPI backend")
print("3. Visual search will be automatically available!")
print("=" * 60)
