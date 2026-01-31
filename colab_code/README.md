# CLIP Visual Embeddings - Member 2

**Member 2: AI Engineer - Embeddings**
**Deliverables**: Generate CLIP-based visual embeddings for video frames to enable semantic video search

---

## Quick Start (Google Colab)

### 1. Mount Google Drive
```python
from google.colab import drive
drive.mount('/content/drive')
```

### 2. Install Dependencies
```bash
!pip install -q torch torchvision transformers pillow opencv-python tqdm librosa
```

Or install from requirements:
```bash
!pip install -q -r /content/drive/MyDrive/HackathonProject/colab_code/requirements_colab.txt
```

### 3. Set Up Directories
```python
import os

# Navigate to project directory
os.chdir('/content/drive/MyDrive/HackathonProject')

# Verify directory structure
!ls -la
```

Expected structure:
```
HackathonProject/
├── clips/           # Input: Video clips from Member 1
├── embeddings/      # Output: Generated embeddings (created automatically)
├── db/              # FAISS indices (Member 3)
└── colab_code/      # This directory
```

### 4. Run Embedding Generation
```python
# Add colab_code to Python path
import sys
sys.path.append('/content/drive/MyDrive/HackathonProject/colab_code')

# Import and run
from embedding_gen import CLIPEmbeddingGenerator

# Initialize generator
generator = CLIPEmbeddingGenerator(model_name="openai/clip-vit-b-32")

# Process all clips
stats = generator.batch_process_clips(
    clips_dir="/content/drive/MyDrive/HackathonProject/clips",
    output_dir="/content/drive/MyDrive/HackathonProject/embeddings",
    strategy="triple",  # or "single"
    file_pattern="*.mp4"
)
```

Or use command-line:
```bash
!python colab_code/embedding_gen.py \
    --clips_dir "/content/drive/MyDrive/HackathonProject/clips" \
    --output_dir "/content/drive/MyDrive/HackathonProject/embeddings" \
    --strategy triple \
    --model "openai/clip-vit-b-32"
```

### 5. Verify Outputs
```bash
!ls -lh /content/drive/MyDrive/HackathonProject/embeddings/
```

Expected files:
- `video_embeddings.npy` - CLIP embeddings (N, 512)
- `video_paths.npy` - Corresponding video paths
- `embedding_config.json` - Model configuration
- `frame_metadata.json` - Frame extraction details

### 6. Run Integration Tests
```python
!python colab_code/integration_test.py \
    --output_dir "/content/drive/MyDrive/HackathonProject/embeddings"
```

All tests should pass before proceeding to Member 3 integration.

---

## Scripts Overview

### 1. `frame_extractor.py`
Frame extraction utilities using OpenCV.

**Key Functions:**
```python
from frame_extractor import extract_frames_triple, extract_middle_frame, get_video_info

# Extract 3 frames (start, middle, end)
frames = extract_frames_triple("clip_001.mp4")  # Returns list of 3 RGB numpy arrays

# Extract single middle frame
frame = extract_middle_frame("clip_001.mp4")  # Returns single RGB numpy array

# Get video metadata
info = get_video_info("clip_001.mp4")
# Returns: {"fps": 30, "frame_count": 300, "duration": 10.0, "resolution": (1920, 1080), ...}
```

**Test:**
```bash
!python colab_code/frame_extractor.py /path/to/sample_clip.mp4
```

### 2. `embedding_gen.py`
Main CLIP embedding generation script.

**Class: `CLIPEmbeddingGenerator`**
```python
from embedding_gen import CLIPEmbeddingGenerator

# Initialize
generator = CLIPEmbeddingGenerator(model_name="openai/clip-vit-b-32")

# Embed single image
import numpy as np
image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
embedding = generator.embed_image(image)  # Returns (512,) normalized embedding

# Embed video clip
embedding = generator.embed_video_clip("clip_001.mp4", strategy="triple")

# Embed text query (for search)
query_embedding = generator.embed_text_query("close-up shot with red lighting")

# Batch process all clips
stats = generator.batch_process_clips(
    clips_dir="/content/drive/MyDrive/HackathonProject/clips",
    output_dir="/content/drive/MyDrive/HackathonProject/embeddings"
)
```

