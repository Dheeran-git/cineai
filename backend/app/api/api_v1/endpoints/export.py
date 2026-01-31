from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.services.timeline_service import timeline_service
from app.services.export_service import export_service
from app.models import database as models

router = APIRouter()

@router.get("/{format}")
def export_timeline(format: str, db: Session = Depends(deps.get_db)):
    project = db.query(models.Project).first()
    if not project:
        raise HTTPException(status_code=404, detail="No project found")
    
    timeline_data = timeline_service.assemble_ai_rough_cut(project.id, db)
    
    if format.lower() == "xml":
        content = export_service.generate_fcp_xml(timeline_data)
        filename = "SmartCut_Export.xml"
        media_type = "application/xml"
    elif format.lower() == "edl":
        content = export_service.generate_edl(timeline_data)
        filename = "SmartCut_Export.edl"
        media_type = "text/plain"
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Use 'xml' or 'edl'.")

    return {
        "filename": filename,
        "content": content,
        "media_type": media_type
    }
