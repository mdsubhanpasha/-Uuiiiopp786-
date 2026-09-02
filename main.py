"""
AURON-CORP-137Q Main FastAPI Server
Orchestrates 137 AI Agents across 7 departments, Quantum QAOA Optimization,
and VOX-AI V4 Voice Control via WebSockets.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from agents.registry import agent_registry, DEPARTMENTS
from brain.quantum_brain import quantum_brain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auron_main")

app = FastAPI(
    title="AURON-CORP-137Q | Company OS",
    description="Live, interactive enterprise Operating System running 137 AI Agents across 7 departments, orchestrated by Qiskit QAOA Quantum Core and VOX-AI V4 Voice Control.",
    version="4.0.0-137Q"
)

# Enable CORS for frontend development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file path for React frontend build
frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")

# REST API Endpoints

@app.get("/api/health")
def health_check():
    return {
        "status": "ONLINE",
        "system": "AURON-CORP-137Q",
        "architect": "Mohammad Subhan Pasha",
        "quantum_core": "Qiskit QAOA Active",
        "voice_engine": "VOX-AI V4 Ready",
        "total_agents": agent_registry.count()
    }

@app.get("/api/status")
def get_company_status_api():
    agents_data = agent_registry.list_all()
    dept_counts = {}
    for dept in DEPARTMENTS:
        dept_counts[dept] = len([a for a in agents_data if a["department"] == dept])

    return {
        "company": "AURON CORP",
        "system": "AURON-4000 137Q",
        "architect": "Mohammad Subhan Pasha",
        "total_agents": agent_registry.count(),
        "departments": DEPARTMENTS,
        "department_counts": dept_counts,
        "quantum_status": "QAOA Quantum Core operational",
        "agents": agents_data
    }

@app.get("/")
async def root_endpoint(request: Request, format: Optional[str] = None):
    """
    Returns company overview + 137 agent list if JSON requested,
    otherwise serves the React Flow frontend application.
    """
    accept_header = request.headers.get("accept", "")
    if "application/json" in accept_header or format == "json":
        return get_company_status_api()

    # If frontend dist exists, serve index.html for browser
    if os.path.exists(os.path.join(frontend_dist, "index.html")):
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    return get_company_status_api()

@app.get("/agents/{agent_id}/run")
def run_specific_agent(
    agent_id: str,
    task: str = Query("Analyze department priorities and generate operational report.", description="Task prompt for the agent")
):
    agent = agent_registry.get_by_id(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found in registry of 137 agents.")

    execution_result = agent.run(task=task)
    return execution_result

@app.get("/quantum/optimize")
def run_quantum_optimization(qubits: int = Query(6, ge=2, le=10)):
    optimization_result = quantum_brain.run_qaoa_optimization(num_qubits=qubits)
    return {
        "system": "AURON-4000 Quantum Core",
        "quantum_brain_result": optimization_result
    }

@app.get("/company/knowledge")
def query_company_knowledge(query: str = Query("What is AURON-CORP-137Q?", description="Knowledge query")):
    res = quantum_brain.query_knowledge(query)
    return res

# VOX-AI V4 WebSocket Voice Control
@app.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("VOX-AI V4 Voice WebSocket client connected.")

    try:
        await websocket.send_json({
            "type": "connection_established",
            "message": "VOX-AI V4 Streaming Voice Core Online. Listening for company directives...",
            "system": "AURON-CORP-137Q"
        })

        while True:
            data_str = await websocket.receive_text()
            try:
                payload = json.loads(data_str)
                user_transcript = payload.get("transcript", data_str)
            except Exception:
                user_transcript = data_str

            logger.info(f"VOX-AI Voice Directive received: {user_transcript}")

            lowered = user_transcript.lower()
            target_agent = None

            if "sales" in lowered or "lead" in lowered or "prospect" in lowered:
                target_agent = agent_registry.get_by_id("icp_definer") or agent_registry.get_by_id("lead_sourcer")
            elif "deal" in lowered or "meeting" in lowered or "proposal" in lowered:
                target_agent = agent_registry.get_by_id("reply_triage") or agent_registry.get_by_id("meeting_booker")
            elif "market" in lowered or "ad" in lowered or "content" in lowered or "script" in lowered:
                target_agent = agent_registry.get_by_id("performance_analyst") or agent_registry.get_by_id("scriptwriter")
            elif "quantum" in lowered or "optimize" in lowered:
                q_res = quantum_brain.run_qaoa_optimization()
                response_text = f"Quantum QAOA optimization executed successfully. Optimal bitstring: {q_res.get('optimal_bitstring')}."
                await websocket.send_json({
                    "type": "voice_response",
                    "transcript": user_transcript,
                    "agent_executed": "QUANTUM_BRAIN",
                    "spoken_response": response_text,
                    "quantum_payload": q_res
                })
                continue
            else:
                target_agent = agent_registry.get_by_id("company_researcher") or agent_registry.list_all()[0]

            if target_agent:
                agent_res = target_agent.run(task=user_transcript)
                spoken_response = (
                    f"Directive routed to {agent_res['agent_name']} in {agent_res['department']}. "
                    f"{agent_res['output']}"
                )
                await websocket.send_json({
                    "type": "voice_response",
                    "transcript": user_transcript,
                    "agent_executed": agent_res['agent_name'],
                    "department": agent_res['department'],
                    "spoken_response": spoken_response,
                    "agent_payload": agent_res
                })
            else:
                await websocket.send_json({
                    "type": "voice_response",
                    "transcript": user_transcript,
                    "agent_executed": "SYSTEM",
                    "spoken_response": f"Processed directive across AURON-137Q network: {user_transcript}"
                })

    except WebSocketDisconnect:
        logger.info("VOX-AI V4 Voice WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

# Mount static assets if dist exists
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
