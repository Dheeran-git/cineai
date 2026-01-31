# 🎬 Semantic Video Search Engine (Hackathon 2026)

> **Team Coordination & Setup Guide**

This repository contains the source code and notebooks for the **Semantic Footage Search Engine**, a tool that allows video editors to search for footage using natural language (intent) rather than keywords.

---

## � Team Roles & Branch Strategy

We are working in parallel branches to move fast. **Do not push directly to `main` until the end.**

| Role | Member | Branch Name | Responsibilities |
| :--- | :--- | :--- | :--- |
| **Member 1** | @VideoLead | `feature/video-processing` | Video download (`yt-dlp`) & Scene Splitting (`PySceneDetect`). Output: `.mp4` clips. |
| **Member 2** | @AILead | `feature/embeddings` | CLIP Model integration. Output: `embeddings.npy`. |
| **Member 3** | @SearchLead | `feature/vector-db` | FAISS Indexing & Search Logic. |
| **Member 4** | **YOU (Frontend)** | `feature/frontend-ui` | Streamlit UI & Final Integration. |

---

## 🛠️ Project Structure (Google Drive + Colab)

Since we are using **Google Colab** for GPUs, our "deployment" is actually a specific folder structure in Google Drive.

**Shared Drive Path:**
`/content/drive/MyDrive/HackathonProject/`

**Folder Layout:**
```text
HackathonProject/
├── videos/          # Raw full-length videos (Managed by Member 1)
├── clips/           # Shortened clips (Output of Member 1)
├── embeddings/      # .npy files (Output of Member 2)
└── db/              # FAISS index files (Output of Member 3)
```

---

## 🚀 How to Run (For Each Member)

### 🧑‍💻 Member 1: Video Processing
1.  Checkout branch `feature/video-processing`.
2.  Open your Colab Notebook.
3.  Mount Drive.
4.  Run the **Video Splitter Script** (see `colab_code/video_splitter.py`).
5.  **Deliverable:** Ensure `HackathonProject/clips/` is full of small `.mp4` files.

### 🧑‍🔬 Member 2: Embeddings
1.  Checkout branch `feature/embeddings`.
2.  Wait for Member 1 to generate at least a few clips.
3.  Run the **Embedding Generator Script** (see `colab_code/embedding_gen.py`).
4.  **Deliverable:** `video_embeddings.npy` and `video_paths.npy` in the `embeddings/` folder.

### 🧑‍🚀 Member 3: Search Backend
1.  Checkout branch `feature/vector-db`.
2.  Write the search logic class.
3.  Test searching against the `.npy` files provided by Member 2.

### 🎨 Member 4 (YOU): Frontend UI
1.  Checkout branch `feature/frontend-ui`.
2.  Create/Edit `app.py`.
3.  **Run in Colab:**
    ```python
    !npm install localtunnel
    !streamlit run app.py &>/content/logs.txt & npx localtunnel --port 8501
    ```
4.  **Authentication:** The password for LocalTunnel is your Colab instance IP. Run this to get it:
    ```python
    import urllib
    print(urllib.request.urlopen('https://ipv4.icanhazip.com').read().decode('utf8').strip("\n"))
    ```

---

## 📥 Git Workflow

1.  **Pull changes** often:
    ```bash
    git checkout your-branch
    git pull origin main  # Get updates if any
    ```
2.  **Commit your Notebooks/Scripts**:
    ```bash
    git add .
    git commit -m "Updated logic for X"
    git push origin your-branch
    ```
3.  **Merge (Final Hour)**:
    Create a Pull Request to merge all branches into `main` for the final submission.

---

## 🧑‍🔬 Member 2: AI Engineer - Visual Embeddings

Member 2 is responsible for generating CLIP-based visual embeddings for semantic video search.

### Deliverables
- **colab_code/embedding_gen.py**: CLIP embedding generator using `openai/clip-vit-b-32`
- **colab_code/frame_extractor.py**: Frame extraction utilities (triple/single strategies)
- **colab_code/audio_analysis.py**: Bonus audio analysis for silence detection
- **colab_code/integration_test.py**: Validation tests for embeddings

### Output Files
| File | Shape | Description |
|------|-------|-------------|
| `video_embeddings.npy` | (N, 512) | CLIP visual embeddings, L2 normalized |
| `video_paths.npy` | (N,) | Corresponding video clip paths |
| `embedding_config.json` | - | Model configuration and stats |
| `frame_metadata.json` | - | Per-clip extraction details |

### Integration with Backend
1. Copy embeddings to `backend/storage/`:
   ```bash
   cp embeddings/*.npy backend/storage/
   ```
2. Backend auto-loads embeddings into FAISS visual index on startup
3. Visual search available via `semantic_search_service.search_by_visual_query()`

### Quick Start (Colab)
```python
from embedding_gen import CLIPEmbeddingGenerator

generator = CLIPEmbeddingGenerator(model_name="openai/clip-vit-b-32")
stats = generator.batch_process_clips(
    clips_dir="/content/drive/MyDrive/HackathonProject/clips",
    output_dir="/content/drive/MyDrive/HackathonProject/embeddings",
    strategy="triple"
)
```

See **colab_code/README.md** for full documentation.

---

## 🆘 Troubleshooting

*   **"No Embeddings Found"**: Member 2 hasn't run their script yet.
*   **"Streamlit Tunnel Crashed"**: Re-run the last cell in the UI notebook.
*   **"Drive not mounted"**: Always run `drive.mount('/content/drive')` first!