**Strategies:**
- `"triple"`: Extract 3 frames (start, middle, end), mean-pool embeddings (recommended)
- `"single"`: Extract single middle frame only (faster, less robust)

### 3. `audio_analysis.py` (Bonus)
Simple audio analysis for silence detection.

**Functions:**
```python
from audio_analysis import analyze_audio_simple, analyze_audio_detailed

# Simple analysis
result = analyze_audio_simple("clip_001.mp4")
# Returns: {"duration": 10.0, "is_silent": False, "avg_volume": 0.05, ...}

# Detailed analysis
result = analyze_audio_detailed("clip_001.mp4")
# Returns: {..., "spectral_centroid": 1500.0, "tempo": 120.0, ...}
```

**Test:**
```bash
!python colab_code/audio_analysis.py /path/to/sample_clip.mp4
```

### 4. `integration_test.py`
Validation tests for generated embeddings.

**Tests:**
1. Format validation (shape, dtype)
2. L2 normalization check
3. Similarity sanity checks
4. Paths alignment verification
5. Configuration completeness

**Usage:**
```bash
!python colab_code/integration_test.py \
    --output_dir "/content/drive/MyDrive/HackathonProject/embeddings"
```

---

## Output Files

### `video_embeddings.npy`
CLIP visual embeddings for all video clips.

- **Shape**: `(N, 512)` where N = number of clips
- **Dtype**: `float32`
- **Normalization**: L2 normalized (norms = 1.0)
- **Aggregation**: Mean-pooled from 3 frames (if `strategy="triple"`)

**Load:**
```python
import numpy as np
embeddings = np.load("video_embeddings.npy")
print(f"Shape: {embeddings.shape}")  # (N, 512)
print(f"Norms: {np.linalg.norm(embeddings, axis=1)[:5]}")  # Should be ~1.0
```

### `video_paths.npy`
Corresponding video clip paths.

- **Shape**: `(N,)`
- **Dtype**: `str` (numpy array of strings)

**Load:**
```python
paths = np.load("video_paths.npy", allow_pickle=True)
print(f"Number of paths: {len(paths)}")
print(f"Sample path: {paths[0]}")
```

### `embedding_config.json`
Model configuration and processing statistics.

**Example:**
```json
{
  "model_name": "openai/clip-vit-b-32",
  "embedding_dim": 512,
  "frame_strategy": "triple",
  "aggregation": "mean_pool",
  "normalization": "l2",
  "device": "cuda",
  "total_clips_found": 100,
  "clips_processed": 98,
  "clips_failed": 2,
  "total_processing_time": 125.6,
  "avg_time_per_clip": 1.256
}
```

### `frame_metadata.json`
Per-clip frame extraction details.

**Example:**
```json
{
  "clip_001.mp4": {
    "frames_extracted": 3,
    "frame_indices": [0, 150, 299],
    "status": "success",
    "extraction_time": 0.15,
    "embedding_time": 0.08
  }
}
```

---

## Integration with Backend

### For Member 3 (Search Backend):

1. **Load embeddings into FAISS**:
```python
import numpy as np
import faiss

embeddings = np.load("video_embeddings.npy")
paths = np.load("video_paths.npy", allow_pickle=True)

# Create FAISS index
dimension = 512
index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
index.add(embeddings)

print(f"FAISS index created with {index.ntotal} vectors")
```

2. **Search**:
```python
# Example: Search with query embedding
query_embedding = generator.embed_text_query("close-up shot")
query_embedding = query_embedding.reshape(1, -1)

k = 10  # Top 10 results
scores, indices = index.search(query_embedding, k)

for score, idx in zip(scores[0], indices[0]):
    print(f"Path: {paths[idx]}, Score: {score:.4f}")
```

