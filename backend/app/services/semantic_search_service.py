"""
Semantic Search Service for SmartCut AI
FAISS-based vector indexing and intent-based retrieval.
Supports both intent-based (text) and visual (CLIP) similarity search.
"""
import numpy as np
import logging
import pickle
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from app.services.intent_embedding_service import intent_embedding_service
from app.services.visual_embedding_service import visual_embedding_service

logger = logging.getLogger(__name__)

# Optional ML imports
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS not available. Using mock vector search.")


@dataclass
class SearchResult:
    """A single semantic search result with explainability."""
    result_id: int
    take_id: int
    moment_id: int
    start_time: float
    end_time: float
    confidence: float
    transcript_snippet: str
    emotion_label: str
    file_name: str
    file_path: str
    reasoning: Dict[str, Any]

class NumpyIndex:
    """A pure-numpy implementation of FAISS IndexFlatIP for fallback."""
    def __init__(self, d):
        self.d = d
        self.vectors = np.empty((0, d), dtype=np.float32)
        
    @property
    def ntotal(self):
        return self.vectors.shape[0]
        
    def add(self, x):
        if x.ndim == 1:
            x = x.reshape(1, -1)
        self.vectors = np.concatenate([self.vectors, x], axis=0)
        
    def search(self, q, k):
        if self.ntotal == 0:
            return np.array([[]]), np.array([[]])
        
        # Cosine similarity (assuming normalized)
        # q: (1, d), vectors: (n, d) -> scores: (1, n)
        scores = np.dot(q, self.vectors.T)
        
        # Top-k
        # argsort gives ascending, so we take tail and reverse
        indices = np.argsort(scores, axis=1)[:, -k:][:, ::-1]
        
        # Get corresponding scores
        top_scores = np.take_along_axis(scores, indices, axis=1)
        
        return top_scores, indices


