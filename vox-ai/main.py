"""VOX-AI FastAPI WebSocket & REST Application Server.

Provides WebSocket real-time audio transport server (`/ws/call`),
REST API endpoints for order queries and appointments, and serves the frontend Phone UI.
"""

import json
import os
import sys
import uuid
from typing import Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

SYS_PATH = os.path.dirname(os.path.abspath(__file__))
if SYS_PATH not in sys.path:
    sys.path.insert(0, SYS_PATH)

from database import (  # noqa: E402
    init_db, seed_db, check_order, book_appointment, escalate_to_human, DEFAULT_DB_PATH
)
from orchestrator import VoicePipelineOrchestrator  # noqa: E402

app = FastAPI(
    title="VOX-AI Real-Time Voice Agent API",
    description="Enterprise Real-Time Voice AI Customer Support System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active call orchestrator instances dictionary
active_sessions: Dict[str, VoicePipelineOrchestrator] = {}


@app.on_event("startup")
def startup_event() -> None:
    """Initializes database schema and seeds 1000 orders on server startup."""
    init_db(DEFAULT_DB_PATH)
    seed_db(DEFAULT_DB_PATH, num_orders=1000)


# Serve Static UI Files
STATIC_DIR = os.path.join(SYS_PATH, "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_phone_ui() -> HTMLResponse:
    """Serves the VOX-AI Web Phone UI and Live Dashboard."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>VOX-AI System Running</h1><p>Static UI loading...</p>")


@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Returns system health check status across all pipeline stages."""
    return {
        "status": "online",
        "service": "VOX-AI Real-Time Engine",
        "version": "1.0.0",
        "stt_engine": "Deepgram Nova-2 Streaming",
        "llm_engine": "GPT-4o Function Calling",
        "tts_engine": "ElevenLabs Streaming (<300ms)",
        "database": "SQLite (1000 Orders Loaded)",
        "target_latency_ms": 1200.0
    }


@app.get("/api/orders/{order_id}")
async def get_order_endpoint(order_id: str) -> Dict[str, Any]:
    """REST endpoint to query customer order status."""
    result = check_order(order_id, DEFAULT_DB_PATH)
    if not result.get("found"):
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@app.post("/api/appointments")
async def create_appointment_endpoint(payload: Dict[str, Any]) -> Dict[str, Any]:
    """REST endpoint to schedule a support appointment."""
    customer_name = payload.get("customer_name", "Valued Customer")
    date = payload.get("date", "2026-03-30")
    time_slot = payload.get("time_slot", "10:00 AM")
    service_type = payload.get("service_type", "Support Consultation")
    return book_appointment(customer_name, date, time_slot, service_type, DEFAULT_DB_PATH)


@app.post("/api/escalate")
async def escalate_endpoint(payload: Dict[str, Any]) -> Dict[str, Any]:
    """REST endpoint to manually trigger call escalation."""
    reason = payload.get("reason", "Manual user escalation request")
    sentiment_score = float(payload.get("sentiment_score", -0.9))
    return escalate_to_human(reason, sentiment_score, DEFAULT_DB_PATH)


@app.websocket("/ws/call")
async def websocket_call_endpoint(websocket: WebSocket) -> None:
    """Real-Time WebSocket Transport Endpoint for Voice Conversation.

    Handles bi-directional audio transport streaming, user interrupt signals,
    transcript feeds, sentiment updates, function execution events, and latency metrics.
    """
    await websocket.accept()
    session_id = f"call_{uuid.uuid4().hex[:8]}"
    orchestrator = VoicePipelineOrchestrator(session_id=session_id, db_path=DEFAULT_DB_PATH)
    active_sessions[session_id] = orchestrator

    # Send initial connection handshake
    await websocket.send_json({
        "event": "connected",
        "session_id": session_id,
        "message": "VOX-AI Real-Time Voice Channel Established."
    })

    try:
        while True:
            # Receive text control message or raw binary audio chunk
            message = await websocket.receive()

            if "text" in message:
                try:
                    data = json.loads(message["text"])
                    action = data.get("action")

                    if action == "interrupt":
                        interrupt_res = orchestrator.trigger_interrupt()
                        await websocket.send_json({"event": "interrupted", "data": interrupt_res})

                    elif action == "speak_text":
                        # Simulate text input as spoken audio text
                        input_text = data.get("text", "")
                        fake_audio = input_text.encode("utf-8")

                        async for event in orchestrator.process_user_audio_chunk(fake_audio):
                            if "audio_bytes" in event:
                                import base64
                                event_copy = dict(event)
                                raw_bytes = event_copy.pop("audio_bytes")
                                event_copy["audio_base64"] = base64.b64encode(raw_bytes).decode("utf-8")
                                await websocket.send_json(event_copy)
                            else:
                                await websocket.send_json(event)

                except Exception as err:
                    await websocket.send_json({"event": "error", "message": str(err)})

            elif "bytes" in message:
                audio_bytes = message["bytes"]
                async for event in orchestrator.process_user_audio_chunk(audio_bytes):
                    if "audio_bytes" in event:
                        import base64
                        event_copy = dict(event)
                        raw_bytes = event_copy.pop("audio_bytes")
                        event_copy["audio_base64"] = base64.b64encode(raw_bytes).decode("utf-8")
                        await websocket.send_json(event_copy)
                    else:
                        await websocket.send_json(event)

    except WebSocketDisconnect:
        print(f"[WebSocket] Client disconnected session: {session_id}")
    finally:
        active_sessions.pop(session_id, None)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
