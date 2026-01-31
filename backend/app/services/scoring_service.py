from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ScoringService:
    def __init__(self):
        # Default Weights
        self.weights = {
            "technical": 0.3,   # Focus, exposure, blur
            "audio": 0.25,      # SNR, clipping, clarity
            "script": 0.25,     # Matching dialogue
            "performance": 0.2  # (Simulated) Emotion intensity
        }

    def compute_take_score(self, cv_data: Dict, audio_data: Dict, nlp_data: Dict) -> Dict[str, Any]:
        """
        Calculates a weighted score for the take and generates global explainability traits.
        """
        tech_score = cv_data.get("technical_score", 50)
        audio_score = audio_data.get("quality_score", 50)
        script_score = nlp_data.get("similarity", 0.5) * 100
        
        # Simulated performance score based on ad-libs and audio energy
        # Only apply score if analysis actually ran
        perf_score = 0
        if nlp_data.get("similarity", 0) > 0:
             perf_score = 80 if nlp_data.get("similarity", 0) > 0.8 else 60
        elif cv_data.get("technical_score", 0) > 0:
             # Fallback: If we have visual/file analysis but no NLP, give a baseline performance score
             perf_score = 50

        weighted_score = (
            (tech_score * self.weights["technical"]) +
            (audio_score * self.weights["audio"]) +
            (script_score * self.weights["script"]) +
            (perf_score * self.weights["performance"])
        )

        # Generate Human-Readable Reasoning
        traits = []
        if tech_score > 80: traits.append("Sharp focus and stable frame")
        if audio_score > 80: traits.append("Crystal clear audio")
        if script_score > 90: traits.append("Perfect script adherence")
        if len(nlp_data.get("ad_libs", [])) > 2: traits.append("Significant creative ad-libs detected")

        summary = f"Overall score: {weighted_score:.1f}. "
        if traits:
            summary += "Key strengths: " + ", ".join(traits) + "."
        else:
            summary += "Average performance with minor technical variances."

        return {
            "total_score": weighted_score,
            "breakdown": {
                "technical": tech_score,
                "audio": audio_score,
                "script": script_score,
                "performance": perf_score,
                # Map to UI keys
                "acting": perf_score,
                "timing": (audio_score + script_score) / 2 if script_score > 0 else 50
            },
            "summary": summary
        }

scoring_service = ScoringService()
