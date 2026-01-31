"""
Intent Embedding Service for SmartCut AI
Generates multimodal intent vectors from video moments for semantic search.
"""
import numpy as np
import logging
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)

# Lazy loading for sentence-transformers (heavy import)
_sentence_model = None

def get_sentence_model():
    global _sentence_model
    if _sentence_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Loaded sentence-transformers model: all-MiniLM-L6-v2")
        except Exception as e:
            logger.warning(f"Failed to load sentence-transformers: {e}. Using mock embeddings.")
            _sentence_model = "mock"
    return _sentence_model


class IntentEmbeddingService:
    """
    Generates multimodal intent embeddings for video moments.
    Combines: emotion, audio features, transcript context, timing cues.
    """
    
    EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 dimension
    
    # Emotion vocabulary for embedding
    EMOTION_LABELS = [
        "neutral", "happy", "sad", "angry", "fearful", "surprised", 
        "disgusted", "hesitant", "confident", "tense", "relieved",
        "awkward", "thoughtful", "anxious", "calm"
    ]
    
    # Temporal patterns
    TIMING_PATTERNS = [
        "pause_before_speech", "pause_after_speech", "quick_response",
        "overlapping_speech", "silence", "sustained_pause", "interrupted"
    ]
    
    def __init__(self):
        self.model = None
        
    def _get_model(self):
        if self.model is None:
            self.model = get_sentence_model()
        return self.model
    
    def generate_moment_embedding(
        self,
        transcript_snippet: str = "",
        emotion_data: Dict[str, Any] = None,
        audio_features: Dict[str, Any] = None,
        timing_data: Dict[str, Any] = None,
        script_context: str = ""
    ) -> np.ndarray:
        """
        Generate a unified intent embedding for a video moment.
        
        Args:
            transcript_snippet: What was said (from Whisper)
            emotion_data: Detected emotions (from CV service)
            audio_features: Audio quality/prosody data (from audio service)
            timing_data: Pause durations, silence patterns
            script_context: Surrounding script lines for narrative context
        
        Returns:
            numpy array of shape (EMBEDDING_DIM,)
        """
        model = self._get_model()
        
        # Build descriptive text combining all modalities
        intent_description = self._build_intent_description(
            transcript_snippet, emotion_data, audio_features, timing_data, script_context
        )
        
        # Generate embedding
        if model == "mock":
            # Mock embedding for testing without GPU
            np.random.seed(hash(intent_description) % 2**32)
            embedding = np.random.randn(self.EMBEDDING_DIM).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)
        else:
            embedding = model.encode(intent_description, normalize_embeddings=True)
        
        return embedding.astype(np.float32)
    
    def _build_intent_description(
        self,
        transcript: str,
        emotion_data: Dict,
        audio_features: Dict,
        timing_data: Dict,
        script_context: str
    ) -> str:
        """
        Build a natural language description of the moment's intent.
        This description is what gets embedded for semantic search.
        """
        parts = []
        
        # Transcript
        if transcript and transcript.strip():
            parts.append(f"Dialogue: {transcript.strip()}")
        else:
            parts.append("No dialogue, silent moment")
        
        # Emotion
        if emotion_data:
            emotion = emotion_data.get("primary_emotion", "neutral")
            intensity = emotion_data.get("intensity", 50)
            parts.append(f"Emotion: {emotion} (intensity {intensity}%)")
            
            # Secondary emotions
            if emotion_data.get("secondary_emotions"):
                secondary = ", ".join(emotion_data["secondary_emotions"][:2])
                parts.append(f"Also showing: {secondary}")
        
        # Audio patterns
        if audio_features:
            if audio_features.get("has_pause_before", False):
                duration = audio_features.get("pause_before_duration", 0)
                parts.append(f"Significant hesitation before speaking: {duration:.1f}s of silence")
            
            if audio_features.get("laughter_detected", False):
                parts.append("Laughter detected during this moment")
            
            if audio_features.get("has_pause_after", False):
                duration = audio_features.get("pause_after_duration", 0)
                parts.append(f"Pause after speaking: {duration:.1f}s")
            
            if audio_features.get("pitch_pattern"):
                parts.append(f"Voice pattern: {audio_features['pitch_pattern']}")
            
            if audio_features.get("speech_rate"):
                rate = audio_features["speech_rate"]
                if rate < 100:
                    parts.append("Speaking slowly, measured pace")
                elif rate > 180:
                    parts.append("Speaking quickly, urgent")
        
        # Timing patterns
        if timing_data:
            pattern = timing_data.get("pattern", "")
            if pattern:
                parts.append(f"Timing: {pattern.replace('_', ' ')}")
            
            reaction_delay = timing_data.get("reaction_delay", 0)
            if reaction_delay > 0.5:
                parts.append(f"Delayed reaction: {reaction_delay:.1f}s hesitation")
        
        # Script context
        if script_context:
            parts.append(f"Script context: {script_context[:100]}")
        
        return ". ".join(parts)
    
    def parse_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Parse an editor's search query to extract intent components.
        
        Example: "hesitant reaction before answering"
        Returns:
            {
                "emotion": "hesitant",
                "temporal": "before",
                "action": "reaction",
                "context": "answering"
            }
        """
        query_lower = query.lower()
        
        intent = {
            "raw_query": query,
            "emotions": [],
            "temporal_cues": [],
            "actions": [],
            "narrative_hints": []
        }
        
        # Detect emotions
        emotion_keywords = {
            "hesitant": ["hesitant", "hesitation", "uncertain", "unsure"],
            "tense": ["tense", "tension", "strained", "stressed"],
            "angry": ["angry", "anger", "furious", "irritated", "frustrated"],
            "sad": ["sad", "depressed", "melancholy", "tearful"],
            "happy": ["happy", "joyful", "elated", "pleased", "smiling"],
            "relieved": ["relieved", "relief", "relaxed"],
            "awkward": ["awkward", "uncomfortable", "nervous"],
            "surprised": ["surprised", "shocked", "startled"],
            "fearful": ["fearful", "afraid", "scared", "terrified"],
            "confident": ["confident", "assured", "bold"],
            "laughter": ["laughter", "laugh", "laughing", "giggle", "chuckle", "funny"]
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(kw in query_lower for kw in keywords):
                intent["emotions"].append(emotion)
        
        # Detect temporal cues
        temporal_keywords = {
            "before": ["before", "prior to", "leading up to"],
            "after": ["after", "following", "post"],
            "during": ["during", "while", "mid-"],
            "pause": ["pause", "silence", "quiet", "still"]
        }
        
        for temporal, keywords in temporal_keywords.items():
            if any(kw in query_lower for kw in keywords):
                intent["temporal_cues"].append(temporal)
        
        # Detect action types
        action_keywords = {
            "reaction": ["reaction", "reacting", "response", "responding"],
            "speaking": ["speaking", "talking", "saying", "dialogue"],
            "listening": ["listening", "hearing", "silent"],
            "interruption": ["interruption", "interrupt", "cutting off"],
            "reveal": ["reveal", "revealing", "confession", "admitting"]
        }
        
        for action, keywords in action_keywords.items():
            if any(kw in query_lower for kw in keywords):
                intent["actions"].append(action)
        
        return intent
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a search query.
        """
        model = self._get_model()
        
        # Enrich query with parsed intent
        intent = self.parse_query_intent(query)
        
        # Build enhanced query text
        enhanced_query = query
        if intent["emotions"]:
            enhanced_query += f". Emotion: {', '.join(intent['emotions'])}"
        if intent["temporal_cues"]:
            enhanced_query += f". Timing: {', '.join(intent['temporal_cues'])}"
        
        if model == "mock":
            np.random.seed(hash(enhanced_query) % 2**32)
            embedding = np.random.randn(self.EMBEDDING_DIM).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)
        else:
            embedding = model.encode(enhanced_query, normalize_embeddings=True)
        
        return embedding.astype(np.float32)


# Singleton instance
intent_embedding_service = IntentEmbeddingService()
