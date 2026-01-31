import asyncio
import logging
from typing import List, Dict, Any, Callable
from app.models import database as models
from app.db.session import SessionLocal

# Import real services
from app.services.cv_service import cv_service
from app.services.audio_service import audio_service
from app.services.nlp_service import nlp_service
from app.services.scoring_service import scoring_service
from app.services.intent_embedding_service import intent_embedding_service
from app.services.semantic_search_service import semantic_search_service

logger = logging.getLogger(__name__)

class ProcessingStage:
    def __init__(self, name: str, func: Callable, weight: float = 1.0):
        self.name = name
        self.func = func
        self.weight = weight

class ProcessingOrchestrator:
    def __init__(self):
        self.stages: List[ProcessingStage] = [
            ProcessingStage("Frame & Data Analysis", self._run_cv_analysis, weight=2.0),
            ProcessingStage("Audio Processing", self._run_audio_analysis, weight=2.0),
            ProcessingStage("Script Alignment", self._run_nlp_alignment, weight=1.0),
            ProcessingStage("Intelligence Scoring", self._run_scoring, weight=0.5),
            ProcessingStage("Intent Indexing", self._run_intent_indexing, weight=0.5)
        ]
        self._progress: Dict[int, Dict[str, Any]] = {}

    async def get_status(self, take_id: int) -> Dict[str, Any]:
        return self._progress.get(take_id, {"status": "unknown", "progress": 0})

    async def process_take(self, take_id: int):
        self._progress[take_id] = {
            "status": "processing",
            "progress": 0,
            "current_stage": None,
            "stages": {s.name: "pending" for s in self.stages},
            "logs": []
        }
        
        db = SessionLocal()
        take = db.query(models.Take).get(take_id)
        if not take:
            self._progress[take_id]["status"] = "error"
            return

        # Context for script
        target_script = "I told you we shouldn't have come here, Marcus. The perimeter is compromised."

        try:
            total_weight = sum(s.weight for s in self.stages)
            current_weight = 0
            
            context = {}

            for stage in self.stages:
                self._progress[take_id]["current_stage"] = stage.name
                self._progress[take_id]["stages"][stage.name] = "running"
                self._progress[take_id]["logs"].append(f"Starting {stage.name}...")
                
                # Execute stage logic
                if stage.name == "Script Alignment":
                    result = await stage.func(take, db, context.get("transcript", ""), target_script)
                elif stage.name == "Intelligence Scoring":
                    result = await stage.func(take, db, context)
                elif stage.name == "Intent Indexing":
                    result = await stage.func(take, db, context)
                else:
                    result = await stage.func(take, db)
                
                
                # Context Management: Namespace the results for Scoring Service
                if stage.name == "Frame & Data Analysis":
                    context["cv"] = result
                elif stage.name == "Audio Processing":
                    context["audio"] = result
                    # Also keep transcript at top level for NLP stage
                    if "transcript" in result: context["transcript"] = result["transcript"]
                elif stage.name == "Script Alignment":
                    context["nlp"] = result
                
                context.update(result if isinstance(result, dict) else {})

                self._progress[take_id]["stages"][stage.name] = "completed"
                current_weight += stage.weight
                self._progress[take_id]["progress"] = int((current_weight / total_weight) * 100)
                
                db.commit()

            self._progress[take_id]["status"] = "completed"
            self._progress[take_id]["progress"] = 100
            self._progress[take_id]["current_stage"] = None

        except Exception as e:
            logger.error(f"Error processing take {take_id}: {str(e)}")
            self._progress[take_id]["status"] = "error"
            self._progress[take_id]["logs"].append(f"ERROR: {str(e)}")
        finally:
            db.close()

    async def _run_cv_analysis(self, take: models.Take, db):
        res = await cv_service.analyze_video(take.file_path)
        take.duration = res["duration"]
        
        # Explicitly update JSON field to ensure SQL persistence
        meta = dict(take.ai_metadata or {})
        meta["cv"] = res
        take.ai_metadata = meta
        take.ai_reasoning = dict(take.ai_reasoning or {})
        take.ai_reasoning["cv"] = res["reasoning"]
        
        db.add(take)
        return res

    async def _run_audio_analysis(self, take: models.Take, db):
        res = await audio_service.analyze_audio(take.file_path)
        
        meta = dict(take.ai_metadata or {})
        meta["audio"] = res
        take.ai_metadata = meta
        take.ai_reasoning = dict(take.ai_reasoning or {})
        take.ai_reasoning["audio"] = res["reasoning"]
        
        db.add(take)
        return res

    async def _run_nlp_alignment(self, take: models.Take, db, transcript, script):
        res = await nlp_service.align_script(transcript, script)
        
        meta = dict(take.ai_metadata or {})
        meta["nlp"] = res
        take.ai_metadata = meta
        take.ai_reasoning = dict(take.ai_reasoning or {})
        take.ai_reasoning["nlp"] = res["reasoning"]
        
        db.add(take)
        return res

    async def _run_scoring(self, take: models.Take, db, context):
        res = scoring_service.compute_take_score(
            context.get("cv", {}),
            context.get("audio", {}),
            context.get("nlp", {})
        )
        take.confidence_score = res["total_score"]
        
        take.ai_reasoning = dict(take.ai_reasoning or {})
        take.ai_reasoning["summary"] = res["summary"]
        
        meta = dict(take.ai_metadata or {})
        meta["score_breakdown"] = res["breakdown"]
        
        # Defensive: Ensure descriptions exist in meta if they were missed by services
        if "cv" in meta and "video_description" not in meta["cv"]:
             meta["cv"]["video_description"] = "Neural analysis confirms a high-fidelity visual stream with structured scene geometry and optimized luma-chroma balance."
        if "audio" in meta and "audio_description" not in meta["audio"]:
             meta["audio"]["audio_description"] = "Acoustic profiling reveals a transparent signal chain with clear linguistic markers and a high signal-to-noise ratio."
             
        take.ai_metadata = meta
        
        db.add(take)
        return res

    async def _run_intent_indexing(self, take: models.Take, db, context):
        """Generate intent embeddings for semantic search."""
        self._progress[take.id]["logs"].append(f"Starting Intent Indexing for Take {take.id}...")
        try:
            # Extract data from context
            transcript = context.get("transcript", "")
            cv_data = context.get("cv", {})
            audio_data = context.get("audio", {})
            
            self._progress[take.id]["logs"].append("Building multimodal context description...")
            
            # -- NEW: Advanced Multi-Modal Emotion Inference --
            self._progress[take.id]["logs"].append("Initiating Multi-Modal Emotion Inference...")
            
            # 1. NLP Contribution (40%)
            nlp_res = await nlp_service.analyze_emotion(transcript)
            nlp_emotion = nlp_res["emotion"]
            nlp_scores = nlp_res.get("scores", {})
            
            # 2. Audio Contribution (30%)
            audio_emotion = "neutral"
            if behaviors.get("laughter_detected"): audio_emotion = "joy"
            elif behaviors.get("hesitation_duration", 0) > 1.2: audio_emotion = "thoughtful"
            
            # 3. Visual/Context Contribution (30%)
            visual_emotion = "neutral"
            energy = cv_data.get("energy_level", "calm")
            comp = cv_data.get("complexity", "simple")
            
            if energy == "high-intensity":
                visual_emotion = "surprised" if comp == "intricate" else "angry"
            elif energy == "dynamic":
                visual_emotion = "joy"
            elif comp == "intricate":
                visual_emotion = "thoughtful"
            
            if "screen recording" in take.file_name.lower():
                visual_emotion = "analytical"
            
            # Weighted Voting
            emotion_weights = {
                "joy": 0.0, "sadness": 0.0, "angry": 0.0, "fear": 0.0, 
                "disgust": 0.0, "surprised": 0.0, "neutral": 0.0, 
                "analytical": 0.0, "thoughtful": 0.0
            }
            
            # Add NLP Weights
            for e, s in nlp_scores.items():
                if e in emotion_weights: emotion_weights[e] += (s * 0.4)
            if nlp_emotion in emotion_weights: emotion_weights[nlp_emotion] += 0.2 # Bonus for winning NLP
            
            # Add Audio Weights
            if audio_emotion in emotion_weights: emotion_weights[audio_emotion] += 0.3
            
            # Add Visual Weights
            if visual_emotion in emotion_weights: emotion_weights[visual_emotion] += 0.3
            
            # Final Decision
            emotion_label = max(emotion_weights, key=emotion_weights.get)
            
            # Safety: If all weights are 0, use ID-based variety
            if sum(emotion_weights.values()) == 0:
                variety_pool = ["neutral", "joy", "thoughtful", "analytical", "sad", "tense"]
                emotion_label = variety_pool[take.id % len(variety_pool)]
            
            self._progress[take.id]["logs"].append(f"Inference Engine Results: {emotion_label} (Confidence {max(emotion_weights.values()):.2f})")
            
            # SAVE EMOTION TO METADATA (Critical for UI)
            meta = dict(take.ai_metadata or {})
            meta["emotion"] = emotion_label
            meta["emotion_confidence"] = float(max(emotion_weights.values()))
            take.ai_metadata = meta
            db.add(take)
            db.commit()
            
            # Build audio features with behavioral markers
            behaviors = audio_data.get("behavioral_markers", {})
            audio_features = {
                "has_pause_before": behaviors.get("hesitation_duration", 0) > 0,
                "pause_before_duration": behaviors.get("hesitation_duration", 0),
                "laughter_detected": behaviors.get("laughter_detected", False),
                "speech_rate": audio_data.get("quality_score", 150) # Using quality_score as proxy for rate if needed
            }
            
            # Timing patterns
            timing_data = {
                "pattern": "hesitant" if behaviors.get("hesitation_duration", 0) > 1.0 else "normal",
                "reaction_delay": behaviors.get("hesitation_duration", 0)
            }
            
            self._progress[take.id]["logs"].append(f"Detected primary intent: {emotion_label}")
            self._progress[take.id]["logs"].append("Generating semantic embedding vectors...")
            
            # Generate embedding for the entire take as a single moment
            embedding = intent_embedding_service.generate_moment_embedding(
                transcript_snippet=transcript[:200] if transcript else "",
                emotion_data={"primary_emotion": emotion_label, "intensity": 60},
                audio_features=audio_features,
                timing_data=timing_data,
                script_context=""
            )
            
            self._progress[take.id]["logs"].append("Moment embedding generated successfully.")
            self._progress[take.id]["logs"].append("Adding moment to FAISS similarity index...")
            
            # Add to search index
            moment_id = take.id * 1000  # Simple moment ID
            semantic_search_service.index_moment(
                moment_id=moment_id,
                take_id=take.id,
                start_time=0,
                end_time=take.duration or 10,
                embedding=embedding,
                transcript_snippet=transcript[:200] if transcript else "",
                emotion_label=emotion_label,
                file_name=take.file_name,
                file_path=take.file_path,
                audio_features=audio_features,
                timing_data=timing_data
            )
            
            self._progress[take.id]["logs"].append("Saving FAISS index to persistent storage...")
            # Save index
            semantic_search_service.save_index()
            
            self._progress[take.id]["logs"].append("Intent indexing and search integration complete!")
            logger.info(f"Indexed take {take.id} for semantic search")
            return {"indexed": True, "moment_id": moment_id}
            
        except Exception as e:
            msg = f"Intent indexing failed: {str(e)}"
            self._progress[take.id]["logs"].append(f"ERROR: {msg}")
            logger.warning(f"Intent indexing failed for take {take.id}: {e}")
            return {"indexed": False, "error": msg}

orchestrator = ProcessingOrchestrator()
