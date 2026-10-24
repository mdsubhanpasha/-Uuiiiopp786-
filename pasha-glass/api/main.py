"""
FastAPI Backend Server for PASHA-GLASS Companion App.
Exposes endpoints for Opt-In Gallery Management, BLE Stream Frame Ingestion, and HUD State.
"""

import base64
import os
import sys
import cv2
import numpy as np
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Ensure pasha-glass directory is in import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.gallery import OptInGallery, MAX_OPT_IN_GALLERY_SIZE
from core.face_engine import FaceEngine
from core.context_sync import ContextSync
from core.ble_stream import MetaGlassesBLEStream


app = FastAPI(
    title="PASHA-GLASS Companion API",
    description="Privacy-First Context Assistant backend for Ray-Ban Meta Glasses",
    version="2.0.0"
)

# Mount static frontend
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")

# Global core singletons
db_file = os.environ.get("PASHA_GLASS_DB", "pasha_glass_app.db")
gallery = OptInGallery(db_path=db_file)
face_engine = FaceEngine(gallery)
context_sync = ContextSync()
ble_stream = MetaGlassesBLEStream()

# Seed initial demo contacts into app db if empty
if gallery.count_contacts() == 0:
    dummy_img = np.zeros((10, 10, 3), dtype=np.uint8)
    seeds = [
        ("c_daniel", "Daniel", "Client from Acme, likes AI infra", "daniel_seed"),
        ("c_sarah", "Sarah", "CTO Partner, prefers LangGraph", "sarah_seed"),
        ("c_alex", "Alex", "Lead Designer, lead on Ray-Ban HUD UX", "alex_seed"),
        ("c_elena", "Elena", "Investor at VC, Edge AI & Privacy", "elena_seed"),
        ("c_marcus", "Marcus", "Security Lead, compliance auditor", "marcus_seed"),
    ]
    for cid, name, ctx, skey in seeds:
        vec = face_engine.extract_embedding_synthetic(dummy_img, seed_id=skey)
        gallery.add_contact(cid, name, ctx, vec)


# Pydantic Schemas
class ContactCreateRequest(BaseModel):
    contact_id: str = Field(..., json_schema_extra={"example": "daniel_client_01"})
    name: str = Field(..., json_schema_extra={"example": "Daniel"})
    context: str = Field(..., json_schema_extra={"example": "Client from Acme, likes AI infra"})
    photo_b64: Optional[str] = Field(None, description="Optional base64 image")
    seed_key: Optional[str] = Field(None, description="Seed key for synthetic embedding generation")


class FrameProcessRequest(BaseModel):
    frame_b64: Optional[str] = None
    seed_id: Optional[str] = None


@app.get("/")
def read_root():
    return {
        "service": "PASHA-GLASS Privacy-First Companion API",
        "status": "online",
        "privacy_policy": "NO public facial recognition. NO social media scraping. Local opt-in only.",
        "gallery_capacity": f"{gallery.count_contacts()}/{MAX_OPT_IN_GALLERY_SIZE}"
    }


@app.get("/api/v1/gallery", response_model=List[Dict[str, Any]])
def list_optin_contacts():
    """List all opt-in contacts in the encrypted local gallery."""
    contacts = gallery.list_contacts()
    cleaned = []
    for c in contacts:
        item = c.copy()
        item.pop("embedding", None)
        cleaned.append(item)
    return cleaned


@app.post("/api/v1/gallery", status_code=201)
def add_optin_contact(req: ContactCreateRequest):
    """Add a new contact with explicit opt-in consent to the local encrypted gallery (Max 50)."""
    try:
        if req.seed_key:
            vec = face_engine.extract_embedding_synthetic(np.zeros((10, 10, 3)), seed_id=req.seed_key)
        elif req.photo_b64:
            img_bytes = base64.b64decode(req.photo_b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            vec = face_engine.extract_embedding_synthetic(img)
        else:
            vec = face_engine.extract_embedding_synthetic(np.zeros((10, 10, 3)), seed_id=req.name)

        contact = gallery.add_contact(
            contact_id=req.contact_id,
            name=req.name,
            context=req.context,
            embedding=vec,
            photo_b64=req.photo_b64
        )
        return {"status": "success", "message": f"Contact '{req.name}' added with explicit consent.", "contact": contact}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add contact: {str(e)}")


@app.get("/api/v1/gallery/{contact_id}")
def get_contact(contact_id: str):
    """Fetch opt-in contact details."""
    contact = gallery.get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found in local gallery")
    contact.pop("embedding", None)
    return contact


@app.delete("/api/v1/gallery/{contact_id}")
def delete_contact(contact_id: str):
    """Revoke opt-in consent and delete contact completely from local database."""
    deleted = gallery.delete_contact(contact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"status": "success", "message": f"Contact '{contact_id}' and associated biometric vectors deleted."}


@app.post("/api/v1/gallery/purge")
def purge_gallery():
    """Purge all contacts and transient frame logs."""
    gallery.purge_all()
    return {"status": "success", "message": "All local biometric embeddings and contacts purged."}


@app.post("/api/v1/process-frame")
def process_camera_frame(req: FrameProcessRequest = Body(...)):
    """
    Process incoming Meta Glasses frame:
    - If face matches opt-in gallery (>0.85 similarity), return HUD context card.
    - If face is unknown/unverified, apply mandatory Gaussian blur and return 'Unknown person - no data'.
    """
    if req.frame_b64:
        img_bytes = base64.b64decode(req.frame_b64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    else:
        frame, _ = ble_stream.generate_synthetic_frame("Ray-Ban Meta Stream", add_face=True)

    bboxes = face_engine.detect_faces(frame)

    known_map = {}
    if req.seed_id and bboxes:
        known_map[bboxes[0]] = req.seed_id

    result = face_engine.process_frame(frame, known_seeds_map=known_map)

    augmented_cards = []
    for card in result["hud_cards"]:
        if card["is_known"]:
            aug_context = context_sync.resolve_augmented_context(card["name"], card["context"])
            card["augmented_context"] = aug_context
            card["hud_text"] = f"{card['name']} - {aug_context}"
        augmented_cards.append(card)

    result["hud_cards"] = augmented_cards

    _, buffer = cv2.imencode('.jpg', result["processed_frame"])
    result["processed_frame_b64"] = base64.b64encode(buffer).decode()
    result.pop("processed_frame")

    return result


@app.post("/api/v1/cleanup-cache")
def cleanup_transient_cache():
    """Trigger 24-hour auto-deletion of transient frame logs."""
    deleted_count = gallery.cleanup_transient_cache(max_age_seconds=86400.0)
    return {"status": "success", "deleted_logs_count": deleted_count}
