import xml.etree.ElementTree as ET
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ExportService:
    def generate_fcp_xml(self, timeline_data: Dict[str, Any]) -> str:
        """
        Generates a basic Final Cut Pro XML (FCP7 style) for the given timeline.
        """
        root = ET.Element("xmeml", version="5")
        sequence = ET.SubElement(root, "sequence", id="SmartCut_Rough_Cut")
        ET.SubElement(sequence, "name").text = "SmartCut AI Selects"
        ET.SubElement(sequence, "duration").text = str(timeline_data["total_duration_frames"])
        
        rate = ET.SubElement(sequence, "rate")
        ET.SubElement(rate, "timebase").text = "24"
        ET.SubElement(rate, "ntsc").text = "FALSE"

        media = ET.SubElement(sequence, "media")
        video = ET.SubElement(media, "video")
        track = ET.SubElement(video, "track")

        for clip_data in timeline_data["tracks"]["v1"]["clips"]:
            clip = ET.SubElement(track, "clipitem", id=clip_data["id"])
            ET.SubElement(clip, "name").text = clip_data["name"]
            ET.SubElement(clip, "duration").text = str(clip_data["duration"])
            ET.SubElement(clip, "start").text = str(clip_data["start"])
            ET.SubElement(clip, "end").text = str(clip_data["start"] + clip_data["duration"])
            
            # Add AI Metadata as markers/comments
            logging_info = ET.SubElement(clip, "logginginfo")
            ET.SubElement(logging_info, "description").text = f"AI Score: {clip_data['score']} | {clip_data['reasoning']}"

        return ET.tostring(root, encoding="unicode", method="xml")

    def generate_edl(self, timeline_data: Dict[str, Any]) -> str:
        """
        Generates a CMX 3600 EDL string.
        """
        edl = f"TITLE: SmartCut_Export\nFCM: NON-DROP FRAME\n\n"
        
        for i, clip in enumerate(timeline_data["tracks"]["v1"]["clips"], 1):
            start = clip["start"]
            end = start + clip["duration"]
            # Simplified EDL entry
            edl += f"{str(i).zfill(3)}  AX       V     C        00:00:00:00 00:00:05:00 {self._frames_to_tc(start)} {self._frames_to_tc(end)}\n"
            edl += f"* FROM CLIP NAME: {clip['name']}\n"
            edl += f"* AI SCORE: {clip['score']}\n\n"

        return edl

    def _frames_to_tc(self, frames: int, fps: int = 24) -> str:
        h = frames // (fps * 3600)
        m = (frames % (fps * 3600)) // (fps * 60)
        s = (frames % (fps * 60)) // fps
        f = frames % fps
        return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"

export_service = ExportService()
