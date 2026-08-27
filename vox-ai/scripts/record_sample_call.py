"""VOX-AI Sample Call Generator & Recording Script.

Simulates a multi-turn voice customer support conversation, executes real tool calling,
performs sentiment detection & escalation, measures latency metrics, and saves `sample_call.wav`
and `sample_call_transcript.json` artifacts.
"""

import asyncio
import json
import os
import sys
import wave

SYS_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SYS_PATH not in sys.path:
    sys.path.insert(0, SYS_PATH)

from database import init_db, seed_db, DEFAULT_DB_PATH  # noqa: E402
from orchestrator import VoicePipelineOrchestrator  # noqa: E402


async def record_sample_call() -> None:
    """Executes sample call simulation and generates WAV audio & transcript artifacts."""
    print("Initializing database for sample call simulation...")
    init_db(DEFAULT_DB_PATH)
    seed_db(DEFAULT_DB_PATH, num_orders=1000)

    session_id = "demo_call_record_001"
    orchestrator = VoicePipelineOrchestrator(session_id=session_id, db_path=DEFAULT_DB_PATH)

    turns_to_simulate = [
        "Hello, I would like to check the status of my order ORD-1001 please.",
        "That's great. Can you also book a support appointment for Alex on 2026-03-30 at 10:00 AM?",
        "Wait, I am extremely frustrated! The delivery date is unacceptable! "
        "I want to speak to a human manager right now!"
    ]

    transcript_log = []
    collected_audio_frames = bytearray()

    print("\n=======================================================")
    print("           VOX-AI DEMO CALL SIMULATION RECORDING       ")
    print("=======================================================\n")

    for turn_idx, user_speech in enumerate(turns_to_simulate, 1):
        print(f"--- Turn {turn_idx} ---")
        print(f"[User Spoken]: {user_speech}")

        turn_record = {
            "turn": turn_idx,
            "user_speech": user_speech,
            "events": []
        }

        fake_audio_chunk = user_speech.encode("utf-8")

        async for event in orchestrator.process_user_audio_chunk(fake_audio_chunk):
            event_type = event.get("event")

            if event_type == "stt_complete":
                print(f"[STT Nova-2]: Transcript='{event['transcript']}' ({event['stt_latency_ms']} ms)")
                turn_record["stt"] = event

            elif event_type == "sentiment_analysis":
                s = event["sentiment"]
                print(f"[Sentiment]: Score={s['score']}, Label={s['label']}, Escalated={event['is_escalated']}")
                turn_record["sentiment"] = event

            elif event_type == "llm_complete":
                print(f"[GPT-4o AI]: '{event['response_text']}' ({event['llm_latency_ms']} ms)")
                if event.get("function_calls"):
                    print(f"[Function Calls]: {event['function_calls']}")
                turn_record["llm"] = event

            elif event_type == "audio_chunk":
                chunk_bytes = event.get("audio_bytes", b"")
                collected_audio_frames.extend(chunk_bytes)
                turn_record["events"].append({
                    "chunk_index": event["chunk_index"],
                    "tts_latency_ms": event["tts_latency_ms"],
                    "audio_byte_len": len(chunk_bytes)
                })

            elif event_type == "turn_complete":
                breakdown = event["latency_breakdown"]
                tot_ms = breakdown['total_end_to_end_ms']
                within = breakdown['within_target']
                print(f"[Latency Benchmark]: End-to-End = {tot_ms} ms (Target <1200ms: {within})\n")
                turn_record["latency_breakdown"] = breakdown

        transcript_log.append(turn_record)

    # Save transcript log JSON
    transcript_path = os.path.join(SYS_PATH, "sample_call_transcript.json")
    with open(transcript_path, "w", encoding="utf-8") as f:
        json.dump(transcript_log, f, indent=2)
    print(f"Saved transcript log to: {transcript_path}")

    # Save audio WAV file artifact
    wav_path = os.path.join(SYS_PATH, "sample_call.wav")
    with wave.open(wav_path, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit PCM
        wav_file.setframerate(16000)
        wav_file.writeframes(bytes(collected_audio_frames))

    print(f"Saved audio recording artifact to: {wav_path} (Size: {len(collected_audio_frames)} bytes)")
    print("\nDemo call recording process successfully completed.\n")


def main() -> None:
    """Main execution point."""
    asyncio.run(record_sample_call())


if __name__ == "__main__":
    main()
