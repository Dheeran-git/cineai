
from typing import List, Dict, Any
import json
import logging
import os
from app.services.semantic_search_service import semantic_search_service
from app.services.visual_embedding_service import visual_embedding_service

logger = logging.getLogger(__name__)

class DataIngestionService:
    def ingest_colab_data(self, json_path: str):
        """
        Ingest smartcut_data.json from Colab.
        """
        if not os.path.exists(json_path):
            logger.error(f"JSON file not found: {json_path}")
            return False
            
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
                
            logger.info(f"Ingesting {len(data)} items from Colab export...")
            
            # Clear existing index? Optional.
            # semantic_search_service.clear_index()
            
            count = 0
            for item in data:
                # Map JSON fields to Index Schema
                # clip_id, start, end, embedding, description
                
                # We need numeric IDs. Let's hash the clip_id or use counter
                moment_id = hash(item["clip_id"]) % 1000000
                take_id = 999 # Dummy take ID for imported data
                
                # Convert embedding list to numpy
                import numpy as np
                embedding = np.array(item["embedding"])
                
                semantic_search_service.index_moment(
                    moment_id=moment_id,
                    take_id=take_id,
                    start_time=item["start_time"],
                    end_time=item["end_time"],
                    embedding=embedding,
                    transcript_snippet=item["transcript"],
                    emotion_label=item.get("emotion_label", "neutral"),
                    reasoning={"description": item["description"]}
                )
                count += 1
                
            semantic_search_service.save_index()
            logger.info(f"Successfully ingested {count} moments.")
            return True
            
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            return False

data_ingestion_service = DataIngestionService()
