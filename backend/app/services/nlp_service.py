from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Optional ML imports
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available. Using mock NLP analysis.")

class NLPService:
    def __init__(self):
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception as e:
                logger.warning(f"Failed to load spaCy model: {e}. Downloading...")
                try:
                    import os
                    os.system("python -m spacy download en_core_web_sm")
                    self.nlp = spacy.load("en_core_web_sm")
                except:
                    logger.error("spaCy fallback failed.")
                    self.nlp = None

    async def align_script(self, transcript: str, script_text: str) -> Dict[str, Any]:
        """
        Compares transcript against target script using semantic similarity.
        """
        if not SPACY_AVAILABLE or not self.nlp:
            # Mock behavior since we can't do semantic similarity without spacy
            return {
                "similarity": 0.88,
                "ad_libs": ["simulated", "ad-lib"],
                "reasoning": "Mock NLP analysis: 88% script match (spaCy not installed)",
                "confidence": 0.7
            }
            
        if not transcript or not script_text:
            return {
                "similarity": 0.0,
                "ad_libs": [],
                "reasoning": "Incomplete data for alignment.",
                "confidence": 0.0
            }

        doc_t = self.nlp(transcript.lower())
        doc_s = self.nlp(script_text.lower())

        similarity = doc_t.similarity(doc_s)

        # Simple ad-lib detection (words in transcript NOT in script)
        # In a real app, this would be more sophisticated (fuzzy matching)
        words_t = set([token.text for token in doc_t if not token.is_punct])
        words_s = set([token.text for token in doc_s if not token.is_punct])
        
        ad_libs = list(words_t - words_s)
        
        reasoning = f"Script alignment shows {similarity*100:.1f}% accuracy."
        if len(ad_libs) > 0:
            reasoning += f" Detected potential ad-libs: {', '.join(ad_libs[:3])}..."

        return {
            "similarity": similarity,
            "ad_libs": ad_libs,
            "reasoning": reasoning,
            "confidence": 0.85
        }

nlp_service = NLPService()

