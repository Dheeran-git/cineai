"""
Visual Embedding Service for SmartCut AI
CLIP-based visual embedding generation for semantic video search.
Member 2: AI Engineer - Backend Integration

Integrates CLIP embeddings from colab_code/embedding_gen.py with the backend
search system for visual similarity search.
"""
import numpy as np
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Lazy loading for heavy CLIP imports
_clip_model = None
_clip_processor = None


def get_clip_model():
    """Lazy load CLIP model to avoid slow startup."""
    global _clip_model, _clip_processor
    if _clip_model is None:
        try:
            import torch
            from transformers import CLIPProcessor, CLIPModel
            
            model_name = "openai/clip-vit-b-32"
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            logger.info(f"Loading CLIP model: {model_name} on {device}")
            _clip_model = CLIPModel.from_pretrained(model_name).to(device)
            _clip_processor = CLIPProcessor.from_pretrained(model_name)
            _clip_model.eval()
            
            logger.info("CLIP model loaded successfully!")
        except Exception as e:
            logger.warning(f"Failed to load CLIP model: {e}. Using mock embeddings.")
            _clip_model = "mock"
            _clip_processor = None
    
    return _clip_model, _clip_processor


class VisualEmbeddingService:
    """
    CLIP-based visual embedding service for video frames.
    
    Provides:
    - Visual embedding generation for images/frames
    - Text-to-image query embedding
    - Integration with pre-computed embeddings from Colab
    """
    
    EMBEDDING_DIM = 512  # CLIP ViT-B/32 dimension
    STORAGE_DIR = Path("./storage")
    EMBEDDINGS_FILE = "video_embeddings.npy"
    PATHS_FILE = "video_paths.npy"
    CONFIG_FILE = "embedding_config.json"
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = "cpu"
        self._embeddings_cache = None
        self._paths_cache = None
        
    def _get_model(self):
        """Get the CLIP model, loading if necessary."""
        if self.model is None:
            self.model, self.processor = get_clip_model()
            if self.model != "mock":
                import torch
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
        return self.model, self.processor
    
    def embed_image(self, image: np.ndarray) -> np.ndarray:
        """
        Generate CLIP embedding for a single image.
        
        Args:
            image: numpy array in RGB format (H, W, 3)
            
        Returns:
            512-dim normalized embedding as numpy array
        """
        model, processor = self._get_model()
        
        if model == "mock":
            # Mock embedding for testing
            np.random.seed(hash(image.tobytes()[:100]) % 2**32)
            embedding = np.random.randn(self.EMBEDDING_DIM).astype(np.float32)
            return embedding / np.linalg.norm(embedding)
        
        try:
            import torch
            from PIL import Image
            
            # Convert numpy to PIL
            pil_image = Image.fromarray(image.astype('uint8'))
            
            # Preprocess and embed
            inputs = processor(images=pil_image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                image_features = model.get_image_features(**inputs)
            
            # L2 normalize
            embedding = image_features / image_features.norm(dim=-1, keepdim=True)
            return embedding.cpu().numpy().flatten()
            
        except Exception as e:
            logger.error(f"Image embedding failed: {e}")
            return np.zeros(self.EMBEDDING_DIM, dtype=np.float32)
    
    def embed_text_query(self, query: str) -> np.ndarray:
        """
        Generate CLIP text embedding for visual search query.
        
        Args:
            query: Natural language description (e.g., "close-up shot with red lighting")
            
        Returns:
            512-dim normalized text embedding
        """
        model, processor = self._get_model()
        
        if model == "mock":
            # Mock embedding
            np.random.seed(hash(query) % 2**32)
            embedding = np.random.randn(self.EMBEDDING_DIM).astype(np.float32)
            return embedding / np.linalg.norm(embedding)
        
        try:
            import torch
            
            # Preprocess text
            inputs = processor(text=[query], return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                text_features = model.get_text_features(**inputs)
            
            # L2 normalize
            embedding = text_features / text_features.norm(dim=-1, keepdim=True)
            return embedding.cpu().numpy().flatten()
            
        except Exception as e:
            logger.error(f"Text embedding failed: {e}")
            return np.zeros(self.EMBEDDING_DIM, dtype=np.float32)
    
    def load_precomputed_embeddings(self) -> tuple:
        """
        Load pre-computed embeddings from Colab.
        
        Returns:
            Tuple of (embeddings_array, paths_array, config_dict)
            Returns (None, None, None) if files don't exist
        """
        if self._embeddings_cache is not None:
            return self._embeddings_cache, self._paths_cache, self._config_cache
        
        embeddings_path = self.STORAGE_DIR / self.EMBEDDINGS_FILE
        paths_path = self.STORAGE_DIR / self.PATHS_FILE
        config_path = self.STORAGE_DIR / self.CONFIG_FILE
        
        try:
            if embeddings_path.exists() and paths_path.exists():
                self._embeddings_cache = np.load(embeddings_path)
                self._paths_cache = np.load(paths_path, allow_pickle=True)
                
                self._config_cache = {}
                if config_path.exists():
                    with open(config_path, "r") as f:
                        self._config_cache = json.load(f)
                
                logger.info(f"Loaded {len(self._embeddings_cache)} visual embeddings")
                return self._embeddings_cache, self._paths_cache, self._config_cache
            else:
                logger.warning(f"Visual embeddings not found at {self.STORAGE_DIR}")
                return None, None, None
                
        except Exception as e:
            logger.error(f"Failed to load embeddings: {e}")
            return None, None, None
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded embeddings."""
        embeddings, paths, config = self.load_precomputed_embeddings()
        
        if embeddings is None:
            return {
                "loaded": False,
                "error": "No embeddings found",
                "storage_path": str(self.STORAGE_DIR)
            }
        
        return {
            "loaded": True,
            "num_embeddings": len(embeddings),
            "embedding_dim": embeddings.shape[1] if len(embeddings.shape) > 1 else 0,
            "model_name": config.get("model_name", "unknown"),
            "frame_strategy": config.get("frame_strategy", "unknown"),
            "storage_path": str(self.STORAGE_DIR)
        }
    
    def clear_cache(self):
        """Clear cached embeddings to free memory."""
        self._embeddings_cache = None
        self._paths_cache = None
        self._config_cache = None
        logger.info("Visual embedding cache cleared")


# Singleton instance
visual_embedding_service = VisualEmbeddingService()
