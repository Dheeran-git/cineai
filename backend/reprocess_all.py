import asyncio
import logging
import os
import imageio_ffmpeg
from app.db.session import SessionLocal
from app.models import database as models
from app.services.orchestrator import orchestrator

# Ensure ffmpeg for librosa
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_exe)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='reprocess.log',
    filemode='w'
)
logger = logging.getLogger(__name__)

async def main():
    db = SessionLocal()
    try:
        takes = db.query(models.Take).all()
        logger.info(f"Found {len(takes)} takes to re-process.")
        
        for take in takes:
            logger.info(f"--- STARTING TAKE {take.id}: {take.file_name} ---")
            # Reset metadata to ensure fresh start
            take.ai_metadata = {}
            take.ai_reasoning = {}
            db.add(take)
            db.commit()
            
            await orchestrator.process_take(take.id)
            logger.info(f"--- COMPLETED TAKE {take.id} ---")
            
    except Exception as e:
        logger.error(f"Reprocess failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