3. **Save FAISS index**:
```python
faiss.write_index(index, "db/faiss_visual_index.bin")
```

### For Member 4 (Frontend):

- Embeddings are pre-computed and indexed by Member 3
- Frontend sends text queries → Backend converts to CLIP embeddings → FAISS search
- Display results with video clips and confidence scores

---

## Model Details

**Model**: `openai/clip-vit-b-32` (Vision Transformer)

| Property | Value |
|----------|-------|
| Embedding Dimension | 512 |
| Model Size | ~600 MB |
| Inference Speed (GPU) | ~30ms per image |
| Inference Speed (CPU) | ~200ms per image |
| Memory (GPU) | ~1 GB |
| Normalization | L2 normalized |
| Similarity Metric | Cosine similarity (via inner product) |

**Why CLIP ViT-B/32?**
- Balance of speed and quality
- Standard 512-dim embeddings (compatible with most FAISS implementations)
- Fits comfortably in Colab free tier (15GB RAM, 12GB GPU)
- Production-ready performance

**Alternatives:**
- `clip-vit-b-16`: Slower, better quality (768-dim)
- `clip-vit-l-14`: Much slower, best quality (768-dim)

---

## Troubleshooting

### Issue: GPU not detected
```python
import torch
print(torch.cuda.is_available())  # Should be True in Colab with GPU runtime
```

**Solution**: Runtime → Change runtime type → GPU (T4)

### Issue: Out of memory
**Solution**:
- Reduce batch size (not currently used, but for future optimization)
- Use `clip-vit-b-32` (not larger models)
- Restart runtime and clear outputs

### Issue: Model download fails
**Solution**:
```python
# Pre-download model
from transformers import CLIPModel
model = CLIPModel.from_pretrained("openai/clip-vit-b-32")
model.save_pretrained("/content/drive/MyDrive/clip_model")

# Load from saved location
generator = CLIPEmbeddingGenerator(model_name="/content/drive/MyDrive/clip_model")
```

### Issue: Frame extraction fails
**Solution**:
- Verify video file is not corrupted: `!ffmpeg -v error -i clip.mp4 -f null -`
- Try single frame strategy: `strategy="single"`
- Check file permissions in Google Drive

### Issue: Embeddings not loading in backend
**Solution**:
- Verify files exist: `!ls -lh embeddings/`
- Check file paths in backend: Ensure paths point to `backend/storage/`
- Copy files to backend: `!cp embeddings/*.npy ../backend/storage/`

---

## Performance Estimates

**Google Colab (T4 GPU, Free Tier)**:
- Model loading: ~30 seconds
- Per clip (3 frames): ~100ms
- 100 clips: ~10-15 seconds
- 1000 clips: ~2 minutes

**Storage Requirements**:
- CLIP model: 600 MB
- Embeddings (1000 clips): ~2 MB (512 * 1000 * 4 bytes)
- Metadata: <1 MB

---

## Next Steps

After generating embeddings:

1. **Validate**: Run `integration_test.py` to ensure all tests pass
2. **Copy to Backend** (if integrating with FastAPI backend):
   ```bash
   !cp /content/drive/MyDrive/HackathonProject/embeddings/*.npy ../backend/storage/
   ```
3. **Member 3**: Load embeddings into FAISS visual index
4. **Member 4**: Update frontend to support visual search queries
5. **Testing**: Benchmark search accuracy and speed

---

## Support

For questions or issues:
1. Check troubleshooting section above
2. Run integration tests to diagnose problems
3. Review plan document: `~/.claude/plans/elegant-tinkering-hoare.md`
4. Contact team lead or @AILead (Member 2)

---

## License & Attribution

- CLIP Model: © OpenAI ([Link](https://github.com/openai/CLIP))
- HuggingFace Transformers: Apache 2.0
- This codebase: Hackathon 2026 Team Project