class SemanticSearchService:
    """
    Vector-based semantic search using FAISS (or mock if unavailable).
    Indexes video moments and retrieves by intent similarity.
    Supports visual (CLIP) search via integrated visual index.
    """
    
    INDEX_PATH = "./storage/faiss_index.bin"
    METADATA_PATH = "./storage/faiss_metadata.pkl"
    
    # Visual index paths (for CLIP embeddings from Colab)
    VISUAL_INDEX_PATH = "./storage/faiss_visual_index.bin"
    VISUAL_EMBEDDINGS_PATH = "./storage/video_embeddings.npy"
    VISUAL_PATHS_PATH = "./storage/video_paths.npy"
    
    def __init__(self):
        self.dimension = intent_embedding_service.EMBEDDING_DIM
        self.index: Any = None  # faiss.IndexFlatIP or MockIndex
        self.metadata: List[Dict] = []  # Parallel list of moment metadata
        
        # Visual search components
        self.visual_dimension = visual_embedding_service.EMBEDDING_DIM  # 512 for CLIP
        self.visual_index: Optional[faiss.IndexFlatIP] = None
        self.visual_paths: List[str] = []
        
        self._load_or_create_index()
        self._load_visual_index()
    
    def _load_or_create_index(self):
        """Load existing index or create a new one."""
        os.makedirs("./storage", exist_ok=True)
        
        meta_exists = os.path.exists(self.METADATA_PATH)
        
        if FAISS_AVAILABLE and os.path.exists(self.INDEX_PATH) and meta_exists:
            try:
                self.index = faiss.read_index(self.INDEX_PATH)
                with open(self.METADATA_PATH, "rb") as f:
                    self.metadata = pickle.load(f)
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            except Exception as e:
                logger.warning(f"Failed to load FAISS: {e}. Creating new.")
                self._create_new_index()
        elif meta_exists:
            # Fallback: Load metadata for keyword search even without FAISS
            try:
                with open(self.METADATA_PATH, "rb") as f:
                    self.metadata = pickle.load(f)
                self.index = NumpyIndex(self.dimension)
                logger.info(f"Loaded {len(self.metadata)} metadata items for keyword fallback")
            except Exception as e:
                logger.warning(f"Failed to load metadata: {e}. Creating new.")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index (or mock)."""
        if FAISS_AVAILABLE:
            self.index = faiss.IndexFlatIP(self.dimension)
        else:
            # Use Numpy fallback
            self.index = NumpyIndex(self.dimension)
            
        self.metadata = []
        logger.info(f"Created new {'FAISS' if FAISS_AVAILABLE else 'MOCK'} index")
    
    def _load_visual_index(self):
        """Load or create visual index for CLIP embeddings."""
        if not FAISS_AVAILABLE:
            # Use NumpyIndex for visual features too
            self.visual_index = NumpyIndex(self.visual_dimension)
            # Try to load if embeddings exist
            if os.path.exists(self.VISUAL_EMBEDDINGS_PATH):
                try:
                    embeddings = np.load(self.VISUAL_EMBEDDINGS_PATH)
                    self.visual_index.add(embeddings.astype(np.float32))
                    if os.path.exists(self.VISUAL_PATHS_PATH):
                        self.visual_paths = list(np.load(self.VISUAL_PATHS_PATH, allow_pickle=True))
                    logger.info(f"Loaded visual NumpyIndex with {self.visual_index.ntotal} vectors")
                except Exception as e:
                    logger.warning(f"Failed to load numpy visual embeddings: {e}")
            else:
                logger.info("Numpy visual index created (no embeddings found)")
            return

        os.makedirs("./storage", exist_ok=True)
        
        # Try loading pre-built visual index
        if os.path.exists(self.VISUAL_INDEX_PATH):
            try:
                self.visual_index = faiss.read_index(self.VISUAL_INDEX_PATH)
                if os.path.exists(self.VISUAL_PATHS_PATH):
                    self.visual_paths = list(np.load(self.VISUAL_PATHS_PATH, allow_pickle=True))
                logger.info(f"Loaded visual FAISS index with {self.visual_index.ntotal} vectors")
                return
            except Exception as e:
                logger.warning(f"Failed to load visual index: {e}")
        
        # Try building from embeddings file
        if os.path.exists(self.VISUAL_EMBEDDINGS_PATH):
            try:
                embeddings = np.load(self.VISUAL_EMBEDDINGS_PATH)
                if os.path.exists(self.VISUAL_PATHS_PATH):
                    self.visual_paths = list(np.load(self.VISUAL_PATHS_PATH, allow_pickle=True))
                
                self.visual_index = faiss.IndexFlatIP(self.visual_dimension)
                self.visual_index.add(embeddings.astype(np.float32))
                logger.info(f"Built visual index from embeddings: {self.visual_index.ntotal} vectors")
                
                # Save the built index
                faiss.write_index(self.visual_index, self.VISUAL_INDEX_PATH)
                return
            except Exception as e:
                logger.warning(f"Failed to build visual index: {e}")
        
        # Create empty visual index
        self.visual_index = faiss.IndexFlatIP(self.visual_dimension)
        self.visual_paths = []
        logger.info("Created empty visual index (no embeddings found)")
    
    def save_index(self):
        """Persist index to disk."""
        os.makedirs("./storage", exist_ok=True)
        if FAISS_AVAILABLE and self.index != "MOCK_INDEX":
            faiss.write_index(self.index, self.INDEX_PATH)
        
        with open(self.METADATA_PATH, "wb") as f:
            pickle.dump(self.metadata, f)
        logger.info(f"Saved index metadata with {len(self.metadata)} items")
    
    def index_moment(
        self,
        moment_id: int,
        take_id: int,
        start_time: float,
        end_time: float,
        embedding: np.ndarray,
        transcript_snippet: str = "",
        emotion_label: str = "neutral",
        file_name: str = "",
        file_path: str = "",
        audio_features: Dict = None,
        timing_data: Dict = None
    ):
        """
        Add a moment's embedding to the index.
        """
        # Ensure normalized for cosine similarity
        embedding = embedding.astype(np.float32)
        if np.linalg.norm(embedding) > 0:
            embedding = embedding / np.linalg.norm(embedding)
        
        # Add to Index (FAISS or Numpy)
        if self.index is not None:
             self.index.add(embedding.reshape(1, -1))
        
        # Store metadata (acts as source of truth for mock mode too)
        self.metadata.append({
            "moment_id": moment_id,
            "take_id": take_id,
            "start_time": start_time,
            "end_time": end_time,
            "transcript_snippet": transcript_snippet,
            "emotion_label": emotion_label,
            "file_name": file_name,
            "file_path": file_path,
            "audio_features": audio_features or {},
            "timing_data": timing_data or {}
        })

    def _keyword_search(self, query: str, top_k: int, filters: Dict = None) -> List[SearchResult]:
        """Simple keyword-based retrieval for when FAISS/Embeddings are unavailable."""
        query_terms = query.lower().split()
        results = []
        
        for i, meta in enumerate(self.metadata):
            score = 0.0
            
            # Apply filters first
            if filters:
                if filters.get("take_id") and meta["take_id"] != filters["take_id"]:
                    continue
                if filters.get("emotion") and meta["emotion_label"] != filters["emotion"]:
                    continue
            
            transcript = meta.get("transcript_snippet", "").lower()
            emotion = meta.get("emotion_label", "").lower()
            fname = meta.get("file_name", "").lower()
            timing_pattern = meta.get("timing_data", {}).get("pattern", "").lower()
            laughter = "laughter" if meta.get("audio_features", {}).get("laughter_detected") else ""
            
            # Accurate scoring: prioritize dialogue matches
            matches = 0
            for term in query_terms:
                if term in transcript: matches += 5
                if term in emotion: matches += 3
                if term in fname: matches += 2
                if term in timing_pattern: matches += 4 # High weight for behavioral patterns
                if term in laughter: matches += 6 # Very high weight for laughter
            
            if matches > 0 or not query_terms:
                # Basic similarity score [0, 1]
                score = min(0.95, 0.5 + (matches * 0.1))
                
                # Mock reasoning for keyword match
                parsed_intent = intent_embedding_service.parse_query_intent(query)
                reasoning = self._generate_reasoning(query, parsed_intent, meta, score)
                reasoning["matched_because"].insert(0, f"Keyword match found in {('transcript' if any(t in transcript for t in query_terms) else 'metadata')}")
                
                results.append(SearchResult(
                    result_id=i,
                    take_id=meta["take_id"],
                    moment_id=meta["moment_id"],
                    start_time=meta["start_time"],
                    end_time=meta["end_time"],
                    confidence=score,
                    transcript_snippet=meta["transcript_snippet"],
                    emotion_label=meta["emotion_label"],
                    file_name=meta.get("file_name", ""),
                    file_path=meta.get("file_path", ""),
                    reasoning=reasoning
                ))
        
        # Sort by score and limit
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:top_k]
    
    def search_by_intent(
        self,
        query: str,
        top_k: int = 10,
        filters: Dict = None
    ) -> List[SearchResult]:
        """
        Search for moments matching the editor's intent query.
        """
        if not self.metadata:
            return []
            
        if self.index.ntotal > 0 or (not FAISS_AVAILABLE and self.metadata):
            # Check if using Mock Embeddings (heuristic check or config)
            # If FAISS is missing, we are definitely using Mock/Numpy index with random vectors.
            if not FAISS_AVAILABLE:
                logger.info("Using Keyword Fallback Search (FAISS unavailable)")
                return self._keyword_search(query, top_k, filters)

            # Generate query embedding
            query_embedding = intent_embedding_service.embed_query(query)
            query_embedding = query_embedding.reshape(1, -1)
            
             # Search (FAISS or Numpy)
            k = min(top_k * 3, self.index.ntotal)
            scores, indices = self.index.search(query_embedding, k)
            current_scores = scores[0]
            current_indices = indices[0]
        else:
            return []

        # Parse query intent for filtering and explainability
        parsed_intent = intent_embedding_service.parse_query_intent(query)
        
        results = []
        for i, idx in enumerate(current_indices):
            idx = int(idx)
            if idx < 0 or idx >= len(self.metadata):
                continue
            
            score = float(current_scores[i])
            meta = self.metadata[idx]
            
            # Apply filters
            if filters:
                if filters.get("take_id") and meta["take_id"] != filters["take_id"]:
                    continue
                if filters.get("emotion") and meta["emotion_label"] != filters["emotion"]:
                    continue
            
            # Generate reasoning
            reasoning = self._generate_reasoning(query, parsed_intent, meta, score)
            
            results.append(SearchResult(
                result_id=idx,
                take_id=meta["take_id"],
                moment_id=meta["moment_id"],
                start_time=meta["start_time"],
                end_time=meta["end_time"],
                confidence=score,
                transcript_snippet=meta["transcript_snippet"],
                emotion_label=meta["emotion_label"],
                file_name=meta.get("file_name", ""),
                file_path=meta.get("file_path", ""),
                reasoning=reasoning
            ))
            
            if len(results) >= top_k:
                break
        
        return results
    
    def _generate_reasoning(
        self,
        query: str,
        parsed_intent: Dict,
        metadata: Dict,
        score: float
    ) -> Dict[str, Any]:
        """
        Generate human-readable reasoning for why a result matched.
        """
        matched_because = []
        
        # Emotion match
        emotion = metadata.get("emotion_label", "neutral")
        if parsed_intent["emotions"]:
            if emotion in parsed_intent["emotions"]:
                matched_because.append(f"Emotion matches: {emotion}")
            else:
                matched_because.append(f"Detected emotion: {emotion}")
        else:
            matched_because.append(f"Detected emotion: {emotion}")
        
        # Timing patterns
        timing = metadata.get("timing_data", {})
        audio = metadata.get("audio_features", {})
        
        if timing.get("pattern"):
            pattern = timing["pattern"].replace("_", " ")
            matched_because.append(f"Timing pattern: {pattern}")
        
        if audio.get("pause_before_duration", 0) > 0.5:
            duration = audio["pause_before_duration"]
            matched_because.append(f"{duration:.1f}s pause before speaking")
        
        if audio.get("pause_after_duration", 0) > 0.5:
            duration = audio["pause_after_duration"]
            matched_because.append(f"{duration:.1f}s pause after speaking")
        
        # Transcript relevance
        transcript = metadata.get("transcript_snippet", "")
        if transcript:
            matched_because.append(f"Dialogue: \"{transcript[:50]}...\"" if len(transcript) > 50 else f"Dialogue: \"{transcript}\"")
        else:
            matched_because.append("Silent moment / non-verbal reaction")
        
        return {
            "matched_because": matched_because,
            "emotion_detected": emotion,
            "timing_pattern": timing.get("pattern", "normal"),
            "confidence_score": round(score * 100, 1),
            "query_intent": parsed_intent
        }
    
    def get_suggestions(self, partial_query: str) -> List[str]:
        """
        Get query suggestions for autocomplete.
        """
        suggestions = [
            "hesitant reaction before answering",
            "tense pause before dialogue",
            "awkward silence after confession",
            "relieved smile after conflict",
            "angry interruption mid-sentence",
            "thoughtful pause while listening",
            "surprised reaction to news",
            "nervous laughter",
            "confident delivery",
            "emotional breakdown",
            "subtle facial reaction",
            "dramatic silence"
        ]
        
        partial_lower = partial_query.lower()
        return [s for s in suggestions if partial_lower in s.lower()][:5]
    
    def search_by_visual_query(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for video clips by visual similarity using CLIP embeddings.
        
        Args:
            query: Natural language visual description (e.g., "close-up shot with red lighting")
            top_k: Number of results to return
            
        """
        if self.visual_index is None:
            logger.warning("Visual index is empty. Run Colab embedding generation first.")
            return []
            
            
        if self.visual_index.ntotal == 0:
            logger.warning("Visual index is empty.")
            return []
        
        # Generate CLIP text embedding for query
        query_embedding = visual_embedding_service.embed_text_query(query)
        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
        
        # Search visual FAISS index
        k = min(top_k, self.visual_index.ntotal)
        scores, indices = self.visual_index.search(query_embedding, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.visual_paths):
                continue
            
            results.append({
                "video_path": self.visual_paths[idx],
                "confidence": float(score),
                "confidence_percent": round(float(score) * 100, 1),
                "match_type": "visual_clip_similarity"
            })
        
        return results
    
    def get_visual_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the visual index."""
        return {
            "visual_index_loaded": self.visual_index is not None,
            "visual_vectors": self.visual_index.ntotal if self.visual_index else 0,
            "visual_paths_count": len(self.visual_paths),
            "visual_dimension": self.visual_dimension,
            "intent_index_vectors": self.index.ntotal if self.index else 0,
            "intent_dimension": self.dimension
        }
    
    def clear_index(self):
        """Clear all indexed data."""
        self._create_new_index()
        self.save_index()


# Singleton instance
semantic_search_service = SemanticSearchService()
