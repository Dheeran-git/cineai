"""
CLIP Visual Embedding Generator
Member 2: AI Engineer - Embeddings

Generates 512-dimensional CLIP embeddings from video frames for semantic video search.
Uses openai/clip-vit-b-32 model from HuggingFace.

Output:
- video_embeddings.npy: (N, 512) CLIP embeddings, L2 normalized
- video_paths.npy: (N,) video clip paths
- embedding_config.json: Model configuration
- frame_metadata.json: Per-clip extraction details
"""

import torch
import numpy as np
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
from tqdm import tqdm
import json
from pathlib import Path
from typing import List, Dict, Optional
import time
import frame_extractor


class CLIPEmbeddingGenerator:
    """
    CLIP-based visual embedding generator for video clips

    Uses 3-frame strategy (start, middle, end) with mean pooling
    to create robust 512-dim embeddings for each video clip.
    """

    def __init__(self, model_name: str = "openai/clip-vit-b-32", device: Optional[str] = None):
        """
        Initialize CLIP model

        Args:
            model_name: HuggingFace model identifier
            device: Device to use ('cuda' or 'cpu'). Auto-detects if None.
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name = model_name
        self.embedding_dim = 512  # CLIP ViT-B/32 dimension

        print(f"Loading CLIP model: {model_name}")
        print(f"Device: {self.device}")

        # Load model and processor
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)

        # Set to evaluation mode (no gradients needed)
        self.model.eval()

        print(f"Model loaded successfully!")
        print(f"Embedding dimension: {self.embedding_dim}")

    def embed_image(self, image: np.ndarray) -> np.ndarray:
        """
        Generate CLIP embedding for a single image

        Args:
            image: numpy array in RGB format (H, W, 3)

        Returns:
            512-dim normalized embedding as numpy array
        """
        # Convert numpy array to PIL Image
        pil_image = Image.fromarray(image.astype('uint8'))

        # Preprocess image for CLIP
        inputs = self.processor(images=pil_image, return_tensors="pt")

        # Move tensors to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Generate embedding
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)

        # L2 normalize for cosine similarity (FAISS inner product)
        embedding = image_features / image_features.norm(dim=-1, keepdim=True)

        # Convert to numpy and flatten
        return embedding.cpu().numpy().flatten()

    def embed_video_clip(
        self,
        video_path: str,
        strategy: str = "triple",
        return_metadata: bool = False
    ) -> np.ndarray:
        """
        Generate embedding for a video clip

        Args:
            video_path: Path to .mp4 video file
            strategy: "triple" (3 frames) or "single" (middle frame only)
            return_metadata: If True, return (embedding, metadata) tuple

        Returns:
            512-dim normalized embedding
            If return_metadata=True: (embedding, metadata_dict)
        """
        start_time = time.time()
        metadata = {
            "video_path": video_path,
            "strategy": strategy,
            "frames_extracted": 0,
            "frame_indices": [],
            "extraction_time": 0,
            "embedding_time": 0
        }

        try:
            if strategy == "triple":
                # Extract 3 frames: start, middle, end
                frames = frame_extractor.extract_frames_triple(video_path)
                metadata["frames_extracted"] = len(frames)

                # Get video info for frame indices
                video_info = frame_extractor.get_video_info(video_path)
                frame_count = video_info["frame_count"]
                metadata["frame_indices"] = [0, frame_count // 2, max(0, frame_count - 1)]

                extraction_time = time.time()
                metadata["extraction_time"] = extraction_time - start_time

                # Embed each frame
                embeddings = []
                for frame in frames:
                    emb = self.embed_image(frame)
                    embeddings.append(emb)

                metadata["embedding_time"] = time.time() - extraction_time

                # Mean pooling across frames
                embedding = np.mean(embeddings, axis=0)

                # Renormalize after mean pooling
                embedding = embedding / np.linalg.norm(embedding)

            else:  # strategy == "single"
                # Extract single middle frame
                frame = frame_extractor.extract_middle_frame(video_path)
                metadata["frames_extracted"] = 1

                # Get video info for frame index
                video_info = frame_extractor.get_video_info(video_path)
                frame_count = video_info["frame_count"]
                metadata["frame_indices"] = [frame_count // 2]

                extraction_time = time.time()
                metadata["extraction_time"] = extraction_time - start_time

                # Embed single frame
                embedding = self.embed_image(frame)

                metadata["embedding_time"] = time.time() - extraction_time

            metadata["total_time"] = time.time() - start_time
            metadata["status"] = "success"

            if return_metadata:
                return embedding, metadata
            else:
                return embedding

        except Exception as e:
            metadata["status"] = "error"
            metadata["error"] = str(e)
            metadata["total_time"] = time.time() - start_time

            if return_metadata:
                # Return zero embedding on error
                zero_embedding = np.zeros(self.embedding_dim, dtype=np.float32)
                return zero_embedding, metadata
            else:
                raise

    def batch_process_clips(
        self,
        clips_dir: str,
        output_dir: str,
        strategy: str = "triple",
        batch_size: int = 16,
        file_pattern: str = "*.mp4"
    ) -> Dict:
        """
        Process all video clips in a directory

        Args:
            clips_dir: Directory containing .mp4 video clips
            output_dir: Directory to save output files
            strategy: "triple" or "single" frame extraction
            batch_size: Batch size (not currently used, kept for future optimization)
            file_pattern: Glob pattern for video files

        Returns:
            Configuration dictionary with processing stats
        """
        clips_dir = Path(clips_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)

        # Find all video clips
        clip_paths = sorted(clips_dir.glob(file_pattern))
        print(f"\nFound {len(clip_paths)} video clips in {clips_dir}")

        if len(clip_paths) == 0:
            print(f"Warning: No video files found matching pattern '{file_pattern}'")
            return {
                "error": "No video files found",
                "clips_dir": str(clips_dir),
                "file_pattern": file_pattern
            }

        # Process each clip
        embeddings = []
        paths = []
        metadata_list = {}

        start_time = time.time()

        for clip_path in tqdm(clip_paths, desc="Generating CLIP embeddings"):
            try:
                embedding, meta = self.embed_video_clip(
                    str(clip_path),
                    strategy=strategy,
                    return_metadata=True
                )

                embeddings.append(embedding)
                paths.append(str(clip_path))
                metadata_list[clip_path.name] = meta

            except Exception as e:
                print(f"\nError processing {clip_path.name}: {e}")
                metadata_list[clip_path.name] = {
                    "status": "error",
                    "error": str(e)
                }

        total_time = time.time() - start_time

        # Convert to numpy arrays
        embeddings_array = np.array(embeddings, dtype=np.float32)
        paths_array = np.array(paths)

        print(f"\n{'='*60}")
        print(f"Processing complete!")
        print(f"Total clips: {len(clip_paths)}")
        print(f"Successfully processed: {len(embeddings)}")
        print(f"Failed: {len(clip_paths) - len(embeddings)}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average time per clip: {total_time/len(clip_paths):.3f}s")
        print(f"{'='*60}\n")

        # Save embeddings
        embeddings_path = output_dir / "video_embeddings.npy"
        np.save(embeddings_path, embeddings_array)
        print(f"Saved embeddings to: {embeddings_path}")
        print(f"  Shape: {embeddings_array.shape}")
        print(f"  Dtype: {embeddings_array.dtype}")

        # Save paths
        paths_path = output_dir / "video_paths.npy"
        np.save(paths_path, paths_array)
        print(f"Saved paths to: {paths_path}")
        print(f"  Shape: {paths_array.shape}")

        # Save configuration
        config = {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "frame_strategy": strategy,
            "aggregation": "mean_pool" if strategy == "triple" else "single_frame",
            "normalization": "l2",
            "device": self.device,
            "total_clips_found": len(clip_paths),
            "clips_processed": len(embeddings),
            "clips_failed": len(clip_paths) - len(embeddings),
            "total_processing_time": total_time,
            "avg_time_per_clip": total_time / len(clip_paths) if len(clip_paths) > 0 else 0,
            "clips_dir": str(clips_dir),
            "output_dir": str(output_dir),
            "file_pattern": file_pattern
        }

        config_path = output_dir / "embedding_config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        print(f"Saved config to: {config_path}")

        # Save frame metadata
        metadata_path = output_dir / "frame_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata_list, f, indent=2)
        print(f"Saved frame metadata to: {metadata_path}")

        print(f"\n✓ All files saved successfully to {output_dir}")

        return config

    def embed_text_query(self, query: str) -> np.ndarray:
        """
        Generate CLIP text embedding for search query

        This enables text-to-image search using CLIP's multimodal capabilities.

        Args:
            query: Text search query (e.g., "close-up shot with red lighting")

        Returns:
            512-dim normalized text embedding
        """
        # Preprocess text
        inputs = self.processor(text=[query], return_tensors="pt", padding=True)

        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Generate text embedding
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)

        # L2 normalize
        embedding = text_features / text_features.norm(dim=-1, keepdim=True)

        return embedding.cpu().numpy().flatten()


def main():
    """
    Main execution function for Google Colab or local testing
    """
    import argparse

    parser = argparse.ArgumentParser(description="Generate CLIP embeddings for video clips")
    parser.add_argument(
        "--clips_dir",
        type=str,
        default="/content/drive/MyDrive/HackathonProject/clips",
        help="Directory containing video clips"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="/content/drive/MyDrive/HackathonProject/embeddings",
        help="Directory to save embeddings"
    )
    parser.add_argument(
        "--strategy",
        type=str,
        choices=["triple", "single"],
        default="triple",
        help="Frame extraction strategy: triple (3 frames) or single (middle frame)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="openai/clip-vit-b-32",
        help="HuggingFace CLIP model name"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.mp4",
        help="File pattern for video clips"
    )

    args = parser.parse_args()

    print("="*60)
    print("CLIP Visual Embedding Generator")
    print("Member 2: AI Engineer - Embeddings")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  Clips directory: {args.clips_dir}")
    print(f"  Output directory: {args.output_dir}")
    print(f"  Frame strategy: {args.strategy}")
    print(f"  CLIP model: {args.model}")
    print(f"  File pattern: {args.pattern}")
    print(f"\n{'='*60}\n")

    # Initialize generator
    generator = CLIPEmbeddingGenerator(model_name=args.model)

    # Process all clips
    stats = generator.batch_process_clips(
        clips_dir=args.clips_dir,
        output_dir=args.output_dir,
        strategy=args.strategy,
        file_pattern=args.pattern
    )

    print("\n" + "="*60)
    print("Processing Complete!")
    print("="*60)
    print("\nOutput files:")
    print(f"  - video_embeddings.npy  ({stats.get('clips_processed', 0)}, 512)")
    print(f"  - video_paths.npy       ({stats.get('clips_processed', 0)},)")
    print(f"  - embedding_config.json")
    print(f"  - frame_metadata.json")
    print("\nNext steps:")
    print("  1. Run integration_test.py to validate embeddings")
    print("  2. Copy embeddings to backend/storage/ for backend integration")
    print("  3. Member 3: Load embeddings into FAISS visual index")
    print("="*60)


if __name__ == "__main__":
    main()
